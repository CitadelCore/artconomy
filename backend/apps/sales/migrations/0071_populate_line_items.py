# Generated by Django 2.2.9 on 2020-01-23 15:29
from collections import defaultdict
from decimal import Decimal
from functools import reduce
from typing import Iterator, List, Union, TYPE_CHECKING, Dict

from django.contrib.contenttypes.models import ContentType
from django.db import migrations

from django.db.models import F, Sum
from moneyed import Money

from apps.profiles.models import User
from apps.sales.models import TransactionRecord

BASE_PRICE = 0
ADD_ON = 1
SHIELD = 2
BONUS = 3
TIP = 4
TABLE_SERVICE = 5
TAX = 6
EXTRA = 7

PRIORITY_MAP = {
    BASE_PRICE: 0,
    ADD_ON: 100,
    TIP: 200,
    SHIELD: 300,
    BONUS: 300,
    TABLE_SERVICE: 300,
    EXTRA: 400,
    TAX: 600,
}

# Order statuses
NEW = 1
PAYMENT_PENDING = 2
QUEUED = 3
IN_PROGRESS = 4
REVIEW = 5
CANCELLED = 6
DISPUTED = 7
COMPLETED = 8
REFUNDED = 9

# Account types
CARD = 300
BANK = 301
ESCROW = 302
HOLDINGS = 303
# All fees put the difference for premium bonus into reserve until an order is complete. When complete, these
# amounts are deposited into either the cash account of Artconomy, or added to the user's holdings.
RESERVE = 304
# Earnings for which we have not yet subtracted card/bank transfer fees.
UNPROCESSED_EARNINGS = 305
# These two fee types will be used to keep track of fees that have been paid out to card processors.
CARD_TRANSACTION_FEES = 306
CARD_MISC_FEES = 307

# Fees from performing ACH transactions
ACH_TRANSACTION_FEES = 308
# Fees for other ACH-related items, like Dwolla's customer onboarding fees.
ACH_MISC_FEES = 309

CORRECTION = 310

# Transaction statuses
SUCCESS = 0


if TYPE_CHECKING:
    from apps.sales.models import LineItemSim, LineItem
    Line = Union[LineItem, LineItemSim]
    LineMoneyMap = Dict[Line, Money]
    TransactionSpecKey = (Union[User, None], int, int)
    TransactionSpecMap = Dict[TransactionSpecKey, Money]


def lines_by_priority(
        lines: Iterator[Union['LineItem', 'LineItemSim']]) -> List[List[Union['LineItem', 'LineItemSim']]]:
    """
    Groups line items by priority.
    """
    priority_sets = defaultdict(list)
    for line in lines:
        priority_sets[line.priority].append(line)
    return [priority_set for _, priority_set in sorted(priority_sets.items())]


def distribute_reduction(
        *, total: Money, distributed_amount: Money, line_values: 'LineMoneyMap'
) -> 'LineMoneyMap':
    reductions = {}
    for line, original_value in line_values.items():
        multiplier = original_value / total
        reductions[line] = Money(distributed_amount.amount * multiplier, 'USD')
    return reductions


def priority_total(
        current: (Money, 'LineMoneyMap'), priority_set: List['Line']
) -> (Money, 'LineMoneyMap'):
    """
    Get the effect on the total of a priority set. First runs any percentage increase, then
    adds in the static amount. Calculates the difference of each separately to make sure they're not affecting each
    other.
    """
    current_total, subtotals = current
    working_subtotals = {}
    summable_totals = {}
    reductions: List['LineMoneyMap'] = []
    for line in priority_set:
        # Percentages with equal priorities should not stack.
        working_amount = current_total * (Decimal('.01') * line.percentage)
        working_amount += line.amount
        if line.cascade_percentage:
            reductions.append(distribute_reduction(total=current_total, distributed_amount=working_amount, line_values={
                key: value for key, value in subtotals.items() if key.priority < line.priority
            }))
        else:
            summable_totals[line] = working_amount
        working_subtotals[line] = working_amount
    new_subtotals = {**subtotals}
    for reduction_set in reductions:
        for line, reduction in reduction_set.items():
            new_subtotals[line] -= reduction
    return current_total + sum(summable_totals.values()), {**new_subtotals, **working_subtotals}


