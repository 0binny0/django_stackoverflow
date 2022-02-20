
from datetime import date
from unittest.mock import Mock, patch


from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model
from django.forms.widgets import TextInput, Textarea

from ..forms import QuestionForm
from ..models import Question, Tag
from authors.models import Profile


class TestCustomQuestionFormFields(SimpleTestCase):

    def setUp(self):
        form = QuestionForm()
        self.tags_field = form['tags'].field
        self.body_field = form['body'].field

        self.body_errors = [
            ("required", "Elaborate on your question"),
            ("min_length", "Add more info to your question")
        ]

    def test_custom_tags_field(self):
        self.assertIsInstance(self.tags_field.widget, TextInput)
        self.assertFalse(self.tags_field.widget.attrs['required'])
        self.assertEqual(
            self.tags_field.help_text,
            "Add up to 4 tags for your question"
        )

    def test_custom_body_field(self):
        self.assertIsInstance(self.body_field.widget, Textarea)
        self.assertEqual(self.body_field.min_length, 50)
        for error in self.body_errors:
            with self.subTest(error=error):
                key, error_msg = error
                self.assertEqual(
                    self.body_field.error_messages[key],
                    error_msg
                )
