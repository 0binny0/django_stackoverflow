
from datetime import date

from unittest.mock import Mock, patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Tag, Question
from authors.models import Profile

class TestQuestionManager(TestCase):
    '''Verify that the QuestionSearchManager returns QuerySets
    based on tags contained in a User's questions and date duration'''
    fixtures = ["postings.json", ]

    @classmethod
    def setUpTestData(cls):
        cls.profile = Profile.objects.get(id=3)

    def test_questions_selected_within_week(self):
        with patch("posts.models.date") as mock_date:
            mock_date.today = Mock(return_value=date(2022, 2, 15))
            questions = Question.postings.by_week(self.profile)
        self.assertEqual(questions.count(), 2)
        self.assertQuerysetEqual(
            questions, [
                "Question(title=Question__005)",
                "Question(title=Question__006)"
            ], transform=repr
        )

    def test_all_questions_selected_within_month(self):
        with patch("posts.models.date") as mock_date:
            mock_date.today = Mock(return_value=date(2022, 2, 15))
            questions = Question.postings.by_month(self.profile)
        self.assertEqual(questions.count(), 3)
        self.assertQuerysetEqual(
            questions, [
                "Question(title=Question__005)",
                "Question(title=Question__006)",
                "Question(title=Question__003)",
            ], transform=repr
        )

    def test_all_questions_selected_past_few_days(self):
        with patch("posts.models.date") as mock_date:
            mock_date.today = Mock(return_value=date(2022, 2, 15))
            questions = Question.postings.recent(self.profile)
        self.assertEqual(questions.count(), 2)
        self.assertQuerysetEqual(
            questions, [
                "Question(title=Question__005)",
                "Question(title=Question__006)",
            ], transform=repr
        )

    def test_all_newest_questions_selected(self):
        questions = Question.postings.all()
        newest_question = questions.first()
        last_question = questions.last()
        self.assertEqual(questions.count(), 7)
        self.assertEqual(newest_question.date, date(2022, 2, 12))
        self.assertEqual(last_question.date, date(2021, 1, 13))

    def test_all_unanswered_questions_by_user_tags(self):
        questions = Question.postings.unanswered()
        self.assertEqual(questions.count(), 3)
        self.assertQuerysetEqual(
            questions, [
                "Question(title=Question__005)",
                "Question(title=Question__007)",
                "Question(title=Question__003)",
            ], transform=repr
        )
