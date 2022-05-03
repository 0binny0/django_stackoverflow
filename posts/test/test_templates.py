
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, RequestFactory
from django.utils.http import urlencode
from django.urls import reverse
from django.core.paginator import Page
from ..templatetags import identifiers

class TestRouteTemplateTag(SimpleTestCase):
    '''Verify that the {% route %} tag directs to a URL
    within the current app based on the path of the
    current page URL'''

    def setUp(self):
        self.request = RequestFactory().get(
            f"{reverse('posts:main')}?tab=monthly"
        )

    def test_directed_to_link_url(self):
        url = identifiers.route(self.request)
        self.assertEqual(url, "/")


class TestPaginatedPageLink(SimpleTestCase):
    '''Verify that a numbered page link can direct a user
    to a different page with the same query arguments.'''

    def setUp(self):
        query = urlencode({'pagesize': 20, 'tab': 'week', 'page': 3, 'q': "python mocks"})
        request = RequestFactory().get(
            f"{reverse('posts:search')}?{query}"
        )
        self.context = {'request': request}

    @patch("django.core.paginator.Page", autospec=True)
    @patch("django.core.paginator.Paginator", autospec=True)
    def test_number_page_url(self, mockPaginator, mockPage):
        mockPaginator.object_list, mockPaginator.per_page = [[], 20]
        mockPage.object_list, mockPage.number, mockPage.paginator = [
            [], 4, mockPaginator
        ]
        numbered_page_url = identifiers.set_page_number_url(self.context, mockPage)
        self.assertEqual(
            numbered_page_url, "/search?pagesize=20&page=4&tab=week&q=python+mocks"
        )
