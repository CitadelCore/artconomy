from decimal import Decimal
from unittest.mock import patch, Mock

from ddt import ddt, unpack, data
from django.test import TestCase, override_settings
from moneyed import Money

from apps.lib.models import NEW_PRODUCT
from apps.profiles.models import NO_US_ACCOUNT, HAS_US_ACCOUNT
from apps.profiles.tests.factories import UserFactory, SubmissionFactory
from apps.sales.models import TransactionRecord, BASE_PRICE, SHIELD, BONUS, TABLE_SERVICE, TAX, COMPLETED, QUEUED, NEW, \
    CANCELLED, Product
from apps.sales.tests.factories import RatingFactory, PromoFactory, TransactionRecordFactory, ProductFactory, \
    DeliverableFactory, \
    CreditCardTokenFactory, RevisionFactory, LineItemFactory


class TestRating(TestCase):
    def test_set_stars(self):
        user = UserFactory.create()
        rater = UserFactory.create()
        RatingFactory.create(target=user, stars=2, rater=rater)
        RatingFactory.create(target=user, stars=5, rater=rater)
        RatingFactory.create(target=user, stars=4, rater=rater)
        user.refresh_from_db()
        self.assertEqual(user.stars, Decimal('3.67'))
        self.assertEqual(user.rating_count, 3)


class TestPromo(TestCase):
    def test_promo_string(self):
        promo = PromoFactory.create(code='Wat')
        self.assertEqual(str(promo), 'WAT')


DESCRIPTION_VALUES = (
    {'price': Decimal('5.00'), 'prefix': '[Starts at $5.00] - ', 'escrow_disabled': False},
    {'price': Decimal('0'), 'prefix': '[Starts at FREE] - ', 'escrow_disabled': False},
    {'price': Decimal('0'), 'prefix': '[Starts at FREE] - ', 'escrow_disabled': True},
    {'price': Decimal('1.1'), 'prefix': '[Starts at $1.10] - ', 'escrow_disabled': True},
)


@ddt
class TestProduct(TestCase):
    def test_can_reference(self):
        user = UserFactory.create()
        product = ProductFactory.create(user=user)
        other = UserFactory.create()
        self.assertTrue(product.can_reference_asset(user))
        self.assertFalse(product.can_reference_asset(other))

    @patch('apps.sales.models.recall_notification')
    def test_recall(self, mock_recall_notification):
        user = UserFactory.create()
        product = ProductFactory.create(hidden=False, user=user)
        mock_recall_notification.assert_not_called()
        product.hidden = True
        product.save()
        mock_recall_notification.assert_called_with(NEW_PRODUCT, user, {'product': product.id}, unique_data=True)

    def test_notification_display(self):
        request = Mock()
        request.user = UserFactory.create()
        context = {'request': request}
        product = ProductFactory.create(user=request.user, primary_submission=SubmissionFactory.create())
        data = product.notification_display(context)
        self.assertEqual(data['id'], product.primary_submission.id)

    def test_escrow_disabled(self):
        product = ProductFactory.create(user__artist_profile__escrow_disabled=True)
        self.assertTrue(product.escrow_disabled)
        product.table_product = True
        self.assertFalse(product.escrow_disabled)
        product.table_product = False
        product.user.artist_profile.escrow_disabled = False
        self.assertFalse(product.escrow_disabled)

    @unpack
    @data(*DESCRIPTION_VALUES)
    def test_preview_description(self, price: Decimal, prefix: str, escrow_disabled: bool):
        account_status = NO_US_ACCOUNT if escrow_disabled else HAS_US_ACCOUNT
        product = ProductFactory.create(
            base_price=price, description='Test **Test** *Test*',
        )
        product.user.artist_profile.bank_status = account_status
        product.user.artist_profile.escrow_disabled = escrow_disabled
        product.user.artist_profile.save()
        self.assertTrue(
            product.preview_description.startswith(prefix),
            msg=f'{repr(product.preview_description)} does not start with {repr(prefix)}.',
        )
        self.assertTrue(
            product.preview_description.endswith('Test Test Test'),
            msg=f"{repr(product.preview_description)} does not end with 'Test Test Test'."
        )


