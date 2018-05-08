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
from message.models import Message, Thread
from transaction.models import Transaction


class MessageTest(LiveServerTestCase):
    """
    Class to test various message app-related backend and API processes
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

        # Create dummy Category, Subcategory, Item, Transaction, and Thread
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
            owner=self.user,
            price_range_minimum=10000,
            price_range_maximum=15000,
            subcategory=self.subcategory
        )
        self.transaction = Transaction.objects.create(
            item1=self.item, item2=self.item2
        )
        self.thread = Thread.objects.create(
            sender=self.user,
            receiver=self.user2,
            transaction=self.transaction
        )


    def test_threads_list_endpoint(self):
        """
        Test method to check if the Threads list endpoint is accessed correctly.

        Expected behavior: The response should return a dictionary which contains the `threads` key-value pair.
        """

        access_token = AccessToken.objects.get(user=self.user).token

        url = "{}/message/threads/{}/".format(self.live_server_url, access_token)
        response = requests.get(url)

        response_data = response.content

        self.assertEqual("threads" in response_data, True)

    def test_create_thread_endpoint(self):
        """
        Test method to check if the Thread create endpoint is accessed correctly.

        Expected behavior: The response should return a dictionary which contains
        the `thread` and `current_user` key-value pair.
        """

        access_token = AccessToken.objects.get(user=self.user).token
        self.HEADERS.update({"HTTP_AUTHORIZATION": "Bearer {}".format(access_token)})

        # POST data
        payload = {'transaction_id': self.transaction.id}

        url = "{}/message/thread/new/".format(self.live_server_url)
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(payload))

        response_data = response.content

        self.assertEqual("thread" in response_data and "current_user" in response_data, True)

    def test_send_message_endpoint(self):
        """
        Test method to check if the Send message endpoint is accessed correctly.
        A test POST data will be passed to the endpoint to check if a message is created

        Expected behavior: The first Message instance should not equate to None.
        """

        # POST data
        payload = {
            "thread": self.thread.id,
            "sender": self.user.id,
            "receiver": self.user2.id,
            "text": "Sample Text"
        }

        # Retrieve response data
        url = "{}/message/send/".format(self.live_server_url)
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(payload))

        # Query first message instance
        message = Message.objects.first()

        self.assertNotEqual(message, None)
