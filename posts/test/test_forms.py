
from datetime import date
from unittest.mock import Mock, patch


from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model

from ..forms import QuestionForm
from ..models import Question, Tag
from authors.models import Profile


class TestDuplicateQuestionSameDate(TestCase):
    '''Verify that a User cannot post a duplicate question
    on the same date.'''

    @classmethod
    def setUpTestData(cls):
        pass

    @patch("posts.models.date")
    def test_user_question_already_posted(self, mock_date):
        pass
