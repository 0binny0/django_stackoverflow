
from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse

from ..views import QuestionListingPage


class TestQuestionListingPageTemplateContext(SimpleTestCase):

    def setUp(self):
        self.view = QuestionListingPage()
        self.page_context = self.view.extra_context.values()

    def test_question_listing_page_context(self):
        self.assertEqual(self.view.template_name, "posts/home_questions.html")
        self.assertIn("All Questions", self.page_context)
        self.assertIn(
            ["Interesting", "Hot", "Week", "Month"], self.page_context
        )
