
from datetime import date

from unittest.mock import Mock, patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Tag, Question, Vote
from authors.models import Profile

from django.db.models import F

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


class TestQuestionScoreUpVote(TestCase):
    '''Verify that a Question's score changes by one point
    dependent upon whether a user likes or dislikes a question'''

    @classmethod
    def setUpTestData(cls):
        tag1 = Tag.objects.create(name="Tag1")
        user = get_user_model().objects.create_user("TestUser")
        cls.profile = Profile.objects.create(user=user)
        cls.question = Question.objects.create(
            title="Question__001",
            body="Content of Question 001",
            profile=cls.profile
        )
        cls.question.tags.add(tag1)

    def test_new_user_like_vote_on_question(self):
        user_vote = Vote.objects.create(
            profile=self.profile, type="like", content_object=self.question
        )
        self.assertEqual(self.question.score, 1)

    def test_new_user_dislike_vote_on_question(self):
        user_vote = Vote.objects.create(
            profile=self.profile, type="dislike", content_object=self.question
        )
        self.assertEqual(self.question.score, -1)


class TestQuestionQuerySearchManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user("MeT00")
        cls.profile1 = Profile.objects.create(user=cls.user1)
        cls.user2 = get_user_model().objects.create_user("YouT00")
        cls.profile2 = Profile.objects.create(user=cls.user2)
        cls.user3 = get_user_model().objects.create_user("NotME")
        cls.profile3 = Profile.objects.create(user=cls.user3)
        cls.tag1 = Tag.objects.create(name="tag1")
        cls.tag2 = Tag.objects.create(name="tag2")
        cls.tag3 = Tag.objects.create(name="tag3")
        cls.question1 = Question.objects.create(
            title="This is a question about creating custom Django Managers",
            body="When creating managers, is it best to encapsulate methods based on their functionality?",
            profile=cls.profile2
        )
        cls.question1.tags.add(*[cls.tag2, cls.tag3])
        cls.question2 = Question.objects.create(
            title="How do I decided when to subclass a Django View?",
            body="When it comes to inheritence, what features of a view do you most likely find yourself wanting to extend?",
            profile=cls.profile2
        )
        cls.question2.tags.add(cls.tag2)
        cls.question3 = Question.objects.create(
            title="What features do you not like about Django?",
            body="When it comes to using Django, are there any features that you can live without?",
            profile=cls.profile1
        )
        cls.question3.tags.add(cls.tag1)
        cls.question4 = Question.objects.create(
            title="What's the purpose of type annotations in Python?",
            body="Is it worth the energy to add type hints in Python? It makes the code more verbose",
            profile=cls.profile3
        )
        cls.question4.tags.add(cls.tag3)
        cls.queryset1, cls.data1 = Question.searches.lookup("[ #(@@Tag2   ] [  ] user:2")
        cls.queryset2, cls.data2 = Question.searches.lookup("title:@*#$Django")
        cls.queryset3, cls.data3 = Question.searches.lookup("user:1")

    def test_search_questions_by_regex_tags(self):
        self.assertEqual(self.queryset1.count(), 2)
        self.assertQuerysetEqual(
            self.queryset1, [
                "Question(title=This is a question about creating custom Django Managers)",
                "Question(title=How do I decided when to subclass a Django View?)"
            ], transform=repr
        )

    def test_search_questions_by_regex_title(self):
        self.assertEqual(self.queryset2.count(), 3)
        self.assertQuerysetEqual(
            self.queryset2, [
                "Question(title=This is a question about creating custom Django Managers)",
                "Question(title=How do I decided when to subclass a Django View?)",
                "Question(title=What features do you not like about Django?)",
            ], transform=repr
        )

    def test_search_questions_by_regex_user(self):
        self.assertEqual(self.queryset3.count(), 1)
        self.assertQuerysetEqual(
            self.queryset3, [
                "Question(title=What features do you not like about Django?)",
            ], transform=repr
        )
