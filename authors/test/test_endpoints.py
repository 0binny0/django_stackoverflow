
from django.http import QueryDict
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase


class TestAccountsEndpointRegisterUsernameAndPassword(APITestCase):
    '''Verify that a 400 status code is delivered to the client when
    an attempt is made to register an account with the same username
    and password
    '''

    @classmethod
    def setUpTestData(cls):
        query = QueryDict(
            "username=TheBig001&password=TheBig001&action=register"
        ).urlencode()
        path = reverse("api_authors:main")
        cls.url = f"{path}?{query}"

    def test_invalid_username_and_password_combo_provided(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "password cannot be username"
        )


class TestAccountsEndpointFailedRegistration(APITestCase):
    '''Verify that a 400 status code is delivered to the client in the event
    that the same value is provided for an username, password, password
    confirmation.'''

    @classmethod
    def setUpTestData(cls):
        path = reverse("api_authors:main")
        query = QueryDict(
            "username=TheBig001&password=theBig001&password2=thebig001&action=register"
        ).urlencode()
        cls.url = f"{path}?{query}"

    def test_registeration_same_field_values(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            "registration failed",
            response.data["non_field_errors"][0]
        )


class TestAccountsEndpointRegisterPasswordMismatch(APITestCase):
    '''Verify that a 400 status code is delivered to the client in the event
    that the password confirmation and password fields do not match.'''

    @classmethod
    def setUpTestData(cls):
        path = reverse("api_authors:main")
        query = QueryDict(
            "password=T0p$ecret&password2=T()pSecret&action=register"
        ).urlencode()
        cls.url = f"{path}?{query}"

    def test_password_fields_not_equal(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "password confirmation failed"
        )


class TestAccountsEndpointNoLoginExists(APITestCase):
    '''Verify that a 400 status code is delivered to the client when
    an attempt is made to login with a username that is not issued.'''

    @classmethod
    def setUpTestData(cls):
        path = reverse("api_authors:main")
        query = QueryDict(
            "username=T00_much_&password=mya((ess&action=login"
        ).urlencode()
        cls.url = f"{path}?{query}"

    def test_username_provided_with_no_account(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)
        self.assertEqual(
            response.data['username'][0],
            "No account registered with that username"
        )


class TestAccountsEndpointLoginIncorrectPassword(APITestCase):
    '''Verify that a 400 status code is delivered to the client
    when the password provided for a given account is not the correct
    password.'''

    @classmethod
    def setUpTestData(cls):
        user_data = {
            "username": "Its_me_again",
            "password": "crackMy_c0de"
        }
        get_user_model().objects.create_user(**user_data)
        path = reverse("api_authors:main")
        query = QueryDict(
            "username=Its_me_again&password=whoopsie&action=login"
        ).urlencode()
        cls.url = f"{path}?{query}"

    def test_incorrect_user_password_entered(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)
        self.assertEqual(
            response.data['password'][0],
            "Password mismatch"
        )


class TestAccountsEndpointLoginSuccess(APITestCase):
    '''Verify that a 200 status code is sent to client when
    the login credentials are assigned to an existing user.'''

    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(
            username="Its_me_again", password="PowerMode"
        )
        path = reverse("api_authors:main")
        query = QueryDict(
            "username=Its_me_again&password=PowerMode&action=login"
        ).urlencode()
        cls.url = f"{path}?{query}"

    def test_valid_user_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
