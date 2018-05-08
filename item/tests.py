import base64, json, requests
from datetime import datetime

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
from item.utils import distance_on_unit_sphere


class ItemTest(LiveServerTestCase):
    """
    Class to test various item app-related backend and API processes
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
            subcategory=self.subcategory,
            latitude=80.0,
            longitude=80.0,
        )
        self.item2 = Item.objects.create(
            name='Nike Kobe 9 EM & Elite',
            owner=self.user,
            price_range_minimum=10000,
            price_range_maximum=15000,
            subcategory=self.subcategory,
            latitude=100.0,
            longitude=100.0,
        )

    # Item Detail view tests
    def test_item_detail_view_endpoint_200(self):
        """
        Test method to check if the Item Detail view endpoint correctly connects and returns the Item's
        data as JSON

        Expected behavior: response.json() should contain item's details
        """

        # Retrieve response data
        url = "{}/item/entry/{}".format(self.live_server_url, self.item.id)
        response = requests.get(url)

        item_data = response.json()

        self.assertEqual(item_data.get('name'), self.item.name)


    def test_item_list_endpoint_200(self):
        """
        Test method to check if the endpoint for Item List correctly connects and returns the List of Items as JSON

        Expected behavior: response.json() should contain a list of item details
        """

        # Retrieve response data
        access_token = AccessToken.objects.get(user=self.user)

        url = "{}/item/entry/list/{}".format(self.live_server_url, access_token.token)
        response = requests.get(url)

        item_list = response.json()

        self.assertEqual(response.status_code, 200)

    # Item Add view tests
    def test_item_add_endpoint(self):
        """
        Test method to check if the endpoint for Item Add correctly connects and creates a new Item instance given the
        provided JSON data

        Expected behavior: response.json() should contain the newly created item's details
        """

        access_token = AccessToken.objects.get(user=self.user)

        # POST data
        payload = {
            "name": "Jordan Super.Fly 3",
            "owner": self.user.id,
            "price_range_minimum": 8000,
            "price_range_maximum": 8500,
            "subcategory": self.subcategory.id
        }

        # Retrieve response data
        url = "{}/item/entry/add/{}/".format(self.live_server_url, access_token.token)
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(payload))

        item_data = response.json()
        self.assertEqual(item_data.get('name'), payload.get('name'))

    # Item Delete view tests
    def test_item_delete_endpoint(self):
        """
        Test method to check if the endpoint for Item Delete correctly connects and deletes an Item instance given the
        provided item's id

        Expected behavior: response.json() should output to "Successfully deleted"
        """

        url = "{}/item/entry/delete/{}/".format(self.live_server_url, self.item.id)
        response = requests.post(url)

        self.assertEqual(response.json(), "Successfully deleted")

    def test_distance_on_unit_sphere(self):
        """
        Test method to compute for distances between two location points

        Expected behavior: Output of function be equal to theoretical distance
        """

        point1 = (7.070963, 125.606439, "Ingenuity Global Consulting")
        point2 = (7.016807, 125.493731, "Gaisano Mall of Toril")

        theoretical_result = (8.589454860633648, 13.82338278455006)
        actual_result = distance_on_unit_sphere(point1[0], point1[1], point2[0], point2[1])

        self.assertEqual(theoretical_result, actual_result)

    def test_item_conflict_check_200(self):
        """
        Test method to check if the endpoint for Checking for Location Conflict would return True
        if there are existing location conflicts

        Expected behavior: response.json() should be "True"
        """

        self.HEADERS['Authorization'] = AccessToken.objects.get(user=self.user).token
        url = "{}/item/conflict/check/".format(self.live_server_url)
        response = requests.get(url, headers=self.HEADERS)

        self.assertEqual(response.json(), "True")

    def test_item_conflict_resolve_200(self):
        """
        Test method to check if the endpoint for Item Delete correctly connects and deletes an Item instance given the
        provided item's id

        Expected behavior: response.json() should output to "Successfully deleted"
        """

        self.HEADERS['Authorization'] = AccessToken.objects.get(user=self.user).token
        url = "{}/item/conflict/resolve/".format(self.live_server_url)
        response = requests.get(url, headers=self.HEADERS)

        self.assertEqual(response.json(), "Conflict successfully resolved")

