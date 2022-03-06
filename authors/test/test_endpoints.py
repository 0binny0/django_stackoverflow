
from django.http import QueryDict
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework.test import APITestCase


class TestRegisterEndpointPasswordConfirmation(APITestCase):
    '''Verify that a 400 status code is delivered to the client when
    an attempt is made to register an account with the same username
    and password
    '''

    @classmethod
    def setUpTestData(cls):
        query = urlencode(QueryDict("username=TheBig001&password=TheBig001"))
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
