
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, RequestFactory
from django.utils.http import urlencode
from django.urls import reverse
from django.core.paginator import Page
from ..templatetags import identifiers
from authors.models import Profile
from ..models import Tag, Question

class TestRouteTemplateTag(SimpleTestCase):
    '''Verify that the {% route %} tag directs to a URL
    within the current app based on the path of the
    current page URL'''

    def setUp(self):
        self.request1 = RequestFactory().get(
            f"{reverse('posts:main')}?tab=monthly"
        )

        self.request2 = RequestFactory().get(
            f"{reverse('posts:tagged', kwargs={'tags': 'python'})}?tab=active"
        )

        self.request3 = RequestFactory().get(
            f"{reverse('posts:search_results')}?page=2&pagesize=10"
        )

    # def test_directed_to_link_url(self):
    #     url = identifiers.route({'request': self.request1}, )
    #     self.assertEqual(url, "/")

    def test_directed_url_with_single_query_string_arg(self):
        url = identifiers.route({'request': self.request1}, button="Unanswered")
        self.assertIn(
            "?tab=unanswered", url
        )

    def test_directed_url_with_multiple_query_string_args(self):
        url = identifiers.route({'request': self.request3}, button="Active")
        self.assertIn("?page=2&pagesize=10" ,url)


class TestPaginatedPageLink(SimpleTestCase):
    '''Verify that a numbered page link can direct a user
    to a different page with the same query arguments.'''

    def setUp(self):
        query = urlencode({'pagesize': 20, 'tab': 'week', 'page': 3, 'q': "python mocks"})
        request = RequestFactory().get(
            f"{reverse('posts:search_results')}?{query}"
        )
        query_buttons = ['recent', 'hot', 'week', 'month']

        self.context = {'request': request, 'query_buttons': query_buttons}

    @patch("django.core.paginator.Page", autospec=True)
    @patch("django.core.paginator.Paginator", autospec=True)
    def test_number_page_url(self, mockPaginator, mockPage):
        mockPaginator.object_list, mockPaginator.per_page = [[], 20]
        mockPage.object_list, mockPage.number, mockPage.paginator = [
            [], 4, mockPaginator
        ]
        numbered_page_url = identifiers.set_page_number_url(self.context, limit=25)
        self.assertEqual(
            numbered_page_url, "/questions/search?q=python+mocks&pagesize=25&page=1&tab=week"
        )


class TestPreviousPageLink(SimpleTestCase):
    pass


class TestMainTopicTemplateTag(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user("ItsMe")
        profile = Profile.objects.create(user=user)
        tag = Tag.objects.create(name="Tag1")
        post = Question.objects.create(
            title="This is Topic #0000000000000000000000000",
            body="This is the content explaining the problem posted",
            profile=profile
        )
        post.tags.add(tag)
        mock_request = Mock()
        mock_request.user = user
        context = {'request': mock_request}
        cls.post_is_question = identifiers.if_main_topic(context, post)

    def test_post_is_question_instance(self):
        self.assertTrue(self.post_is_question)
