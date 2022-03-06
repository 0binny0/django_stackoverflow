
from django.contrib.auth import get_user_model

from rest_framework.test import APISimpleTestCase, APITestCase
from rest_framework.exceptions import ValidationError

from ..validators import character_validator
from ..serializers import LoginSerializer, RegisterSerializer


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


class TestRegisterSerializerUsernameField(APITestCase):
    '''Verify that a username can only take in lowercase letters,
    uppercase letters, up to 3 numbers, and single underscores.'''

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user("TestUser")
        cls.invalid_characters = "!@#$%^&*()-+={[]}:;\"'<,>.?/~`"
        cls.username_strings = [
            "_This_is_ME_", "_This_is_001ME", "This_is_ME_", "ThisisME",
            "This_is_N0Tme"
        ]

        cls.invalid_username_strings = [
            '____This_is__MEagain+', '000000h..ooo()o',
        ]

    def test_error_raised_invalid_characters_in_string(self):
        for char in self.invalid_characters:
            with self.subTest(char=char):
                serializer = RegisterSerializer(
                    data={"username": f"0h..ooo{char}o"}, partial=True
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn("username", serializer.errors)

    def test_error_raised_too_many_digits(self):
        serializer = RegisterSerializer(data={
            "username": "This_is_n00000_good"
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_username_string_valid_characters(self):
        for string in self.username_strings:
            with self.subTest(string=string):
                serializer = RegisterSerializer(
                    data={"username": string}, partial=True
                )
                self.assertTrue(serializer.is_valid())
                self.assertEqual(
                    serializer.validated_data['username'],
                    string
                )

    def test_register_username_already_taken(self):
        serializer = RegisterSerializer(
            data={"username": "TestUser"}, partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)


class TestRegisterSerializerPasswordField(APITestCase):
    '''Verify that a password cannot take in the following
    characters: <>`':;,.'''

    @classmethod
    def setUpTestData(cls):
        cls.invalid_characters = "<>`':;,.\""

    def test_validated_password_string_characters(self):
        for char in self.invalid_characters:
            with self.subTest(char=char):
                serializer = RegisterSerializer(
                    data={"password": f"secretC{char}od{char}"}
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn("password", serializer.errors)


class TestRegisterSerializerRegistrationFailed(APITestCase):
    '''Verify that an error is raised when the username,
    password, and password confirmation values are of the
    same value.'''

    @classmethod
    def setUpTestData(cls):
        cls.data = {
            "username": "Whoopsie",
            "password": "Whoopsie",
            "password2": "Whoopsie"
        }
        cls.serializer = RegisterSerializer(
            data=cls.data, partial=True
        )

    def test_duplicate_values_in_all_registration_fields(self):
        self.assertFalse(self.serializer.is_valid())
        self.assertEqual(
            str(self.serializer.errors['non_field_errors'][0]),
            "registration failed"
        )


class TestRegisterSerializerPasswordConfirmation(APITestCase):
    '''Verify that an error is raised when the password
    confirmation does not match the password entered in a
    registration form.'''

    @classmethod
    def setUpTestData(cls):
        cls.data = {
            "username": "Its_not_me_again",
            "password": "T()p$ecret",
            "password2": "T0pSecret"
        }
        cls.serializer = RegisterSerializer(
            data=cls.data, partial=True
        )

    def test_password_confirmation_fail(self):
        self.assertFalse(self.serializer.is_valid())
        self.assertIn(
            "password confirmation failed",
            str(self.serializer.errors["non_field_errors"][0])
        )
