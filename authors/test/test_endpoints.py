
from django.http import QueryDict
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework.test import APITestCase


class TestRegisterEndpointUsernameAndPassword(APITestCase):
    '''Verify that a 400 status code is delivered to the client when
    an attempt is made to register an account with the same username
    and password
    '''

    @classmethod
    def setUpTestData(cls):
        query = QueryDict("username=TheBig001&password=TheBig001").urlencode()
        path = reverse("api_authors:register")
        cls.url = f"{path}?{query}"

    def test_invalid_username_and_password_combo_provided(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("password2", response.data)
        self.assertEqual(
            response.data["password2"][0],
            "password cannot be username"
        )


class TestRegisterEndpointFailedRegistration(APITestCase):
    '''Verify that a 400 status code is delivered to the client in the event
    that the same value is provided for an username, password, password
    confirmation.'''

    @classmethod
    def setUpTestData(cls):
        path = reverse("api_authors:register")
        query = QueryDict(
            "username=TheBig001&password=theBig001&password2=thebig001"
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


class TestRegisterEndpointPasswordMismatch(APITestCase):
    '''Verify that a 400 status code is delivered to the client in the event
    that the password confirmation and password fields do not match.'''

    @classmethod
    def setUpTestData(cls):
        path = reverse("api_authors:register")
        query = QueryDict("password=T0p$ecret&password2=T()pSecret").urlencode()
        cls.url = f"{path}?{query}"

    def test_password_fields_not_equal(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "password confirmation failed"
        )
