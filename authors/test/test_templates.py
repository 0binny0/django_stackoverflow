
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from ..models import Profile
from posts.models import Question, Bookmark, Tag, Vote

class TestQuestionsBookmookedTemplate(TestCase):

    @classmethod
    def setUpTestData(cls):
        tag1 = Tag.objects.create(name="Tag1")
        user1 = get_user_model().objects.create_user("ItsMe")
        profile1 = Profile.objects.create(user=user1)
        user2 = get_user_model().objects.create_user("ItsYou")
        profile2 = Profile.objects.create(user=user2)

        question1 = Question.objects.create(
            title="This is Question 1 title",
            body="This is the content body of Question1",
            score=1,
            profile=profile1
        )
        question1.tags.add(tag1)

        b1 = Bookmark.objects.create(profile=profile2, question=question1)

        cls.template = render_to_string(
            "authors/bookmark.html", {'question': question1}
        )

    def test_bookmark_template_context(self):
        for text in ["This is Question 1 title", "1 vote", "0 answers", "Tag1", "ItsMe"]:
            with self.subTest(text=text):
                self.assertIn(text, self.template)
