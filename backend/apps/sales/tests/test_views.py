from decimal import Decimal
from unittest.mock import patch, Mock

from dateutil.relativedelta import relativedelta
from ddt import data, unpack, ddt
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from django.utils.datetime_safe import date
from moneyed import Money
from rest_framework import status

from apps.lib.abstract_models import ADULT
from apps.lib.models import Comment, Subscription, COMMENT
from apps.lib.test_resources import APITestCase, PermissionsTestCase, MethodAccessMixin
from apps.lib.tests.factories import TagFactory, AssetFactory
from apps.lib.tests.test_utils import EnsurePlansMixin
from apps.profiles.models import User, IN_SUPPORTED_COUNTRY, NO_SUPPORTED_COUNTRY, UNSET, ArtistTag
from apps.profiles.tests.factories import UserFactory, SubmissionFactory, CharacterFactory
from apps.sales.models import (
    Order, Product, TransactionRecord, ADD_ON, BASE_PRICE, NEW, COMPLETED, IN_PROGRESS,
    PAYMENT_PENDING,
    REVIEW, QUEUED, DISPUTED, CANCELLED, DELIVERABLE_STATUSES, REFUNDED, Deliverable, WAITING, OPEN)
from apps.sales.tests.factories import DeliverableFactory, CreditCardTokenFactory, ProductFactory, RevisionFactory, \
    RatingFactory, ReferenceFactory, ServicePlanFactory, InvoiceFactory
from apps.sales.views.views import (
    CurrentOrderList, CurrentSalesList, CurrentCasesList,
    CancelledOrderList,
    ArchivedOrderList,
    CancelledSalesList,
    ArchivedSalesList,
    CancelledCasesList,
    ArchivedCasesList,
    ProductList)

order_scenarios = (
    {
        'category': 'current',
        'included': (NEW, IN_PROGRESS, DISPUTED, REVIEW, PAYMENT_PENDING, QUEUED),
    },
    {
        'category': 'archived',
        'included': (COMPLETED,),
    },
    {
        'category': 'cancelled',
        'included': (REFUNDED, CANCELLED),
    }
)

categories = [scenario['category'] for scenario in order_scenarios]


