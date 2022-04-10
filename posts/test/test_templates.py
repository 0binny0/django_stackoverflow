
from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse

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
