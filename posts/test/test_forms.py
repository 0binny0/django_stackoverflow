
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
        self.assertFalse(self.tags_field.required)
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


class TestQuestionSubmissionTitleField(TestCase):
    """Verify that an error is raised when the title exceeds
    the maximum character limit."""

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user("TestUser")
        profile = Profile.objects.create(user=user)
        msg = "This is a very very very very very very very very long title"
        data = {
            'title': msg,
            'body': "The context to this post doesn't explain alot does it"
        }
        cls.form = QuestionForm(data)

    def test_invalid_question_title_length(self):
        import pdb; pdb.set_trace()
        self.assertFalse(self.form.is_valid())
        self.assertTrue(self.form.has_error("title"))
        self.assertEqual(
            self.form.errors.as_data()['title'][0].message,
            "The title of your question is too long"
        )


class TestQuestionSubmissionBodyField(TestCase):
    '''Verify that an error is raised when the content of the body
    field doesn\'t meet the minimum character limit.'''

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user("TestUser")
        profile = Profile.objects.create(user=user)
        data = {
            "title": "This is the question title",
            "body": "",
            "profile": profile
        }
        cls.form = QuestionForm(data)

    def test_question_body_field_no_content(self):
        self.assertFalse(self.form.is_valid())
        self.assertTrue(self.form.has_error("body"))
        self.assertEqual(
            self.form.errors.as_data()['body'][0].message,
            "Elaborate on your question"
        )