@ddt
class TestOrderListBase(object):
    @unpack
    @data(*order_scenarios)
    def test_fetch_orders(self, category, included):
        user = UserFactory.create(username='Fox')
        kwargs = self.factory_kwargs(user)
        [
            DeliverableFactory.create(
                status=order_status, **kwargs) for order_status in [x for x, y in DELIVERABLE_STATUSES]
        ]
        user = User.objects.get(username='Fox')
        self.login(user)
        response = self.client.get(self.make_url(user, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for order in response.data['results']:
            self.assertIn(Deliverable.objects.filter(order_id=order['id']).first().status, included)
        self.assertEqual(len(response.data['results']), len(included))


class TestOrderLists(TestOrderListBase, APITestCase):
    fixture_list = ['order-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/orders/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        return {'order__buyer': user, 'order__seller': UserFactory.create()}


class TestSaleLists(TestOrderListBase, APITestCase):
    fixture_list = ['sale-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/sales/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        return {'order__seller': user, 'order__buyer': UserFactory.create()}


class TestCaseLists(TestOrderListBase, APITestCase):
    fixture_list = ['case-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/cases/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        user.is_staff = True
        user.save()
        return {'arbitrator': user, 'order__buyer': UserFactory.create(), 'order__seller': UserFactory.create()}


order_passes = {**MethodAccessMixin.passes, 'get': ['user', 'staff']}


class TestCurrentOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = CurrentOrderList


class TestCancelledOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = CancelledOrderList


class TestArchivedOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = ArchivedOrderList


class TestCurrentSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = CurrentSalesList


class TestCancelledSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = CancelledSalesList


class TestArchivedSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = ArchivedSalesList


class StaffUserList:
    def test_self(self):
        request = self.factory.get('/')
        request.user = self.user
        self.check_perms(request, self.user)

    def test_self_staff(self):
        request = self.factory.get('/')
        request.user = self.user
        request.user.is_staff = True
        self.check_perms(request, self.user, fails=False)


staff_order_passes = {**order_passes, 'get': ['staff']}


class TestCurrentCasesListPermissions(PermissionsTestCase, StaffUserList, MethodAccessMixin):
    passes = staff_order_passes
    kwargs = {'username': 'Test'}
    view_class = CurrentCasesList


class TestCancelledCasesListPermissions(PermissionsTestCase, StaffUserList, MethodAccessMixin):
    passes = staff_order_passes
    kwargs = {'username': 'Test'}
    view_class = CancelledCasesList


class TestArchivedCasesListPermissions(PermissionsTestCase, StaffUserList, MethodAccessMixin):
    passes = staff_order_passes
    kwargs = {'username': 'Test'}
    view_class = ArchivedCasesList


class TestSamples(APITestCase):
    def test_sample_list(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        response = self.client.get(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/samples/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['submission']['id'], submission.id)

    def test_destroy_sample(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        linked = Product.samples.through.objects.get(submission=submission, product=product)
        self.login(product.user)
        response = self.client.delete(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/samples/{linked.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(product.samples.all().count(), 0)

    def test_destroy_sample_primary(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        product.primary_submission = submission
        product.save()
        linked = Product.samples.through.objects.get(submission=submission, product=product)
        self.login(product.user)
        response = self.client.delete(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/samples/{linked.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(product.samples.all().count(), 0)
        product.refresh_from_db()
        self.assertIsNone(product.primary_submission)

    def test_add_sample(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        submission.artists.add(product.user)
        self.login(product.user)
        response = self.client.post(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/samples/',
            {'submission_id': submission.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['submission']['id'], submission.id)


class TestCardManagement(APITestCase):
    def test_make_primary(self):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.login(user)
        user.refresh_from_db()
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/{}/primary/'.format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, cards[2].id)
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(
            user.username, cards[3].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, cards[3].id)

    def test_make_primary_not_logged_in(self):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/{}/primary/'.format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/{}/primary/'.format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_wrong_card(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.login(user)
        user.refresh_from_db()
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(
            user.username, CreditCardTokenFactory.create(user=user2).id
        ))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_card_listing(self):
        user = UserFactory.create()
        self.login(user)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data)

    def test_card_listing_stripe(self):
        user = UserFactory.create()
        self.login(user)
        _authorize_cards = [CreditCardTokenFactory(user=user, token='boop', stripe_token=None) for __ in range(3)]
        stripe_cards = [CreditCardTokenFactory(user=user, token='', stripe_token=f'{i}') for i in range(2)]
        response = self.client.get('/api/sales/v1/account/{}/cards/stripe/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in stripe_cards:
            self.assertIDInList(card, response.data)
        self.assertEqual(len(response.data), len(stripe_cards))

    def test_card_listing_not_logged_in(self):
        user = UserFactory.create()
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_listing_staffer(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data)

    @patch('apps.sales.models.delete_payment_method')
    def test_card_removal(self, _delete_payment_method):
        user = UserFactory.create()
        self.login(user)
        cards = [CreditCardTokenFactory(user=user, stripe_token=f'{i}') for i in range(4)]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)

    @patch('apps.sales.models.delete_payment_method')
    def test_card_removal_new_primary(self, _mock_execute):
        old_card = CreditCardTokenFactory.create()
        new_card = CreditCardTokenFactory.create(user=old_card.user)
        user = old_card.user
        user.primary_card = new_card
        user.save()
        self.login(user)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, new_card.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card, old_card)

    @patch('apps.sales.models.delete_payment_method')
    def test_card_removal_not_logged_in(self, _mock_execute):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user, stripe_token=f'{i}') for i in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    @patch('apps.sales.models.delete_payment_method')
    def test_card_removal_outsider(self, _mock_execute):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        cards = [CreditCardTokenFactory(user=user, stripe_token=f'{i}') for i in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    @patch('apps.sales.models.delete_payment_method')
    def test_card_removal_staff(self, _mock_execute):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        cards = [CreditCardTokenFactory(user=user, stripe_token=f'{i}') for i in range(4)]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)


class TestProductListPermissions(PermissionsTestCase, MethodAccessMixin):
    passes = {**MethodAccessMixin.passes}
    passes['get'] = ['user', 'staff', 'outsider', 'anonymous']
    passes['post'] = ['user', 'staff']
    view_class = ProductList

    def get_object(self):
        product = Mock()
        product.user = self.user
        return product


class TestProduct(APITestCase):
    def test_product_listing_logged_in(self):
        user = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        hidden = ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        for product in products:
            self.assertIDInList(product, response.data['results'])
        self.assertIDInList(hidden, response.data['results'])

    def test_create_product(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 2.50,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], 3.00)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_free(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 0,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], 3.00)
        self.assertEqual(result['base_price'], 0.00)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(MINIMUM_PRICE=Decimal('1.00'))
    def test_create_product_minimum_unmet(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 0.50,
            }
        )
        result = response.data
        self.assertEqual(result['base_price'], ['Must be at least $1.00'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(MINIMUM_PRICE=Decimal('1.00'))
    def test_create_product_minimum_irrelevant(self):
        user = UserFactory.create(artist_profile__escrow_disabled=True)
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 0.50,
            }
        )
        result = response.data
        self.assertEqual(result['base_price'], 0.50)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_not_logged_in(self):
        user = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 2.50,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=user)
        self.login(user2)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 2.50,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_staff(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=staffer)
        self.login(staffer)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 2.50,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], 3.00)
        self.assertEqual(result['base_price'], 2.50)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_listing_not_logged_in(self):
        user = UserFactory.create()
        products = [ProductFactory.create(user=user) for __ in range(3)]
        ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        for product in products:
            self.assertIDInList(product, response.data['results'])

    def test_product_listing_other_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        for product in products:
            self.assertIDInList(product, response.data['results'])

    def test_product_inventory(self):
        product = ProductFactory.create(track_inventory=True)
        response = self.client.get(f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_set_product_inventory_not_logged_in(self):
        product = ProductFactory.create(track_inventory=True)
        response = self.client.patch(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/',
            {'count': 3}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_product_inventory_wrong_user(self):
        product = ProductFactory.create(track_inventory=True)
        self.login(UserFactory.create())
        response = self.client.patch(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/',
            {'count': 3}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_product_inventory(self):
        product = ProductFactory.create(track_inventory=True)
        self.login(product.user)
        response = self.client.patch(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/',
            {'count': 3}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_product_inventory_no_tracking(self):
        product = ProductFactory.create(track_inventory=False)
        response = self.client.get(f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_listing_staff(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        hidden = ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        for product in products:
            self.assertIDInList(product, response.data['results'])
        self.assertIDInList(hidden, response.data['results'])

    def test_product_delete(self):
        user = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)

    def test_product_delete_not_logged_in(self):
        user = UserFactory.create()
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_wrong_product(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user2) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_staffer(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        DeliverableFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete(
            '/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(
            '/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)


class TestComment(APITestCase):
    def test_make_comment(self):
        deliverable = DeliverableFactory.create()
        self.login(deliverable.order.buyer)
        response = self.client.post(
            '/api/lib/v1/comments/sales.Deliverable/{}/'.format(deliverable.id),
            {'text': 'test comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = response.data
        self.assertEqual(comment['text'], 'test comment')
        self.assertEqual(comment['user']['username'], deliverable.order.buyer.username)
        Comment.objects.get(id=comment['id'])


class TestProductSearch(APITestCase):
    def test_query_not_logged_in(self):
        product1 = ProductFactory.create(name='Test1')
        product2 = ProductFactory.create(name='Wat product 2')
        tag = TagFactory.create(name='test')
        product2.tags.add(tag)
        product3 = ProductFactory.create(
            name='Test3', task_weight=5, user__artist_profile__load=2, user__artist_profile__max_load=10,
        )
        # Hidden products
        ProductFactory.create(name='TestHidden', hidden=True)
        hidden = ProductFactory.create(name='Wat2 hidden', hidden=True)
        hidden.tags.add(tag)
        ProductFactory.create(
            name='Test4 overload', task_weight=5, user__artist_profile__load=10, user__artist_profile__max_load=10,
        )
        maxed = ProductFactory.create(name='Test5 maxed', max_parallel=2)
        DeliverableFactory.create(product=maxed, status=IN_PROGRESS)
        DeliverableFactory.create(product=maxed, status=QUEUED)
        maxed.refresh_from_db()
        overloaded = ProductFactory.create(name='Test6 overloaded', task_weight=1, user__artist_profile__max_load=5)
        DeliverableFactory.create(order__seller=overloaded.user, task_weight=7, status=IN_PROGRESS)
        ProductFactory.create(name='Test commissions closed', user__artist_profile__commissions_closed=True)
        overloaded.user.refresh_from_db()

        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})

        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)

    def test_query_logged_in(self):
        user = UserFactory.create(username='Fox')
        user2 = UserFactory.create()
        product1 = ProductFactory.create(name='Test1')
        product2 = ProductFactory.create(name='Wat')
        tag = TagFactory.create(name='test')
        product2.tags.add(tag)
        product3 = ProductFactory.create(name='Test3', task_weight=5)
        # Overweighted.
        ProductFactory.create(name='Test4', task_weight=100, user=user)
        product4 = ProductFactory.create(name='Test5', max_parallel=2, user=user)
        DeliverableFactory.create(product=product4)
        DeliverableFactory.create(product=product4)
        # Product from blocked user. Shouldn't be in results.
        ProductFactory.create(name='Test Blocked', user=user2)
        user.blocking.add(user2)

        ProductFactory.create(user__artist_profile__commissions_closed=True)

        user.artist_profile.max_load = 10
        user.artist_profile.load = 2
        user.artist_profile.save()

        user = User.objects.get(username='Fox')
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertIDInList(product4, response.data['results'])
        self.assertEqual(len(response.data['results']), 4)

    def test_query_different_user(self):
        product1 = ProductFactory.create(name='Test1')
        product2 = ProductFactory.create(name='Wat')
        tag = TagFactory.create(name='test')
        product2.tags.add(tag)
        product3 = ProductFactory.create(
            name='Test3', task_weight=5, user__artist_profile__load=2, user__artist_profile__max_load=10
        )
        # Hidden products
        ProductFactory.create(name='Test4', hidden=True)
        hidden = ProductFactory.create(name='Wat2', hidden=True)
        hidden.tags.add(tag)
        ProductFactory.create(
            name='Test5', task_weight=5, user__artist_profile__load=8, user__artist_profile__max_load=10,
        )
        overloaded = ProductFactory.create(name='Test6', max_parallel=2)
        ProductFactory.create(user__artist_profile__commissions_closed=True)
        DeliverableFactory.create(product=overloaded, status=IN_PROGRESS)
        DeliverableFactory.create(product=overloaded, status=QUEUED)

        user = UserFactory.create(username='Fox')
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)

    def test_blocked(self):
        product = ProductFactory.create(name='Test1')
        user = UserFactory.create(username='Fox')
        user.blocking.add(product.user)
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertEqual(len(response.data['results']), 0)

    def test_personal(self):
        user = UserFactory.create(username='Fox')
        listed = ProductFactory.create(user=user, name='Test')
        listed2 = ProductFactory.create(user=user, name='Test2', hidden=True)
        listed3 = ProductFactory.create(user=user, task_weight=999, name='Test3')
        # Inactive.
        ProductFactory.create(user=user, active=False, name='Test4')
        # Wrong user.
        ProductFactory.create(name='Test5')

        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/Fox/', {'q': 'test'})
        self.assertIDInList(listed, response.data['results'])
        self.assertIDInList(listed2, response.data['results'])
        self.assertIDInList(listed3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)


class TestCancelPremium(EnsurePlansMixin, APITestCase):
    def test_cancel(self):
        user = UserFactory.create()
        self.login(user)
        user.service_plan = self.landscape
        user.next_service_plan = self.landscape
        user.service_plan_paid_through = date(2017, 11, 18)
        user.save()
        response = self.client.post(f'/api/sales/v1/account/{user.username}/cancel-premium/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 11, 18))


class TestCreateInvoice(APITestCase):
    def test_create_invoice_no_bank_configured(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = UNSET
        user.artist_profile.save()
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invoice(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': user2.username,
            'price': '5.00',
            'details': 'wat',
            'private': False,
            'rating': ADULT,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['status'], PAYMENT_PENDING)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(order.private, False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['revisions_hidden'])
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)

        deliverable = Deliverable.objects.get(id=response.data['id'])
        self.assertEqual(deliverable.invoice.status, OPEN)
        item = deliverable.invoice.line_items.get(type=ADD_ON)
        self.assertEqual(item.amount, Money('2.00', 'USD'))
        self.assertEqual(item.priority, 100)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        item = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(item.amount, Money('3.00', 'USD'))
        self.assertEqual(item.priority, 0)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        self.assertIsNone(order.claim_token)
        self.assertFalse(deliverable.invoice.record_only)

    def test_create_invoice_table_product(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1, table_product=True,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': user2.username,
            'price': '15.00',
            'details': 'wat',
            'private': False,
            'task_weight': 3,
            'rating': ADULT,
            'revisions': 3,
            'paid': False,
            'hold': False,
            'expected_turnaround': 4
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['status'], PAYMENT_PENDING)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(order.private, False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['revisions_hidden'])
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)

        deliverable = Deliverable.objects.get(id=response.data['id'])
        # Actual price will be $8-- $3 plus the $5 static fee. Setting the order price to $15 will make a $7 adjustment.
        item = deliverable.invoice.line_items.get(type=ADD_ON)
        self.assertEqual(item.amount, Money('7.00', 'USD'))
        self.assertEqual(item.priority, 100)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        item = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(item.amount, Money('3.00', 'USD'))
        self.assertEqual(item.priority, 0)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        self.assertIsNone(order.claim_token)
        self.assertFalse(deliverable.invoice.record_only)

    def test_create_invoice_email(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': 'test@example.com',
            'price': '5.00',
            'details': 'oh',
            'rating': ADULT,
            'private': True,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(order.customer_email, 'test@example.com')
        self.assertTrue(order.claim_token)

    def test_create_invoice_completed(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': True,
            'product': product.id,
            'buyer': 'test@example.com',
            'price': '5.00',
            'details': 'oh',
            'rating': ADULT,
            'private': True,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4,
            'paid': False,
            'hold': False,
        })
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data['adjustment_task_weight'], -5)
        self.assertEqual(response.data['adjustment_expected_turnaround'], -2)
        self.assertEqual(response.data['adjustment_revisions'], -1)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)

        self.assertEqual(order.customer_email, 'test@example.com')
        self.assertTrue(order.claim_token)

    def test_create_invoice_no_product(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': None,
            'buyer': 'test@example.com',
            'price': '5.00',
            'details': 'oh',
            'private': True,
            'rating': ADULT,
            'task_weight': 2,
            'paid': False,
            'hold': False,
            'revisions': 3,
            'expected_turnaround': 4
        }, format='json')
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data['adjustment_task_weight'], 0)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 0)
        self.assertEqual(response.data['adjustment_revisions'], 0)
        self.assertEqual(response.data['task_weight'], 2)
        self.assertEqual(response.data['revisions'], 3)
        self.assertEqual(response.data['details'], 'oh')
        self.assertEqual(response.data['expected_turnaround'], 4)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product'], None)

        self.assertEqual(order.customer_email, 'test@example.com')
        self.assertTrue(order.claim_token)

    def test_create_invoice_no_product_nonsheild(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = NO_SUPPORTED_COUNTRY
        user.artist_profile.save()
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': None,
            'buyer': 'test@example.com',
            'price': '5.00',
            'details': 'oh',
            'private': True,
            'rating': ADULT,
            'task_weight': 2,
            'paid': False,
            'hold': False,
            'revisions': 3,
            'expected_turnaround': 4
        }, format='json')
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data['adjustment_task_weight'], 0)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 0)
        self.assertEqual(response.data['adjustment_revisions'], 0)
        self.assertEqual(response.data['task_weight'], 2)
        self.assertEqual(response.data['revisions'], 3)
        self.assertEqual(response.data['details'], 'oh')
        self.assertEqual(response.data['expected_turnaround'], 4)
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(response.data['product'], None)

        self.assertEqual(order.customer_email, 'test@example.com')
        self.assertTrue(order.claim_token)

    def test_create_invoice_escrow_disabled(self):
        user = UserFactory.create(artist_mode=True)
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = NO_SUPPORTED_COUNTRY
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': user2.username,
            'price': '5.00',
            'task_weight': 3,
            'details': 'bla bla',
            'rating': ADULT,
            'private': True,
            'revisions': 3,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['details'], 'bla bla')
        self.assertTrue(order.private)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertIsNone(order.claim_token)

    def test_create_invoice_paid(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': user2.username,
            'price': '5.00',
            'paid': True,
            'hold': False,
            'rating': ADULT,
            'details': 'wat',
            'private': False,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['status'], QUEUED)
        self.assertEqual(response.data['details'], 'wat')
        self.assertFalse(order.private)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertFalse(response.data['revisions_hidden'])
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertIsNone(order.claim_token)

    def test_create_invoice_paid_and_completed(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': True,
            'product': product.id,
            'buyer': user2.username,
            'price': '5.00',
            'paid': True,
            'hold': False,
            'rating': ADULT,
            'details': 'wat',
            'private': False,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['status'], IN_PROGRESS)
        self.assertEqual(response.data['details'], 'wat')
        self.assertFalse(order.private)
        self.assertEqual(response.data['adjustment_task_weight'], -5)
        self.assertEqual(response.data['adjustment_expected_turnaround'], -2)
        self.assertEqual(response.data['adjustment_revisions'], -1)
        self.assertFalse(response.data['revisions_hidden'])
        self.assertEqual(response.data['rating'], ADULT)
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertIsNone(order.claim_token)


class TestLists(APITestCase):
    def test_new_products(self):
        user = UserFactory.create()
        product = ProductFactory.create(user=user)
        response = self.client.get('/api/sales/v1/new-products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], product.id)

    def test_who_is_open(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create()
        response = self.client.get('/api/sales/v1/who-is-open/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        user.watching.add(product.user)
        response = self.client.get('/api/sales/v1/who-is-open/')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], product.id)

    def test_rating_list(self):
        user = UserFactory.create()
        rating = RatingFactory.create(target=user)
        response = self.client.get(f'/api/sales/v1/account/{user.username}/ratings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], rating.id)

    def test_featured_products(self):
        ProductFactory.create(active=False, featured=True)
        active_product = ProductFactory.create(active=True, featured=True)
        ProductFactory.create(active=True, featured=True, hidden=True)
        response = self.client.get('/api/sales/v1/featured-products/')
        self.assertEqual(len(response.data['results']), 1)
        self.assertIDInList(active_product, response.data['results'])


class TestSalesStats(APITestCase):
    def test_sales_stats(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.get(f'/api/sales/v1/account/{user.username}/sales/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPremiumInfo(APITestCase):
    @override_settings(PREMIUM_PERCENTAGE_BONUS=Decimal('69'))
    def test_premium_info(self):
        self.landscape = ServicePlanFactory.create(name='Landscape')
        response = self.client.get(f'/api/sales/v1/pricing-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['premium_percentage_bonus'], Decimal('69'))


class TestOrderAuth(APITestCase):
    def test_anon_to_existing_guest(self):
        order = DeliverableFactory.create(order__buyer=UserFactory.create(
            email='wat@localhost', guest_email='test@example.com', guest=True,
            username='__3'
        )).order
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.buyer.id)

    def test_anon_to_new_guest(self):
        order = DeliverableFactory.create(order__buyer=None, order__customer_email='test@example.com').order
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['guest_email'], 'test@example.com')
        self.assertEqual(response.data['email'][-9:], 'localhost')
        order.refresh_from_db()
        self.assertEqual(response.data['id'], order.buyer.id)

    def test_anon_chown_attempt(self):
        order = DeliverableFactory.create(order__buyer=None, order__customer_email='test@example.com').order
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_seller_chown_attempt(self):
        order = DeliverableFactory.create(order__buyer=None, order__customer_email='test@example.com').order
        self.login(order.seller)
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_chown_no_guest(self):
        order = DeliverableFactory.create(order__buyer=None, order__customer_email='test@example.com').order
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertEqual(order.deliverables.first().invoice.bill_to, user)
        self.assertIsNone(order.claim_token)
        self.assertEqual(order.customer_email, '')

    def test_order_already_claimed(self):
        order = DeliverableFactory.create().order
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': '97uh97',
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_revisiting(self):
        order = DeliverableFactory.create(order__buyer=UserFactory.create(
            email='wat@localhost', guest_email='test@example.com', guest=True,
            username='__3'
        )).order
        self.login(order.buyer)
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': '97uh97',
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], '__3')

    def test_invalid_token(self):
        order = DeliverableFactory.create(order__buyer=UserFactory.create(
            email='wat@localhost', guest_email='test@example.com', guest=True,
            username='__3'
        )).order
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': '97uh97',
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestOrderOutputs(APITestCase):
    def test_order_outputs_get(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        revision = RevisionFactory.create()
        submission = SubmissionFactory.create(deliverable=deliverable, revision=revision)
        response = self.client.get(f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIDInList(submission, response.data)

    def test_order_outputs_post(self):
        deliverable = DeliverableFactory.create(status=COMPLETED, final_uploaded=True)
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)
        self.assertIn(deliverable.order.seller, output.artists.all())
        tag = ArtistTag.objects.get(user=deliverable.order.seller, submission=output)
        self.assertFalse(tag.hidden)

    def test_order_outputs_post_specific_revision(self):
        product = ProductFactory.create()
        deliverable = DeliverableFactory.create(status=COMPLETED, final_uploaded=True, product=product)
        revision_1 = RevisionFactory.create(deliverable=deliverable, created_on=timezone.now() - relativedelta(days=1))
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'revision': revision_1.id,
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)
        self.assertEqual(output.revision, revision_1)
        self.assertNotIn(output, product.samples.all())

    def test_order_outputs_post_hidden_details_buyer(self):
        deliverable = DeliverableFactory.create(status=COMPLETED, final_uploaded=True, order__hide_details=True)
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        output = deliverable.outputs.all()[0]
        tag = ArtistTag.objects.get(user=deliverable.order.seller, submission=output)
        self.assertTrue(tag.hidden)

    def test_order_outputs_post_hidden_details_seller(self):
        deliverable = DeliverableFactory.create(status=COMPLETED, final_uploaded=True, order__hide_details=True)
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.seller)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        output = deliverable.outputs.all()[0]
        tag = ArtistTag.objects.get(user=deliverable.order.seller, submission=output)
        self.assertFalse(tag.hidden)

    def test_order_outputs_post_nonspecific_revision_buyer(self):
        product = ProductFactory.create()
        deliverable = DeliverableFactory.create(status=COMPLETED, final_uploaded=True, product=product)
        character = CharacterFactory.create(primary_submission=None, user=deliverable.order.buyer)
        deliverable.characters.add(character)
        RevisionFactory.create(deliverable=deliverable, created_on=timezone.now() - relativedelta(days=1))
        revision_2 = RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)
        self.assertEqual(output.revision, revision_2)
        product.refresh_from_db()
        self.assertNotIn(output, product.samples.all())
        character.refresh_from_db()
        self.assertEqual(output, character.primary_submission)

    def test_order_outputs_post_nonspecific_revision_seller(self):
        product = ProductFactory.create()
        deliverable = DeliverableFactory.create(status=COMPLETED, final_uploaded=True, product=product)
        character = CharacterFactory.create(primary_submission=None, user=deliverable.order.buyer)
        deliverable.characters.add(character)
        RevisionFactory.create(deliverable=deliverable, created_on=timezone.now() - relativedelta(days=1))
        revision_2 = RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.seller)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)
        self.assertEqual(output.revision, revision_2)
        product.refresh_from_db()
        self.assertIn(output, product.samples.all())
        character.refresh_from_db()
        self.assertIsNone(character.primary_submission)

    def test_order_output_exists(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        revision = RevisionFactory.create(deliverable=deliverable)
        SubmissionFactory.create(deliverable=deliverable, owner=deliverable.order.buyer, revision=revision)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(deliverable.outputs.all().count(), 1)


class TestOrderInvite(APITestCase):
    def test_order_invite_no_buyer(self):
        deliverable = DeliverableFactory.create(order__buyer=None, order__customer_email='test@example.com')
        self.login(deliverable.order.seller)
        request = self.client.post(f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/invite/')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox[0].subject, f'You have a new invoice from {deliverable.order.seller.username}!')
        self.assertIn('This artist should', mail.outbox[0].body)

    def test_order_invite_buyer_not_guest(self):
        deliverable = DeliverableFactory.create(order__customer_email='test@example.com')
        self.login(deliverable.order.seller)
        request = self.client.post(f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/invite/')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_order_invite_buyer_guest(self):
        deliverable = DeliverableFactory.create(
            order__buyer__guest=True, order__buyer__guest_email='test@wat.com',
        )
        self.login(deliverable.order.seller)
        deliverable.order.customer_email = 'test@example.com'
        deliverable.order.save()
        request = self.client.post(f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/invite/')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox[0].subject, f'Claim Link for order #{deliverable.order.id}.')
        self.assertIn('resend your claim link', mail.outbox[0].body)
        deliverable.order.refresh_from_db()
        self.assertEqual(deliverable.order.buyer.guest_email, 'test@example.com')

    def test_order_invite_email_not_set(self):
        deliverable = DeliverableFactory.create(order__buyer=None, order__customer_email='')
        self.login(deliverable.order.seller)
        request = self.client.post(f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/invite/')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)


class TestReferences(APITestCase):
    def test_upload_reference(self):
        deliverable = DeliverableFactory.create()
        asset = AssetFactory.create(uploaded_by=deliverable.order.seller)
        self.login(deliverable.order.seller)
        response = self.client.post(f'/api/sales/v1/references/', {
            'file': asset.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_attach_reference(self):
        deliverable = DeliverableFactory.create(arbitrator=UserFactory.create())
        reference = ReferenceFactory.create(owner=deliverable.order.seller)
        self.login(deliverable.order.seller)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/references/',
            {'reference_id': reference.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        Subscription.objects.get(
            type=COMMENT,
            subscriber=deliverable.order.buyer,
            content_type=ContentType.objects.get_for_model(reference),
            object_id=response.data['reference']['id'],
        )
        Subscription.objects.get(
            type=COMMENT,
            subscriber=deliverable.order.seller,
            content_type=ContentType.objects.get_for_model(reference),
            object_id=response.data['reference']['id'],
        )
        Subscription.objects.get(
            type=COMMENT,
            subscriber=deliverable.arbitrator,
            content_type=ContentType.objects.get_for_model(reference),
            object_id=response.data['reference']['id'],
        )

    def test_list_references(self):
        deliverable = DeliverableFactory.create()
        deliverable.reference_set.add(ReferenceFactory.create(), ReferenceFactory.create(), ReferenceFactory.create())
        self.login(deliverable.order.buyer)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/references/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        # Should be unpaginated.
        self.assertNotIn('results', response.data)


class TestCreateDeliverable(APITestCase):
    def setUp(self):
        self.landscape = ServicePlanFactory.create(name='Landscape')

    def test_create_deliverable(self):
        old_deliverable = DeliverableFactory.create(
            order__seller__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            order__seller__service_plan=self.landscape,
            order__seller__service_plan_paid_through=(timezone.now() + relativedelta(days=5)).date(),
        )
        product = ProductFactory.create(
            expected_turnaround=2,
            task_weight=5,
            revisions=1,
            base_price=Money('3.00', 'USD'),
            user=old_deliverable.order.seller,
        )
        self.login(old_deliverable.order.seller)
        response = self.client.post(f'/api/sales/v1/order/{old_deliverable.order.id}/deliverables/', {
            'name': 'Boop',
            'completed': False,
            'price': '5.00',
            'details': 'wat',
            'task_weight': 3,
            'revisions': 3,
            'product': product.id,
            'rating': ADULT,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        deliverable = Deliverable.objects.get(id=response.data['id'])
        order = deliverable.order
        self.assertEqual(response.data['status'], PAYMENT_PENDING)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(order.private, False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['rating'], ADULT)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['revisions_hidden'])
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)

        deliverable = Deliverable.objects.get(id=response.data['id'])
        item = deliverable.invoice.line_items.get(type=ADD_ON)
        self.assertEqual(item.amount, Money('2.00', 'USD'))
        self.assertEqual(item.priority, 100)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        item = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(item.amount, Money('3.00', 'USD'))
        self.assertEqual(item.priority, 0)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        self.assertIsNone(order.claim_token)

    def test_create_deliverable_non_landscape(self):
        old_deliverable = DeliverableFactory.create(
            product__expected_turnaround=2,
            product__task_weight=5,
            product__revisions=1,
            product__base_price=Money('3.00', 'USD'),
            product__user__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            product__user__service_plan_paid_through=timezone.now() - relativedelta(days=5),
            product__user__service_plan=self.landscape,
        )
        self.login(old_deliverable.order.seller)
        response = self.client.post(f'/api/sales/v1/order/{old_deliverable.order.id}/deliverables/', {
            'name': 'Boop',
            'completed': False,
            'price': '5.00',
            'details': 'wat',
            'task_weight': 3,
            'rating': ADULT,
            'revisions': 3,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_deliverable_buyer_fail(self):
        old_deliverable = DeliverableFactory.create(
            product__expected_turnaround=2,
            product__task_weight=5,
            product__revisions=1,
            product__base_price=Money('3.00', 'USD'),
            product__user__artist_profile__bank_account_status=IN_SUPPORTED_COUNTRY,
            product__user__landscape_paid_through=timezone.now() + relativedelta(days=5),
        )
        self.login(old_deliverable.order.buyer)
        response = self.client.post(f'/api/sales/v1/order/{old_deliverable.order.id}/deliverables/', {
            'name': 'Boop',
            'completed': False,
            'price': '5.00',
            'details': 'wat',
            'task_weight': 3,
            'revisions': 3,
            'rating': ADULT,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestBroadcast(APITestCase):
    def test_no_orders(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(f'/api/sales/v1/account/{user.username}/broadcast/', {'text': 'Boop'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'You have no open orders to broadcast to.')

    def test_broadcast(self):
        deliverable = DeliverableFactory.create()
        self.login(deliverable.order.seller)
        deliverable2 = DeliverableFactory.create(order=deliverable.order)
        deliverable3 = DeliverableFactory.create(order__seller=deliverable.order.seller)
        deliverable4 = DeliverableFactory.create()
        response = self.client.post(
            f'/api/sales/v1/account/{deliverable.order.seller.username}/broadcast/', {'text': 'Boop'},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deliverable.comments.all().count() + deliverable2.comments.all().count(), 1)
        self.assertEqual(deliverable3.comments.all().count(), 1)
        comment = deliverable3.comments.all()[0]
        self.assertEqual(comment.text, 'Boop')
        self.assertEqual(comment.user, deliverable3.order.seller)
        self.assertEqual(deliverable4.comments.all().count(), 0)


class TestClearWaitlist(APITestCase):
    def test_clear_waitlist(self):
        deliverable = DeliverableFactory.create(status=WAITING)
        deliverable2 = DeliverableFactory.create(status=WAITING, product=deliverable.product)
        deliverable3 = DeliverableFactory.create(order__seller=deliverable.order.seller, status=WAITING)
        deliverable4 = DeliverableFactory.create(
            order__seller=deliverable.order.seller, product=deliverable.product, status=IN_PROGRESS,
        )
        deliverable5 = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/account/{deliverable.order.buyer.username}/products/{deliverable.product.id}/clear-waitlist/',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post(
            f'/api/sales/v1/account/{deliverable.product.user.username}/products/'
            f'{deliverable.product.id}/clear-waitlist/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.login(deliverable.product.user)
        response = self.client.post(
            f'/api/sales/v1/account/{deliverable.product.user.username}/products/'
            f'{deliverable.product.id}/clear-waitlist/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        for item in [deliverable, deliverable2, deliverable3, deliverable4, deliverable5]:
            item.refresh_from_db()
        self.assertEqual(deliverable.status, CANCELLED)
        self.assertEqual(deliverable2.status, CANCELLED)
        self.assertEqual(deliverable3.status, WAITING)
        self.assertEqual(deliverable4.status, IN_PROGRESS)
        self.assertEqual(deliverable5.status, COMPLETED)


class TestQueue(APITestCase):
    def test_queue_anonymous(self):
        deliverable = DeliverableFactory.create()
        response = self.client.get(f'/api/sales/v1/account/{deliverable.order.seller.username}/queue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAnonymousInvoice(APITestCase):
    def test_invoice_created(self):
        UserFactory.create(username=settings.ANONYMOUS_USER_USERNAME)
        user = UserFactory.create(is_staff=True)
        self.login(user)
        response = self.client.post('/api/sales/v1/create-anonymous-invoice/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_non_staff(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post('/api/sales/v1/create-anonymous-invoice/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestRecentInvoices(APITestCase):
    def test_show_recent(self):
        newest = InvoiceFactory.create(created_on=timezone.now().replace(year=2022, month=8, day=1), creates_own_transactions=True)
        oldest = InvoiceFactory.create(created_on=timezone.now().replace(year=2020, month=8, day=1), creates_own_transactions=True)
        middle = InvoiceFactory.create(created_on=timezone.now().replace(year=2021, month=8, day=1), creates_own_transactions=True)
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get('/api/sales/v1/recent-invoices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target_list = [newest.id, middle.id, oldest.id]
        self.assertEqual(target_list, [invoice['id'] for invoice in response.data['results']])

    def test_fail_non_staff(self):
        self.login(UserFactory.create())
        response = self.client.get('/api/sales/v1/recent-invoices/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
