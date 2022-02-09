
from django.test import SimpleTestCase, TestCase

from django.contrib.auth import get_user_model

class TestCustomUsernameUniqueness(SimpleTestCase):

    def setUp(self):
        user = get_user_model()
        self.unique_error_message = (
            user._meta.get_field("username").error_messages['unique']
        )

    def test_username_uniqueness_error(self):
        self.assertEqual(self.unique_error_message, "Username not available")