class TestTransactionRecord(TestCase):
    def test_string(self):
        record = TransactionRecordFactory.create(payer__username='Dude', payee__username='Chick')
        self.assertEqual(
            str(record),
            'Successful [Escrow hold]: $10.00 from Dude [Credit Card] to Chick [Escrow] for None',
        )

    @patch('apps.sales.models.warn')
    @patch('apps.sales.models.refund_transaction')
    def test_default_refund(self, mock_refund_transaction, _mock_warn):
        card = CreditCardTokenFactory.create(last_four='1234')
        record = TransactionRecordFactory.create(card=card)
        mock_refund_transaction.return_value = '5678'
        record.refund()
        mock_refund_transaction.assert_called_with(record.remote_id, '1234', Decimal('10.00'))

    @patch('apps.sales.models.warn')
    def test_refund_account(self, _mock_warn):
        record = TransactionRecordFactory.create(source=TransactionRecord.ACH_MISC_FEES)
        with self.assertRaises(NotImplementedError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'Account refunds are not yet implemented.')

    @patch('apps.sales.models.warn')
    def test_refund_failed(self, _mock_warn):
        record = TransactionRecordFactory.create(status=TransactionRecord.FAILURE)
        with self.assertRaises(ValueError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'Cannot refund a failed transaction.')

    @patch('apps.sales.models.warn')
    def test_refund_wrong_type(self, _mock_warn):
        record = TransactionRecordFactory.create(source=TransactionRecord.BANK)
        with self.assertRaises(NotImplementedError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'ACH Refunds are not implemented.')

    @patch('apps.sales.models.warn')
    def test_refund_escrow(self, _mock_warn):
        record = TransactionRecordFactory.create(source=TransactionRecord.ESCROW)
        with self.assertRaises(ValueError) as context_manager:
            record.refund()
        self.assertEqual(
            str(context_manager.exception),
            'Cannot refund an escrow sourced payment. Are you sure you grabbed the right payment object?',
        )


