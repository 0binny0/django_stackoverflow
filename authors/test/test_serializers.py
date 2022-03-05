
from django.contrib.auth import get_user_model

from rest_framework.test import APISimpleTestCase, APITestCase
from rest_framework.exceptions import ValidationError

from ..validators import character_validator
from ..serializers import LoginSerializer


class TestCharacterValidator(APITestCase):
    '''Verify that a ValidationError is raised based on whether a string
    contains characters that are not letters, numbers, and single underscores'''

    def setUp(self):
        self.invalid_characters = "!@#$%^&*()-+={[]}:;\"'<,>.?/`~"

    def test_invalid_character_provided(self):
        for character in self.invalid_characters:
            with self.subTest(character=character):
                string = f"IamTHE{character}man"
                msg = "invalid character found"
                with self.assertRaises(ValidationError, msg=msg):
                    character_validator(string)


class TestLoginSerializerUsernameField(APITestCase):

    def setUp(self):
        self.username_strings1 = [
            "_This_is_me", "_This_is_me001_", "This_is_me_"
        ]

        self.username_strings2 = [
            "_____This_is_", "This_is_my_full_username", "WhoAm+"
        ]

    def test_validated_username_strings_fail(self):
        for string in self.username_strings1:
            with self.subTest(string=string):
                serializer = LoginSerializer(
                    data={"username": string}, partial=True
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn("username", serializer.errrors)


    def test_validated_username_strings_fail(self):
        for string in self.username_strings2:
            with self.subTest(string=string):
                serializer = LoginSerializer(
                    data={"username": string}, partial=True
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn("username", serializer.errors)


class TestLoginSerializerPassword(APITestCase):
    '''Verify that a ValidationError is raised when the password
    provided upon a login attempt is not the password used
    to register'''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="MainUser", password="s3cretC0de"
        )
        cls.serializer = LoginSerializer(
            data={"username": "MainUser", "password": "secretCode"}
        )


    def test_user_signin_password_correct(self):
        self.assertFalse(self.serializer.is_valid())
        self.assertIn("password", self.serializer.errors)