def get_totals(
        lines: Iterator['Line']) -> (Money, 'LineMoneyMap'):
    priority_sets = lines_by_priority(lines)
    value, subtotals = reduce(priority_total, priority_sets, (Money('0.00', 'USD'), {}))
    return value, subtotals


def reckon_lines(lines) -> Money:
    """
    Reckons all line items to produce a total value.
    """
    value, _subtotals = get_totals(lines)
    return value.round(2)


def populate_line_items(apps, schema):
    Product = apps.get_model('sales', 'Product')
    Product.objects.filter(user__artist_profile__escrow_disabled=True).update(payout=F('price'))
    for product in Product.objects.filter(user__artist_profile__escrow_disabled=False):
        product.payout = product.price
    Order = apps.get_model('sales', 'Order')
    LineItem = apps.get_model('sales', 'LineItem')
    content_type_id = ContentType.objects.get_for_model(Order).id
    for order in Order.objects.filter(escrow_disabled=True):
        # We won't actually be transferring into escrow here, but if the product is ever converted to an
        # escrow product, this would do the right thing.
        if order.price is not None:
            original_price = order.price
        else:
            original_price = order.product.price
        LineItem.objects.create(
            order=order, amount=original_price, destination_user=order.seller, destination_account=ESCROW, priority=PRIORITY_MAP[BASE_PRICE],
            type=BASE_PRICE,
        )
        if order.adjustment:
            LineItem.objects.create(
                order=order, amount=order.adjustment, destination_user=order.seller, destination_account=ESCROW,
                priority=PRIORITY_MAP[ADD_ON], type=ADD_ON,
            )
        print(f'Migrated non-sheild order {order.id}')
    for order in Order.objects.filter(escrow_disabled=False):
        print(f'Migrating {order.id}')
        if order.price is not None:
            original_price = order.price
        else:
            original_price = order.product.price
        LineItem.objects.create(
            order=order, amount=original_price, destination_account=ESCROW, destination_user=order.seller, priority=PRIORITY_MAP[BASE_PRICE],
            type=BASE_PRICE,
        )
        adjustment_base_price = order.adjustment
        if order.adjustment:
            LineItem.objects.create(
                order=order, amount=order.adjustment, destination_account=ESCROW, destination_user=order.seller,
                type=ADD_ON, priority=PRIORITY_MAP[ADD_ON],
            )
        LineItem.objects.create(
            order=order, percentage=Decimal('4'), amount=Decimal('.50'), type=SHIELD,
            destination_account=RESERVE, destination_user=None, cascade_percentage=True,
            cascade_amount=True,
            priority=PRIORITY_MAP[SHIELD],
        )
        LineItem.objects.create(
            order=order, percentage=Decimal('4'), amount=Decimal('.25'), type=BONUS, destination_account=RESERVE,
            destination_user=None, cascade_percentage=True, cascade_amount=True,
            priority=PRIORITY_MAP[BONUS],
        )
        if order.tip:
            LineItem.objects.create(
                order=order, amount=order.tip, type=TIP,
                destination_account=ESCROW, destination_user=order.seller,
                priority=PRIORITY_MAP[TIP],
            )
        tabulated = reckon_lines(LineItem.objects.filter(order=order))
        original = (order.adjustment + original_price + order.tip)
        expected_payout = order.line_items.filter(
            type__in=[BASE_PRICE, ADD_ON, TIP],
        ).aggregate(total=Sum('amount'))['total']
        expected_payout = expected_payout - (expected_payout * Decimal('.08')) - Decimal('.75')
        actual_payout = TransactionRecord.objects.filter(
            object_id=order.id, content_type_id=content_type_id, source=ESCROW, destination=HOLDINGS,
            status=TransactionRecord.SUCCESS,
        ).aggregate(total=Sum('amount'))['total']
        if actual_payout:
            difference = expected_payout - actual_payout
            assert not difference, "Shit's broke, yo."
        difference = tabulated - original
        if abs(difference.amount) > Decimal('.01'):
            raise RuntimeError("TABULATED: ", tabulated, "ORIGINAL: ", original)


def clear_line_items(apps, schema):
    LineItem = apps.get_model('sales', 'LineItem')
    LineItem.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0070_auto_20200123_1528'),
    ]

    operations = [
        migrations.RunPython(populate_line_items, reverse_code=clear_line_items)
    ]
