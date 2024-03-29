
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APISimpleTestCase, APITestCase, APIClient

from ..models import Question, Tag, Vote, Bookmark
from authors.models import Profile

class LoggedInAPIClient(APIClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.credentials(**kwargs)


class APIStateTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(
            username="MainUser", password="mypassword"
        )
        cls.profile = Profile.objects.create(user=cls.user1)
        cls.user2 = get_user_model().objects.create_user(
            username="adummy101", password="nuclearsecrets"
        )
        cls.profile2 = Profile.objects.create(user=cls.user2)
        cls.tag = Tag.objects.create(name="Tag1")
        cls.question = Question.objects.create(
            title="Test Dummy Question",
            body="This is post content about question 'Test Dummy Question'",
            profile=cls.profile
        )
        cls.question.tags.add(cls.tag)

class TestUserVoteEndpointNewVote(APIStateTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.client = LoggedInAPIClient(
            HTTP_ACCEPT="application/json",
            CONTENT_TYPE="application/json"
        )


    def test_user_vote_on_new_question(self):
        self.client.login(username="adummy101", password="nuclearsecrets")
        response = self.client.put(
            reverse("api_posts:post", kwargs={"id": 1}),
            data={"type": "up", "post": "question"}
        )
        self.assertEqual(response.status_code, 204)


class TestUserVoteEndpointChangedVote(APIStateTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Vote.objects.create(profile=cls.profile2, type="down", content_object=cls.question)
        cls.client = LoggedInAPIClient(
            HTTP_ACCEPT="application/json",
            CONTENT_TYPE="application/json"
        )

    def test_user_changed_vote_from_positive_to_negative(self):
        self.client.login(username="adummy101", password="nuclearsecrets")
        response = self.client.put(
            reverse("api_posts:post", kwargs={"id": 1}),
            data={"type": "up", "post": "question"}
        )
        self.assertEqual(response.status_code, 204)


# class TestUserVoteEndpointDuplicateVote(APIStateTestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         super().setUpTestData()
#         Vote.objects.create(profile=cls.profile2, type="down", content_object=cls.question)
#         cls.client = LoggedInAPIClient(
#             HTTP_ACCEPT="application/json",
#             CONTENT_TYPE="application/json"
#         )
#
#     def test_user_duplicate_vote_type_disallowed(self):
#         self.client.login(username="adummy101", password="nuclearsecrets")
#         response = self.client.post(
#             reverse("api_posts:posts", kwargs={"id": 1}),
#             data={"type": "down", "post": "question"}
#         )
#         self.assertEqual(response.status_code, 400)

class TestUserVoteEndpointVoteOnOwnPost(APIStateTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.client = LoggedInAPIClient(
            HTTP_ACCEPT="application/json",
            CONTENT_TYPE="application/json"
        )

    def test_user_vote_on_own_question(self):
        self.client.login(username="MainUser", password="mypassword")
        response = self.client.post(
            reverse("api_votes:vote", kwargs={"id": 1}),
            data={"type": "down", "post": "question"}
        )
        self.assertEqual(response.status_code, 400)


class TestUserVoteEndpointUserDeletesPost(APIStateTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Vote.objects.create(
            profile=cls.profile,
            type="up",
            content_object=cls.question
        )

    def test_user_question_deleted_vote(self):
        self.client.login(username="MainUser", password="mypassword")
        response = self.client.delete(
            f"{reverse('api_posts:post', kwargs={'id': 1})}?post=question"
        )
        self.assertEqual(response.status_code, 204)


class TestUserVoteEndpointGetExistingVotes(APIStateTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Vote.objects.create(
            profile=cls.profile2,
            type="up",
            content_object=cls.question
        )
        Bookmark.objects.create(profile=cls.profile2, question=cls.question)

    def test_get_vote_state_upon_viewing_post(self):
        self.client.login(username="adummy101", password="nuclearsecrets")
        response = self.client.get(
            f"{reverse('api_votes:vote', kwargs={'id': 1})}?post=question"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], "application/json")
        self.assertEqual(
            response.data, {
                'question_id': 1, 'vote': "up", "bookmark": True,
                "answers": None
            }
        )


class TestAnonymousUserVoteAttempt(APISimpleTestCase):

    def test_warn_user_to_login_to_vote(self):
        response = self.client.post(reverse(
            "api_votes:vote", kwargs={"id": 1}
        ), data={"type": "dislike", "post": "question"})
        self.assertEqual(response.status_code, 400)


class TestUserPostDeleted(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(
            username="ItsMe", password="secretclearance"
        )
        profile = Profile.objects.create(user=user)
        tag = Tag.objects.create(name="Tag1")
        question = Question.objects.create(
            title="This is a title about the subject post",
            body="This is content that elaborates upon the the subject title",
            profile=profile
        )
        question.tags.add(tag)
        cls.url = f"{reverse('api_posts:post', kwargs={'id': 1})}?post=question"

    def test_deleted_post_response(self):
        self.client.login(username="ItsMe", password="secretclearance")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
