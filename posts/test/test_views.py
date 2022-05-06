
from unittest.mock import patch, Mock, PropertyMock
from datetime import date


from django.test import TestCase, SimpleTestCase, RequestFactory
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth import get_user_model
from authors.models import Profile

from ..models import Tag, Question, Answer
from ..forms import QuestionForm
from ..views import QuestionListingPage, EditQuestionPage, Page, PostedQuestionPage, SearchResultsPage, PaginatedPage


class TestQuestionListingPageTemplateContext(SimpleTestCase):

    def setUp(self):
        self.view = QuestionListingPage()
        self.page_context = self.view.extra_context.values()

    def test_question_listing_page_context(self):
        self.assertEqual(self.view.template_name, "posts/main.html")
        self.assertIn("Top Questions", self.page_context)
        self.assertIn(
            ["Interesting", "Hot", "Week", "Month"], self.page_context
        )


class TestRequestQuestionListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.template_chain = ["index.html", "posts/main.html", "posts/listing.html"]

    def test_get_main_question_page(self):
        response = self.client.get(reverse("posts:main"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "posts:main")
        self.assertTemplateUsed(response, "posts/main.html")
        self.assertContains(response, "Browse the complete list of questions")
        for query_button in ["Interesting", "Hot", "Week", "Month"]:
            with self.subTest(query_button=query_button):
                self.assertContains(response, query_button)



class TestDuplicateQuestionPostAttempt(TestCase):
    '''Verify that a User cannot post two questions with the same
    title on the same day.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("Author_101")
        cls.profile = Profile.objects.create(user=cls.user)
        cls.tag = Tag.objects.create(name="Tag1")
        cls.data = {
            'title': "This is a pretty dumb question",
            'body': "There isn't much to say here...Sorry about that!!! Not sure what else to add",
            'profile': cls.profile
        }

    def test_post_duplicate_question_prevented(self):
        self.client.force_login(self.user)
        with patch("posts.models.Question.date") as mock_date:
            mock_date.return_value = date(2022, 3, 1)
            question = Question.objects.create(**self.data)
            question.tags.add(self.tag)
            del self.data['profile']
            self.data.update({"tags_0": "Tag1"})
            posted_question_today = Question.objects.filter(
                title="This is a pretty dumb question", profile=self.profile
            ).count()
            response = self.client.post(
                reverse("posts:ask"), data=self.data
            )
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "posts/ask.html")
            self.assertContains(response, "This post is already posted")
            self.assertContains(response, "title")
            self.assertContains(response, "body")
            self.assertContains(response, "tags")


class TestEditQuestionPage(SimpleTestCase):

    def setUp(self):
        self.view = EditQuestionPage()
        self.context = self.view.get_context_data()

    def test_edit_question_page_instance(self):
        self.assertIsInstance(self.view, Page)
        self.assertEqual(self.view.template_name, "posts/ask.html")
        self.assertEqual(self.context['title'], "Edit your question")
        self.assertIs(self.context['form'], QuestionForm)


class TestGetEditQuestionPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("The_User_000")
        profile = Profile.objects.create(user=cls.user)
        tag = Tag.objects.create(name="TagABC")
        question = Question.objects.create(
            title="What is the difference between A & B?",
            body="I'm trying to figure out this out. Can you help me?",
            profile=profile
        )
        question.tags.add(tag)


    def test_user_question_instance_populates_edit_form(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("posts:edit", kwargs={
                'question_id': 1
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/ask.html")
        self.assertContains(response, "Edit your question")


class TestPostEditQuestionPage(TestCase):
    '''Verify that a message is displayed to the user in the event
    that some aspect of the previous posted question was edited.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="OneAndOnly",
            password="passcoderule"
        )
        profile = Profile.objects.create(user=cls.user)
        tag = Tag.objects.create(name="TagZ")
        question = Question.objects.create(
            title="This is Question Infinity",
            body="The is the content body for This is Question Infinity",
            profile=profile
        )
        question.tags.add(tag)

        cls.data = {
            "title": "This is Question Zero",
            "body": "The is the content body for This is Question Infinity",
            "tags_0": "TagN", "tags_1": "TagZ"
        }

    def test_posted_question_content_changed(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("posts:edit", kwargs={"question_id": 1}),
            data=self.data
        )
        self.assertRedirects(
            response, reverse("posts:question", kwargs={"question_id": 1}),
            status_code=303
        )

class TestGetPostedQuestionPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        tag = Tag.objects.create(name="Tag3")
        cls.user = get_user_model().objects.create_user("MainUser_000")
        profile = Profile.objects.create(user=cls.user)
        question = Question.objects.create(
            title="What is the difference between a session and a cookie?",
            body='''
            "When constructing a HTTP request, what factors are considered
            when deciding to attach data to a cookie or to a session?
            ''',
            profile=profile
        )
        question.tags.add(tag)

    def test_get_newly_asked_question_posted(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("posts:question", kwargs={"question_id": 1})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/question.html")
        self.assertContains(response, "a session and a cookie?")
        self.assertContains(response, "Tag3")
        self.assertContains(response, "When constructing a HTTP request")
        self.assertContains(response, "MainUser_000")


class TestEditInstanceAnswerPage(TestCase):
    '''Verify that a User who has posted an Answer to a given Question
    has the ability to edit their answer.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("TestUser")
        cls.profile = Profile.objects.create(user=cls.user)
        cls.answer_user = get_user_model().objects.create_user("TheAnswer")
        cls.answer_profile = Profile.objects.create(user=cls.answer_user)
        cls.tag = Tag.objects.create(name="Tag1")
        cls.question = Question.objects.create(
            title="How do I get an answer to my post",
            body="This is the content that elaborates on the title that the user provided",
            profile=cls.profile
        )
        cls.question.tags.add(cls.tag)
        cls.answer = Answer.objects.create(
            body="This is answer in response to 'How do I get an answer to my post'",
            question=cls.question,
            profile=cls.answer_profile
        )
        cls.data = {
            "body": "This is a not a very good question. Let me explain why."
        }

    def test_request_get_page_to_edit_answer(self):
        self.client.force_login(self.answer_user)
        response = self.client.get(
            reverse("posts:answer_edit", kwargs={
                "question_id": self.question.id, "answer_id": self.answer.id
            })
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/question.html")

    def test_post_request_edited_answer(self):
        self.client.force_login(self.answer_user)
        response = self.client.post(
            reverse("posts:answer_edit", kwargs={
                "question_id": self.question.id,
                "answer_id": self.answer.id
            }), data=self.data
        )
        self.assertRedirects(
            response, reverse("posts:question", kwargs={'question_id': 1}),
            status_code=303
        )



class TestGetPaginatedPage(SimpleTestCase):

    def setUp(self):
        query = urlencode({'q': 'title:django views', 'pagesize': 10, 'page': ""})
        request = RequestFactory().get(
            f'reverse("posts:search")?{query}'
        )
        self.page = PaginatedPage.as_view()(request)
        self.page_context = self.page.context_data

    def test_get_search_page(self):
        self.assertEqual(
            self.page_context['paginator'].per_page, 10
        )
        self.assertEqual(
            self.page_context['paginator'].object_list.count(), 0
        )


class TestGetSearchPageNoResults(TestCase):

    @classmethod
    def setUpTestData(cls):
        url_path = reverse(f"{'posts:search'}")
        cls.url = f"{url_path}?{urlencode({'q': 'user:4  [ d  jango]'})}"
        cls.url2 = f"{url_path}?{urlencode({'q': 'title:hamburgerbun  '})}"

    def test_get_search_results_user_not_found(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/empty_results.html")
        self.assertContains(response, "We couldn't find anything tagged")
        self.assertContains(response, "not deleted, user 4")

    def test_get_search_results_bad_title_entered(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/empty_results.html")
        self.assertContains(response, "title: hamburgerbun, questions only, not deleted")


class TestRedirectTaggedPaginatedPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        url_path = reverse("posts:search")
        query_string = urlencode({"q":"[django-rest-framework] [restful-api]"})
        cls.url = f"{url_path}?{query_string}"

    def test_get_search_tags_page(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/main.html")
        self.assertContains(response, "All Questions")
        self.assertContains(response, "Tagged with")
