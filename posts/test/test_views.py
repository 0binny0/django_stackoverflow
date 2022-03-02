
from django.test import TestCase, SimpleTestCase, RequestFactory
from django.urls import reverse

from ..views import QuestionListingPage


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