@override_settings(
    SERVICE_PERCENTAGE_FEE=Decimal('5'),
    SERVICE_STATIC_FEE=Decimal('.25'),
    PREMIUM_PERCENTAGE_BONUS=Decimal('4'),
    PREMIUM_STATIC_BONUS=Decimal('.10'),
    TABLE_PERCENTAGE_FEE=Decimal('20'),
    TABLE_STATIC_FEE=Decimal('2.00'),
    TABLE_TAX=Decimal('8'),
)
class TestDeliverable(TestCase):
    def test_total(self):
        deliverable = DeliverableFactory.create(product__base_price=Money(5, 'USD'))
        self.assertEqual(deliverable.total(), Money('5.00', 'USD'))
        LineItemFactory.create(deliverable=deliverable, amount=Money('2.00', 'USD'))
        self.assertEqual(deliverable.total(), Money('7.00', 'USD'))

    def deliverable_and_context(self):
        deliverable = DeliverableFactory.create()
        deliverable.arbitrator = UserFactory.create()
        deliverable.save()
        request = Mock()
        request.user = deliverable.arbitrator
        context = {'request': request}
        return deliverable, context

    def test_notification_name(self):
        deliverable, context = self.deliverable_and_context()
        self.assertEqual(
            f'Case #{deliverable.order.id} [{deliverable.name}]',
            deliverable.notification_name(context),
        )
        deliverable.buyer = deliverable.arbitrator
        deliverable.arbitrator = None
        self.assertEqual(
            f'Order #{deliverable.order.id} [{deliverable.name}]',
            deliverable.notification_name(context),
        )

    def test_notification_link(self):
        deliverable, context = self.deliverable_and_context()
        self.assertEqual(
            {'name': 'CaseDeliverableOverview', 'params': {
                'orderId': deliverable.order.id,
                'deliverableId': deliverable.id,
                'username': context['request'].user.username,
            }},
            deliverable.notification_link(context),
        )
        deliverable.buyer = deliverable.arbitrator
        deliverable.arbitrator = None
        deliverable.save()
        self.assertEqual(
            {'name': 'OrderDeliverableOverview', 'params': {
                'orderId': deliverable.order.id,
                'deliverableId': deliverable.id,
                'username': context['request'].user.username,
            }},
            deliverable.notification_link(context),
        )

    def test_notification_link_guest(self):
        deliverable, context = self.deliverable_and_context()
        deliverable.order.buyer = UserFactory.create(guest=True, username='__1')
        deliverable.order.claim_token = 'y1zGvlKfTnmA'
        deliverable.order.save()
        context['request'].user = deliverable.order.buyer
        self.assertEqual(
            {
                'name': 'OrderClaim',
                'params': {
                    'claim_token': 'y1zGvlKfTnmA',
                    'order_id': deliverable.order.id,
                    'deliverable_id': deliverable.id,
                },
            },
            deliverable.notification_link(context),
        )

    def test_notification_link_deliverable(self):
        deliverable, context = self.deliverable_and_context()
        DeliverableFactory.create(order=deliverable.order)
        self.assertEqual(
            {'name': 'CaseDeliverableOverview', 'params': {
                'orderId': deliverable.order.id,
                'deliverableId': deliverable.id,
                'username': context['request'].user.username,
            }},
            deliverable.notification_link(context),
        )
        deliverable.buyer = deliverable.arbitrator
        deliverable.arbitrator = None
        deliverable.save()
        self.assertEqual(
            {'name': 'OrderDeliverableOverview', 'params': {
                'orderId': deliverable.order.id,
                'deliverableId': deliverable.id,
                'username': context['request'].user.username,
            }},
            deliverable.notification_link(context),
        )

    def test_notification_display(self):
        deliverable, context = self.deliverable_and_context()
        deliverable.product.primary_submission = SubmissionFactory.create()
        output = deliverable.notification_display(context)
        self.assertEqual(output['id'], deliverable.product.primary_submission.id)
        self.assertEqual(output['title'], deliverable.product.primary_submission.title)

    def test_notification_display_revision(self):
        deliverable, context = self.deliverable_and_context()
        deliverable.product.primary_submission = SubmissionFactory.create()
        deliverable.revisions_hidden = False
        revision = RevisionFactory.create(deliverable=deliverable)
        output = deliverable.notification_display(context)
        self.assertEqual(output['id'], revision.id)
        self.assertIn(revision.file.file.name, output['file']['full'])

    def test_create_line_items_escrow(self):
        deliverable = DeliverableFactory.create(product__base_price=Money('15.00', 'USD'))
        base_price = deliverable.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money('15.00', 'USD'))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        shield = deliverable.line_items.get(type=SHIELD)
        self.assertEqual(shield.percentage, Decimal('5'))
        self.assertEqual(shield.amount, Money('.25', 'USD'))
        self.assertTrue(shield.cascade_percentage)
        self.assertTrue(shield.cascade_amount)
        bonus = deliverable.line_items.get(type=BONUS)
        self.assertEqual(bonus.percentage, Decimal('4'))
        self.assertEqual(bonus.amount, Money('.10', 'USD'))
        self.assertTrue(bonus.cascade_percentage)
        self.assertTrue(bonus.cascade_amount)
        self.assertEqual(bonus.priority, shield.priority)
        self.assertEqual(deliverable.line_items.all().count(), 3)

    def test_create_line_items_non_escrow(self):
        deliverable = DeliverableFactory.create(product__base_price=Money('15.00', 'USD'), escrow_disabled=True)
        base_price = deliverable.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money('15.00', 'USD'))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        self.assertEqual(deliverable.line_items.all().count(), 1)

    def test_create_line_items_table_service(self):
        deliverable = DeliverableFactory.create(product__base_price=Money('15.00', 'USD'), table_order=True)
        base_price = deliverable.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money('15.00', 'USD'))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        table_service = deliverable.line_items.get(type=TABLE_SERVICE)
        self.assertEqual(table_service.percentage, Decimal('20'))
        self.assertEqual(table_service.amount, Money('2.00', 'USD'))
        self.assertTrue(table_service.cascade_percentage)
        self.assertFalse(table_service.cascade_amount)
        self.assertFalse(table_service.back_into_percentage)
        set_on_fire = deliverable.line_items.get(type=TAX)
        self.assertEqual(set_on_fire.percentage, Decimal('8'))
        self.assertEqual(set_on_fire.amount, Money('0.00', 'USD'))
        self.assertTrue(set_on_fire.back_into_percentage)
        self.assertEqual(deliverable.line_items.all().count(), 3)


