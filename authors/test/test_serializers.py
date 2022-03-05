
from rest_framework.test import APISimpleTestCase
from rest_framework.exceptions import ValidationError

from ..validators import character_validator
from ..serializers import LoginSerializer

class TestCharacterValidator(APISimpleTestCase):
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


class TestLoginSerializerUsernameField(APISimpleTestCase):

    def setUp(self):
        self.username_strings1 = [
            "_This_is_me", "_This_is_me001_", "This_is_me_"
        ]

        self.username_strings2 = [
            "_____This_is_", "This_is_my_full_username", "WhoAm+"
        ]

    def test_validated_username_strings_pass(self):
        for string in self.username_strings1:
            with self.subTest(string=string):
                serializer = LoginSerializer(
                    data={"username": string}, partial=True
                )
                serializer.is_valid()
                self.assertEqual(
                    serializer.validated_data["username"],
                    string
                )

    def test_validated_username_strings_fail(self):
        for string in self.username_strings2:
            with self.subTest(string=string):
                import pdb; pdb.set_trace()
                serializer = LoginSerializer(
                    data={"username": string}, partial=True
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn("username", serializer.errors)
