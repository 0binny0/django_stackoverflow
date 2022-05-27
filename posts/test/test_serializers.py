
from unittest.mock import Mock

from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from ..models import Tag, Question, Vote
from ..serializers import VoteSerializer
from authors.models import Profile



class TestDuplicateUserVoteNotAllowed(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.voter = get_user_model().objects.create_user(username="main")
        voter_profile = Profile.objects.create(user=cls.voter)
        poster = get_user_model().objects.create_user(username="author")
        poster_profile = Profile.objects.create(user=poster)
        question = Question.objects.create(
            title="This is a question about Django APITestCases",
            body="This is content that elaborates on the title provided to this question",
            profile=poster_profile
        )
        cls.user_vote = Vote.objects.create(
            profile=voter_profile, type="down", content_object=question
        )
        question.vote.add(cls.user_vote)


    def test_duplicate_user_vote_disallowed(self):
        data = {
            'type': "down",
            'resource': 'questions/1/'
        }
        request = Mock()
        request.configure_mock(**{'user': self.voter})
        serializer = VoteSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

class TestChangedUserVote(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.voter = get_user_model().objects.create_user(username="main")
        voter_profile = Profile.objects.create(user=cls.voter)
        poster = get_user_model().objects.create_user(username="author")
        poster_profile = Profile.objects.create(user=poster)
        question = Question.objects.create(
            title="This is a question about Django APITestCases",
            body="This is content that elaborates on the title provided to this question",
            profile=poster_profile
        )
        cls.user_vote = Vote.objects.create(
            profile=voter_profile, type="down", content_object=question
        )
        question.vote.add(cls.user_vote)


    def test_duplicate_user_vote_disallowed(self):
        data = {
            'type': "up",
            'resource': 'questions/1/'
        }
        request = Mock()
        request.configure_mock(**{'user': self.voter})
        serializer = VoteSerializer(data=data, context={'request': request})
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
