
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from ..views import RegisterNewUserPage
from ..forms import RegisterUserForm

from posts.views import Page

class TestRegisterNewUserView(SimpleTestCase):

    def setUp(self):
        self.view = RegisterNewUserPage()
        self.context = self.view.get_context_data()

    def test_register_new_user_page_instance(self):
        self.assertIsInstance(self.view, Page)
        self.assertIsInstance(self.context['form'], RegisterUserForm)
        self.assertEqual(self.view.template_name, "authors/form.html")
        self.assertEqual("Register a New Account", self.context['title'])


class TestGetRegisterNewUserPage(TestCase):
    '''Verify that an anonymous user can request a page
    to register a new account.'''

    def test_get_register_user_page(self):
        response = self.client.get(reverse("authors:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authors/form.html")
        self.assertContains(response, "Register a New Account")
        self.assertContains(response, "action=/users/signup/")
