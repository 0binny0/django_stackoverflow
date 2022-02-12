
from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Tag, Question
from authors.models import Profile

class TestQuestiongManager(TestCase):
    fixtures = ["./fixtures/postings.json", ]

    @classmethod
    def setUpTestData(cls):
        profile = Profile.objects.get(id=2)
        cls.questions = Question.postings.by_week(profile)

    def test_all_questions_selected_related_to_tags(self):
        self.assertEqual(self.question.count(), 2)
        self.assertQuerySetEqual(
            self.questions, [
                "Question(title=Question 5)",
                "Question(title=Question 1)"
            ], transform=repr, msg="""
                The question queryset includes questions with
                tags that aren't associated with any question
                posted by a given user
            """
        )
