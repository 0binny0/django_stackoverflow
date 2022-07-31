
from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model

from posts.models import Question, Tag
from ..models import Profile

class TestCustomUsernameUniqueness(SimpleTestCase):

    def setUp(self):
        user = get_user_model()
        self.unique_error_message = (
            user._meta.get_field("username").error_messages['unique']
        )

    def test_username_uniqueness_error(self):
        self.assertEqual(self.unique_error_message, "Username not available")


class TestProfilePostedManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("ItsMe")
        profile = Profile.objects.create(user=cls.user)

        tag1 = Tag.objects.create(name="TagA")
        tag2 = Tag.objects.create(name="TagB")
        tag3 = Tag.objects.create(name="TagZ")

        question1 = Question.objects.create(
            title="This is a title about question1",
            body="This is the post content about question1",
            score=17,
            profile=profile
        )
        question1.tags.add(tag3)

        question2 = Question.objects.create(
            title="This is a title about question2",
            body="This is the post content about question2",
            score=12,
            profile=profile
        )
        question2.tags.add(*[tag1, tag3])

        question3 = Question.objects.create(
            title="This is a title about question3",
            body="This is the post content about question3",
            profile=profile
        )
        question3.tags.add(tag2)

        cls.records, cls.title = profile.get_tag_posts().values()

    def test_user_posted_tag_queryset(self):
        self.assertEqual(self.title, "3 Tags")
        self.assertQuerysetEqual(
            self.records, ["TagA", "TagB", "TagZ"], transform=str
        )
