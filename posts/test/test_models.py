
from datetime import date

from unittest.mock import Mock, patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Tag, Question
from authors.models import Profile

class TestQuestiongManager(TestCase):
    fixtures = ["postings.json", ]

    @classmethod
    def setUpTestData(cls):
        profile = Profile.objects.get(id=2)
        with patch("posts.models.date") as mock_date:
            mock_date.today = Mock(return_value=date(2022, 2, 15))
            cls.questions = Question.postings.by_week(profile)

    def test_all_questions_selected_related_to_tags(self):
        self.assertEqual(self.questions.count(), 2)
        self.assertQuerysetEqual(
            self.questions, [
                "Question(title=Question__005)",
                "Question(title=Question__006)"
            ], transform=repr, msg="""
                The question queryset includes questions with
                tags that aren't associated with any question
                posted by a given user
            """
        )
