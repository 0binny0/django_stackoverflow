
from datetime import date
from unittest.mock import Mock, patch


from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model
from django.forms.widgets import TextInput

from ..forms import QuestionForm
from ..models import Question, Tag
from authors.models import Profile


class TestQuestionFormCustomTagsField(SimpleTestCase):
    '''Verify that the widget used for the tags field
    is a TextInput and is not required.'''

    def setUp(self):
        form = QuestionForm()
        self.tags_field = form['tags'].field

    def test_custom_tags_widget(self):
        self.assertIsInstance(self.tags_field.widget, TextInput)
        self.assertFalse(self.tags_field.widget.attrs['required'])
