import json, requests
from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from django.test.client import Client

from cities_light.models import City, Country
from oauth2_provider.models import AccessToken, Application


class UserTest(LiveServerTestCase):
    """
    Class to test various user_profile app-related backend and API processes
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

    # Signup tests
    def test_signup_view_endpoint_201(self):
        """
        Test method to check if the Signup view endpoint correctly connects and validates POST data.
        For this case, a correct data will be passed to the request

        Expected behavior: The response should return a 201 status code
        """

        # POST data
        payload = {
            "first_name": "Some",
            "last_name": "User",
            "email": "some@gmail.com",
            "username": "someuser",
            "password": "pass"
        }

        # Retrieve response data
        url = "{}/user/signup/".format(self.live_server_url)
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(payload))

        self.assertEqual(response.status_code, 201)

    def test_signup_view_endpoint_400(self):
        """
        Test method to check if the Signup view endpoint correctly connects and validates POST data.
        For this case, an invalid/incomplete data will be purposely passed to the request

        Expected behavior: The response should return a 400 status code
        """

        # POST data
        payload = {
            "first_name": "Another",
            "last_name": "User",
        }

        # Retrieve response data
        url = "{}/user/signup/".format(self.live_server_url)
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(payload))

        self.assertEqual(response.status_code, 400)

    def test_userprofile_view_endpoint_200(self):
        """
        Test method to check if the UserProfile view endpoint correctly connects and returns user's GET information.

        Expected behavior: The response should return a 200 status code
        """

        access_token = AccessToken.objects.get(user=self.user)

        url = "{}/user/profile/{}".format(self.live_server_url, access_token.token)
        response = requests.get(url)

        self.assertEqual(response.status_code, 200)

    def test_userprofile_view_endpoint_401(self):
        """
        Test method to check if the UserProfile view endpoint correctly connects and returns user's GET information.
        For this case, no `identifier` will be provided to the request.

        Expected behavior: The response should return a 401 status code
        """

        access_token = AccessToken.objects.get(user=self.user)

        url = "{}/user/profile/{}".format(self.live_server_url, "")
        response = requests.get(url)

        self.assertEqual(response.status_code, 401)

    def test_change_password_200(self):
        """
        Test method to check if the endpoint for Change Password correctly modifies the user's password.

        Expected behavior: The response should return a 200 status code
        """

        access_token = AccessToken.objects.get(user=self.user)

        url = "{}/user/change_password/{}/".format(self.live_server_url, access_token.token)

        # POST data
        password_load = {
            "old_password": "testpassword",
            "new_password": "testpassword2",
        }

        self.HEADERS['Authorization'] = access_token

        # Retrieve response data
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(password_load), allow_redirects=False)

        self.assertEqual(response.status_code, 200)

    def test_change_location_200(self):
        """
        Test method to check if the endpoint for Change Password correctly modifies the user's password.

        Expected behavior: The response should return a 200 status code
        """

        access_token = AccessToken.objects.get(user=self.user)

        url = "{}/user/change_location/{}/".format(self.live_server_url, access_token.token)

        # POST data
        password_load = {
            "latitude": 3.141516,
            "longitude": -102.987654,
        }

        self.HEADERS['Authorization'] = access_token

        # Retrieve response data
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(password_load), allow_redirects=False)

        self.assertEqual(response.status_code, 200)