import json, requests

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from django.test.client import Client

from cities_light.models import City, Country
from oauth2_provider.models import AccessToken, Application

from item.models import (
    Category,
    Item,
    Subcategory
)
from transaction.models import Notification, Transaction


class TransactionTest(LiveServerTestCase):
    """
    Class to test various transaction app-related backend and API processes
    """

    HEADERS = {"Content-type": "application/json", "Accept": "application/json"}

    def setUp(self):
        self.client = Client()

        # Create City to be added to User's UserProfile
        country = Country.objects.create(name="Philippines")
        City.objects.create(name="Davao", country=country)

        # Create dummy User and login using credentials
        self.user = User.objects.create(
            username='testuser',
            password='testpassword',
        )
        self.user2 = User.objects.create(
            username='user2',
            password='password2'
        )

        self.user = authenticate(username='testuser', password='testpassword')

        # Create new Application to retrieve Client ID and Client Secret
        self.application = Application.objects.create(
            name='TEST',
            user=self.user,
            client_type='public',
            authorization_grant_type='password'
        )

        # Setup requests to create an access token for dummy user
        payload = {
            'grant_type': "password",
            'username': "testuser",
            'password': "testpassword",
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret
        }

        requests.post("{}/oauth2/token/".format(self.live_server_url), data=payload)

        # Create dummy Category, Subcategory, and Item
        category = Category.objects.create(name='Sports Apparel')
        self.subcategory = Subcategory.objects.create(name='Basketball Shoes', parent_category=category)
        self.item = Item.objects.create(
            name='Jordan XX9',
            owner=self.user,
            price_range_minimum=5000,
            price_range_maximum=6500,
            subcategory=self.subcategory
        )
        self.item2 = Item.objects.create(
            name='Nike Kobe 9 EM & Elite',
            owner=self.user2,
            price_range_minimum=10000,
            price_range_maximum=15000,
            subcategory=self.subcategory
        )

    # Transaction tests
    def test_transaction_endpoint(self):
        """
        Test method to check if the Transaction view endpoint correctly connects and validates POST data.
        For this case, a correct data will be passed to the request

        Expected behavior: The response should return a "Transaction successful" text.
        """

        access_token = AccessToken.objects.get(user=self.user).token

        # POST data
        payload = {
            "user_item_id": self.item.id,
            "other_item_id": self.item2.id,
            "action_from_id": self.item2.owner.id
        }

        # Retrieve response data
        url = "{}/transaction/info/{}/".format(self.live_server_url, access_token)
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(payload))

        self.assertEqual("transaction_id" in response.json(), True)

    # Notification tests
    def test_notification_endpoint(self):
        """
        Test method to check if the Notifications view endpoint correctly connects and retrieves a list of
        notifications given the user's access token.

        Expected behavior: The response should return a dictionary with 'notifications' key-value pair.
        """

        access_token = AccessToken.objects.get(user=self.user).token

        # Retrieve response data
        url = "{}/transaction/notifications/{}".format(self.live_server_url, access_token)
        response = requests.get(url)

        response_data = response.content

        self.assertEqual("notifications" in response_data, True)

    def test_notification_action_endpoint(self):
        """
        Test method to check if the Notifications Action view endpoint is accessed correctly and performs a corresponding
        action given the POST request data.

        Expected behavior: The associated notification should be deleted; A new one will be created based on user action
        """

        # Creates a new transaction and its corresponding notification
        transaction = Transaction.objects.create(item1=self.item, item2=self.item2)
        notification = Notification.objects.create(
            notification='offered a Swapp with you.',
            recipient=User.objects.get(id=self.item2.owner.id),
            action_from=self.user,
            transaction=transaction
        )

        # POST data
        payload = {"notification_id": notification.id, "action": "accept"}

        # Retrieve response data
        self.HEADERS['Authorization'] = AccessToken.objects.get(user=self.user).token
        url = "{}/transaction/notification/action/".format(self.live_server_url)
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(payload))

        response_data = response.content

        # Retrieve new Notification instance
        action_notification = Notification.objects.last()

        condition = ((Notification.objects.get(id=notification.id) == None) and
                    (action_notification and action_notification.type == "accept"))

        self.assertEqual(condition, True)
