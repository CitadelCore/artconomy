import logging
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Q, IntegerField, Case, When, F
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.datetime_safe import date
from moneyed import Money

from apps.lib.models import Subscription, COMMISSIONS_OPEN, Event, DISPUTE, SALE_UPDATE, ORDER_UPDATE
from apps.lib.utils import notify, recall_notification
from apps.profiles.models import User


logger = logging.getLogger(__name__)


def escrow_balance(user):
    # TODO: This accounting requires too many special cases. We need a better way to keep track of all of this.
    from apps.sales.models import PaymentRecord
    try:
        debit = Decimal(
            str(user.credits.filter(
                status=PaymentRecord.SUCCESS,
                source=PaymentRecord.ESCROW
            ).exclude(type=PaymentRecord.REFUND).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        debit = Decimal('0.00')
    try:
        debit += Decimal(
            str(user.escrow_holdings.filter(
                status=PaymentRecord.SUCCESS,
                type=PaymentRecord.REFUND,
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        pass
    try:
        debit += Decimal(
            str(user.debits.filter(
                source=PaymentRecord.ESCROW, status=PaymentRecord.SUCCESS,
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        pass
    try:
        credit = Decimal(
            str(user.escrow_holdings.filter(
                status=PaymentRecord.SUCCESS).exclude(
                type__in=[
                    PaymentRecord.DISBURSEMENT_SENT,
                    PaymentRecord.DISBURSEMENT_RETURNED,
                    PaymentRecord.REFUND,
                ]
            ).aggregate(Sum('amount'))['amount__sum']))
    except InvalidOperation:
        credit = Decimal('0.00')

    return credit - debit


def available_balance(user):
    from apps.sales.models import PaymentRecord
    try:
        debit = Decimal(
            str(user.debits.filter(
                status=PaymentRecord.SUCCESS,
                source=PaymentRecord.ACCOUNT,
                # In the case of disbursement failed, we use success by default since it's a record from Dwolla, not
                # us.
                type__in=[PaymentRecord.DISBURSEMENT_SENT, PaymentRecord.TRANSFER, PaymentRecord.DISBURSEMENT_RETURNED],
            ).exclude(
                # Exclude service fees that haven't finalized.
                type__in=[PaymentRecord.TRANSFER],
                finalized=False
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        debit = Decimal('0.00')
    try:
        credit = Decimal(
            str(
                user.credits.filter(
                    status=PaymentRecord.SUCCESS,
                    finalized=True
                ).exclude(type=PaymentRecord.REFUND).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        credit = Decimal('0.00')

    return credit - debit


def pending_balance(user):
    from apps.sales.models import PaymentRecord
    try:
        credit = Decimal(
            str(
                user.credits.filter(
                    status=PaymentRecord.SUCCESS,
                    finalized=False
                ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        credit = Decimal('0.00')
    try:
        debit = Decimal(
            str(
                user.debits.filter(
                    status=PaymentRecord.SUCCESS,
                    type=PaymentRecord.TRANSFER,
                    finalized=False
                ).aggregate(Sum('amount'))['amount__sum']
            )
        )
    except InvalidOperation:
        debit = Decimal('0.00')
    return credit - debit


def translate_authnet_error(err):
    response = str(err)
    if hasattr(err, 'full_response'):
        # API is inconsistent in how it returns error info.
        if 'response_reason_text' in err.full_response:
            response = err.full_response['response_reason_text']
        if 'response_text' in err.full_response:
            response = err.full_response['response_text']
        if 'response_reason_code' in err.full_response:
            response = RESPONSE_TRANSLATORS.get(err.full_response['response_reason_code'], response)
        if 'response_code' in err.full_response:
            response = RESPONSE_TRANSLATORS.get(err.full_response['response_code'], response)
    return response


def product_ordering(qs, query=''):
    return qs.annotate(
        matches=Case(
            When(name__iexact=query, then=0),
            default=1,
            output_field=IntegerField()
        ),
        tag_matches=Case(
            When(tags__name__iexact=query, then=0),
            default=1,
            output_field=IntegerField()
        )
        # How can we make it distinct on id while making matches and tag_matches priority ordering?
    ).order_by('id', 'matches', 'tag_matches').distinct('id')


def available_products(requester, query='', ordering=True):
    from apps.sales.models import Product
    if query:
        q = Q(name__istartswith=query) | Q(tags__name=query.lower())
        qs = Product.objects.filter(available=True).filter(q)
    else:
        qs = Product.objects.filter(available=True)
    if requester.is_authenticated:
        if not requester.is_staff:
            qs = qs.exclude(user__blocking=requester)
        qs = qs.exclude(user__blocked_by=requester)
    if ordering:
        return product_ordering(qs, query)
    return qs


RESPONSE_TRANSLATORS = {
    '54': 'This transaction cannot be refunded. It may not yet have posted. '
          'Please try again tomorrow, and contact support if it still fails.',
    'E00027': "The zip or address we have on file for your card is either incorrect or has changed. Please remove the "
          "card and add it again with updated information.",
    'E00040': "Something is wrong in our records with the card you've added. Please remove the card and re-add it."
}


def service_price(user, service):
    price = Money(getattr(settings, service.upper() + '_PRICE'), 'USD')
    if service == 'landscape':
        if user.portrait_paid_through and user.portrait_paid_through > date.today():
            price -= Money(settings.PORTRAIT_PRICE, 'USD')
    return price


def set_service(user, service, target_date=None):
    if service == 'portrait':
        user.portrait_enabled = True
        user.landscape_enabled = False
    else:
        user.landscape_enabled = True
        user.portrait_enabled = False
    if target_date:
        setattr(user, service + '_paid_through', target_date)
        # Landscape includes portrait, so this is always set regardless.
        user.portrait_paid_through = target_date
        for watched in user.watching.all():
            content_type = ContentType.objects.get_for_model(watched)
            sub, _ = Subscription.objects.get_or_create(
                subscriber=user,
                content_type=content_type,
                object_id=watched.id,
                type=COMMISSIONS_OPEN
            )
            sub.until = target_date
            sub.telegram = True
            sub.email = True
            sub.save()
    user.save()


def check_charge_required(user, service):
    if service == 'portrait':
        if user.landscape_paid_through:
            if user.landscape_paid_through >= date.today():
                return False, user.landscape_paid_through
        if user.portrait_paid_through:
            if user.portrait_paid_through >= date.today():
                return False, user.portrait_paid_through
    else:
        if user.landscape_paid_through:
            if user.landscape_paid_through >= date.today():
                return False, user.landscape_paid_through
    return True, None


def available_products_by_load(seller, load=None):
    from apps.sales.models import Product
    if load is None:
        load = seller.load
    return Product.objects.filter(user_id=seller.id, active=True, hidden=False).exclude(
        task_weight__gt=seller.max_load - load
    ).exclude(Q(parallel__gte=F('max_parallel')) & ~Q(max_parallel=0))


def available_products_from_user(seller):
    from apps.sales.models import Product
    if seller.commissions_closed or seller.commissions_disabled:
        return Product.objects.none()
    return available_products_by_load(seller)


# Primitive recursion check lock.
UPDATING = {}


def update_availability(seller, load, current_closed_status):
    from apps.sales.models import Order
    global UPDATING
    if seller in UPDATING:
        return
    UPDATING[seller] = True
    try:
        products = available_products_by_load(seller, load)
        if seller.commissions_closed:
            seller.commissions_disabled = True
        elif not products.exists():
            seller.commissions_disabled = True
        elif load >= seller.max_load:
            seller.commissions_disabled = True
        elif not seller.sales.filter(status=Order.NEW).exists():
            seller.commissions_disabled = False
        seller.load = load
        if products and not seller.commissions_disabled:
            seller.has_products = True
        seller.save()
        products.update(available=True)
        # Sanity setting.
        seller.products.filter(hidden=True).update(available=False)
        if current_closed_status and not seller.commissions_disabled:
            previous = Event.objects.filter(
                type=COMMISSIONS_OPEN, content_type=ContentType.objects.get_for_model(User), object_id=seller.id,
                date__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
            notify(
                COMMISSIONS_OPEN, seller, unique=True, mark_unread=not previous.exists(),
                silent_broadcast=previous.exists()
            )
        if seller.commissions_disabled or seller.commissions_closed:
            seller.products.all().update(available=False)
            recall_notification(COMMISSIONS_OPEN, seller)
    finally:
        del UPDATING[seller]


def finalize_order(order, user=None):
    from apps.sales.models import PaymentRecord
    from apps.sales.tasks import withdraw_all
    with atomic():
        if order.status == order.DISPUTED and user == order.buyer:
            # User is rescinding dispute.
            recall_notification(DISPUTE, order)
            # We'll pretend this never happened.
            order.disputed_on = None
        order.status = order.COMPLETED
        order.save()
        notify(SALE_UPDATE, order, unique=True, mark_unread=True)
        new_tx = PaymentRecord(
            payer=None,
            amount=order.price + order.adjustment,
            payee=order.seller,
            source=PaymentRecord.ESCROW,
            txn_id=str(uuid4()),
            target=order,
            type=PaymentRecord.TRANSFER,
            status=PaymentRecord.SUCCESS,
            response_code='OdrFnl',
            response_message='Order finalized.'
        )
        old_transaction = PaymentRecord.objects.get(
            object_id=order.id, content_type=ContentType.objects.get_for_model(order), payer=order.buyer,
            type=PaymentRecord.SALE
        )
        new_tx.save()
        old_transaction.finalized = True
        old_transaction.save()
        PaymentRecord.objects.create(
            payer=order.seller,
            amount=(
                    ((order.price + order.adjustment) * order.seller.percentage_fee * Decimal('.01'))
                    + Money(order.seller.static_fee, 'USD')
            ),
            payee=None,
            source=PaymentRecord.ACCOUNT,
            txn_id=str(uuid4()),
            target=order,
            type=PaymentRecord.TRANSFER,
            status=PaymentRecord.SUCCESS,
            response_code='OdrFee',
            finalized=new_tx.finalized,
            finalize_on=new_tx.finalize_on,
            response_message='Artconomy Service Fee'
        )
    # Don't worry about whether it's time to withdraw or not. This will make sure that an attempt is made in case
    # there's money to withdraw that hasn't been taken yet, and another process will try again if it settles later.
    # It will also ignore if the seller has auto_withdraw disabled.
    withdraw_all.delay(order.seller.id)


def claim_order_by_token(order_claim, user):
    from apps.sales.models import Order, buyer_subscriptions
    if not order_claim:
        return
    order = Order.objects.filter(claim_token=order_claim).first()
    if not order:
        logger.warning("User %s attempted to claim non-existent order token, %s", user, order_claim)
        return
    if order.seller == user:
        logger.warning("Seller %s attempted to claim their own order token, %s", user, order_claim)
        return
    order.claim_token = None
    order.buyer = user
    order.save()
    buyer_subscriptions(order)
    notify(ORDER_UPDATE, order, unique=True, mark_unread=True)
