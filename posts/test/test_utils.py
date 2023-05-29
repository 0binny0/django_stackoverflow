
from django.test import SimpleTestCase, RequestFactory
from django.utils.http import urlencode
from unittest.mock import PropertyMock, patch
from django.urls import reverse
from django.core.paginator import Paginator

from ..utils import (
    resolve_search_query, retrieve_query_title, retrieve_query_tags,
    retrieve_query_user_id, get_page_links, retrieve_exact_phrases
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
            "What is the this? keyword in JavaScript!",
            "What does (self) refer to in Python?",
            "What is a dataclass?"
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
            ["python"], ["django-+-rest-framework", "api"],
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
            "  [django-forms] title://django form inheritance [  python---]",
            "user:333         [Python]   [___________Django  ---- Models]",
            "[--i- Python-   _   - ------]",
            "title://django form inheritance user:228 [  oop---]",
            "        [ JavaScript!- ((()))] title:    [django-rest-framework] user:729"

        ]
        self.query_data = [
            {"title": None, "tags": ["spython", "djangomodels"], "user": None, "phrases": [""]},
            {"title": "//django form inheritance", "tags": ["django-forms", "python"], "user": None, "phrases": [""]},
            {"title": None, "tags": ["python", "django-models"], "user": 333, "phrases": [""]},
            {"title": None, "tags": ["i-python"], "user": None, "phrases": [""]},
            {"title": "//django form inheritance", "tags": ["oop"], "user": 228, "phrases": [""]},
            {"title": None, "tags": ['javascript', 'django-rest-framework'], "user": 729, "phrases": [""]}
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

        self.min_page_links = [10, 6, 8, 2, 1, 10, 1]
        self.max_page_links = [14, 10, 12, 6, 5, 14, 5]

    def test_selected_page_links(self):
        paginator = Paginator(list(range(0, 140)), 10)
        for i, page in enumerate(self.current_page):
            with self.subTest(i=i):
                page = paginator.page(self.current_page[i])
                page_links_returned = get_page_links(page)
                self.assertEqual(
                    page_links_returned[0].number, self.min_page_links[i]
                )
                self.assertEqual(
                    page_links_returned[-1].number, self.max_page_links[i]
                )

class TestGetSearchPhrase(SimpleTestCase):

    def setUp(self):
        user = '2'
        title = "'I dunno lol'"
        tags = ['abc', 'xyz']
        string = "title:'I dunno lol' user:2 [abc] [xyz] Python  decorators"
        self.phrases = retrieve_exact_phrases(user, tags, title, string)

    def test_filtered_search_phrases(self):
        self.assertEqual(self.phrases, ['python', 'decorators'])
