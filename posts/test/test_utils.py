
from django.test import SimpleTestCase
from unittest.mock import PropertyMock, patch

from ..utils import (
    resolve_search_query, retrieve_query_title, retrieve_query_tags,
    retrieve_query_user_id, get_page_links
)

class TestSearchQueryTitle(SimpleTestCase):
    '''Verify that a title keyword in a search query is cleaned.'''

    def setUp(self):
        self.test_search_titles = [
            "title:What is the this? keyword in JavaScript!",
            "title: What does        (self) refer      to in       Python?",
            "title: What is a dataclass?   [python]"
        ]
        self.cleaned_search_titles = [
            "what is the this keyword in javascript",
            "what does self refer to in python",
            "what is a dataclass"
        ]

    def test_url_reserverd_keyword_filter_search_query(self):
        for i, test_string in enumerate(self.test_search_titles):
            with self.subTest(i=i, test_string=test_string):
                title = retrieve_query_title(test_string)
                self.assertEqual(title, self.cleaned_search_titles[i])


class TestQueryStringTags(SimpleTestCase):
    '''Verify that any tags [...] within a search query string are cleaned'''

    def setUp(self):
        self.submitted_tags = [
            "-- [  Pyth %    on]",
             "[_%!---%%%django__+___ -@& rest_framework  (^)   ]  [api]",
            "[-- django               models  ]         ",
            "$))[[django-views]]",
            " [                  ] [] >>>> [[]]  [$&))( @%)     ]"
        ]

        self.cleaned_tags = [
            ["python"], ["django-rest-framework", "api"],
            ['djangomodels'], ["django-views"], None
        ]

    def test_searched_query_tags(self):
        for i, tag_query in enumerate(self.submitted_tags):
            with self.subTest(i=i, tag_query=tag_query):
                tags = retrieve_query_tags(tag_query)
                self.assertEqual(tags, self.cleaned_tags[i])


class TestQueryStringSearches(SimpleTestCase):
    '''Find all tags in a search query that are encapsulated
    with open and closed brackets.'''

    def setUp(self):
        self.query_strings = [
            "[s   python ] [ django models ]",
            "[]  [django-forms] title://django form inheritance [  python---]",
            "user:333         [Python]   [___________Django  ---- Models]",
            "[--i- Python-   _   - ------]",
            "title://django form inheritance user:228 [  oop---]",
            "        [ JavaScript!- ((()))] title:    [django-rest-framework] user:729"

        ]
        self.query_data = [
            {"title": None, "tags": ["spython", "djangomodels"], "user": None},
            {"title": "django form inheritance", "tags": ["django-forms", "python"], "user": None},
            {"title": None, "tags": ["python", "django-models"], "user": 333},
            {"title": None, "tags": ["i-python"], "user": None},
            {"title": "django form inheritance", "tags": ["oop"], "user": 228},
            {"title": None, "tags": ['javascript', 'django-rest-framework'], "user": 729}
        ]

    def test_query_string_contains_tags(self):
        for i, query in enumerate(self.query_strings):
            with self.subTest(query=query, i=i):
                result = resolve_search_query(query)
                self.assertEqual(result, self.query_data[i])


class TestUserIdSearchQuery(SimpleTestCase):
    '''Verify that posts can be searched for by a user\'s id'''

    def setUp(self):
        self.mock_user_id_searches = [
            "user:5O3", "user abc", "user:1o55X|1", "user:      "
        ]
        self.user_id_results = [5, None, 1, None]

    def test_search_user_id_match(self):
        for i, user_search in enumerate(self.mock_user_id_searches):
            with self.subTest(user_search=user_search):
                user_id_result = retrieve_query_user_id(user_search)
                self.assertEqual(
                    user_id_result,
                    self.user_id_results[i]
                )


class TestCustomDynamicPageSelector(SimpleTestCase):

    def setUp(self):
        self.current_page = [13, 8, 10, 4, 1, 14, 2]

        self.returned_page_links = [
            [10, 11, 12, 13, 14], [6, 7, 8, 9, 10], [8, 9, 10, 11, 12], [2, 3, 4, 5, 6],
            [1, 2, 3, 4, 5], [10, 11, 12, 13, 14], [1, 2, 3, 4, 5]
        ]

    @patch('django.core.paginator.Page')
    @patch('django.core.paginator.Paginator')
    def test_selected_page_links(self, mock_paginator, mock_page):
        mock_paginator.page_range = range(1, 15)
        mock_paginator.num_pages = 10
        for i, page in enumerate(self.current_page):
            with self.subTest(i=i):
                mock_page.number = self.current_page[i]
                mock_page.paginator = mock_paginator
                page_links_returned = get_page_links(mock_page)
                self.assertListEqual(
                    page_links_returned,
                    self.returned_page_links[i]
                )
