
from unittest.mock import Mock, MagicMock

from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIRequestFactory

from ..models import Tag, Question, Vote, Answer, Bookmark
from ..serializers import VoteSerializer, CurrentPostStateSerializer
from authors.models import Profile



class TestDuplicateUserVoteNotAllowed(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.voter = get_user_model().objects.create_user(username="main")
        voter_profile = Profile.objects.create(user=cls.voter)
        poster = get_user_model().objects.create_user(username="author")
        poster_profile = Profile.objects.create(user=poster)
        cls.question = Question.objects.create(
            title="This is a question about Django APITestCases",
            body="This is content that elaborates on the title provided to this question",
            profile=poster_profile
        )
        cls.user_vote = Vote.objects.create(
            profile=voter_profile, type="down", content_object=cls.question
        )
        cls.question.vote.add(cls.user_vote)


    def test_duplicate_user_vote_disallowed(self):
        data = {
            'type': "down",
            'resource': 'questions/1/'
        }
        request = Mock()
        request.configure_mock(**{'user': self.voter})
        serializer = VoteSerializer(instance=self.question, data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

class TestChangedUserVote(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.voter = get_user_model().objects.create_user(username="main")
        voter_profile = Profile.objects.create(user=cls.voter)
        poster = get_user_model().objects.create_user(username="author")
        poster_profile = Profile.objects.create(user=poster)
        cls.question = Question.objects.create(
            title="This is a question about Django APITestCases",
            body="This is content that elaborates on the title provided to this question",
            profile=poster_profile
        )
        cls.user_vote = Vote.objects.create(
            profile=voter_profile, type="down", content_object=cls.question
        )
        cls.question.vote.add(cls.user_vote)
        cls.request = Mock()
        cls.request.configure_mock(**{'user': cls.voter})

    def test_changed_user_vote_successful(self):
        serializer = VoteSerializer(
            instance=self.question, data={'type': 'up'},
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())

# class TestUserDuplicateQuestionVote(APITestCase):
#     '''Verify that a User cannot duplicate an upvote
#     or a downvote.'''
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.voter = get_user_model().objects.create_user(username="main")
#         voter_profile = Profile.objects.create(user=cls.voter)
#         poster = get_user_model().objects.create_user(username="author")
#         poster_profile = Profile.objects.create(user=poster)
#         question = Question.objects.create(
#             title="This is a question about Django APITestCases",
#             body="This is content that elaborates on the title provided to this question",
#             profile=poster
#         )
#         cls.user_vote = Vote.objects.create(
#             profile=voter_profile, type="downvote", content_object=question
#         )
#         question.vote.add(cls.user_vote)
#         cls.client = Client(enforce_csrf_checks=True)
#
#     def test_user_cannot_downvote_on_question(self):
#         self.client.force_login(self.voter)
#         response = self.client.post(
#             reverse("api_posts:question", kwargs={'id': 1}),
#             data={"type": "downvote"},
#             headers={
#                 "Accept": "application/json",
#                 "Content-Type": "application/json"
#             }
#         )
#         self.assertEqual(response.status, 400)
#
#

class PageStateTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user("ItsMe")
        cls.profile1 = Profile.objects.create(user=cls.user1)
        cls.user2 = get_user_model().objects.create_user("ItsNotYou")
        cls.profile2 = Profile.objects.create(user=cls.user2)
        cls.user3 = get_user_model().objects.create_user("ItsNoOne")
        cls.profile3 = Profile.objects.create(user=cls.user3)
        cls.question = Question.objects.create(
            title="How can the output of a Serializer be changed?",
            body="I have to change the keys when data is serialized. How do I do that?",
            profile=cls.profile3
        )
        cls.answer1 = Answer.objects.create(
            body="To change the serialized output, override the 'to_representation' method",
            profile=cls.profile1,
            question=cls.question
        )

        Vote.objects.create(
            profile=cls.profile2,
            content_object=cls.answer1,
            type="up"
        )

        cls.request = APIRequestFactory().request()
        cls.request.user = cls.user2

        cls.serializer = CurrentPostStateSerializer(
            cls.question, context={'request': cls.request}
        )


class TestPageSerializerOutputAnswersOnly(PageStateTestCase):
    '''Verify that a list of dictionaries are returned where each
    dictionary references an answer that a user has voted on.
    '''

    def test_serializer_to_representation_output(self):
        self.assertEqual(
            self.serializer.data, {
                "question_id": 1, "vote": False, "bookmark": False,
                "answers": [
                    {'id': 1, 'vote': 'up'}
                ]
            }
        )


class TestPageSerializerVotedOnQuestionAndBookmarked(PageStateTestCase):
    '''Verify that a dictionary is created that shows that a question
    is voted on, an answer is voted on, and the question was bookmarked'''
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Vote.objects.create(
            profile=cls.profile2,
            content_object=cls.question,
            type="down"
        )
        Bookmark.objects.create(
            profile=cls.profile2,
            question=cls.question
        )

        cls.serializer = CurrentPostStateSerializer(
            cls.question, context={'request': cls.request}
        )

    def test_serializer_to_representation_output(self):
        self.assertEqual(
            self.serializer.data, {
                'question_id': 1, 'vote': "down", "bookmark": True,
                "answers": [{'id': 1, "vote": "up"}]
            }
        )