class TestCreditCardToken(TestCase):
    def test_string(self):
        card = CreditCardTokenFactory.create(last_four='1234')
        self.assertEqual(str(card), 'Visa ending in 1234')
        card.active = False
        self.assertEqual(str(card), 'Visa ending in 1234 (Deleted)')

    def test_no_delete(self):
        card = CreditCardTokenFactory.create()
        self.assertRaises(RuntimeError, card.delete)


class TestRevision(TestCase):
    def test_can_reference(self):
        user = UserFactory.create()
        buyer = UserFactory.create()
        revision = RevisionFactory.create(
            owner=user, deliverable__order__seller=user,
            deliverable__product__user=user, deliverable__order__buyer=buyer,
        )
        other = UserFactory.create()
        self.assertTrue(revision.can_reference_asset(revision.owner))
        self.assertFalse(revision.can_reference_asset(other))
        self.assertFalse(revision.can_reference_asset(buyer))
        revision.deliverable.status = COMPLETED
        self.assertTrue(revision.can_reference_asset(buyer))


class TestLoadAdjustment(TestCase):
    def test_load_changes(self):
        user = UserFactory.create()
        user.artist_profile.max_load = 10
        user.artist_profile.save()
        DeliverableFactory.create(task_weight=5, status=QUEUED, order__seller=user)
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order = DeliverableFactory.create(task_weight=5, status=NEW, order__seller=user)
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order.status = QUEUED
        order.save()
        user.refresh_from_db()
        # Max load reached.
        self.assertEqual(user.artist_profile.load, 10)
        self.assertTrue(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order2 = DeliverableFactory.create(task_weight=5, status=NEW, order__seller=user)
        user.refresh_from_db()
        # Now we have an order in a new state. This shouldn't undo the disability.
        self.assertEqual(user.artist_profile.load, 10)
        self.assertTrue(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order.status = COMPLETED
        order.save()
        user.refresh_from_db()
        # We have reduced the load, but never took care of the new order, so commissions are still disabled.
        self.assertEqual(user.artist_profile.load, 5)
        self.assertTrue(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order2.status = CANCELLED
        order2.save()
        order.save()
        # Cancalled the new order, so now the load is within parameters and there are no outstanding new orders.
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        # Closing commissions should disable them as well.
        user.artist_profile.commissions_closed = True
        user.save()
        self.assertTrue(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        user.artist_profile.commissions_closed = False
        order.status = NEW
        order.save()
        # Unclosing commissions shouldn't enable commissions if they still have an outstanding order.
        user.refresh_from_db()
        user.artist_profile.commissions_closed = False
        user.save()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        order.status = CANCELLED
        order.save()
        # We should be clear again.
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertFalse(user.artist_profile.commissions_disabled)
        Product.objects.all().delete()
        # Make a product too big for the user to complete. Should close the user.
        product = ProductFactory.create(user=user, task_weight=20)
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        # And dropping it should open them back up.
        product.task_weight = 1
        product.save()
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertFalse(user.artist_profile.commissions_disabled)
