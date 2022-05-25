
from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..views import RegisterNewUserPage, LoginUserPage
from ..forms import RegisterUserForm, LoginUserForm
from ..models import Profile

from posts.views import Page

class TestRegisterNewUserView(SimpleTestCase):

    def setUp(self):
        self.view = RegisterNewUserPage()
        self.context = self.view.get_context_data()

    def test_register_new_user_page_instance(self):
        self.assertIsInstance(self.view, Page)
        self.assertIs(self.context['form'], RegisterUserForm)
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
        self.assertContains(response, "/users/signup/")


class TestLoginUserView(SimpleTestCase):

    def setUp(self):
        self.view = LoginUserPage()
        self.context = self.view.get_context_data()


    def test_get_login_page(self):
        self.assertIsInstance(self.view, Page)
        self.assertIs(self.context['form'], LoginUserForm)
        self.assertEqual(self.view.template_name, "authors/form.html")
        self.assertEqual(
            "Login into your account",
            self.context['title']
        )


class TestGetLoginPage(TestCase):

    def test_get_request_login_page(self):
        response = self.client.get(reverse("authors:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authors/form.html")
        self.assertContains(response, "Login into your account")


class TestUserLoginSuccess(TestCase):
    '''Verify that a user is redirected to the main home page
    when the username & password credentials provided are valid'''

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(
            username="TheBest101",
            password="some$ecret"
        )
        Profile.objects.create(user=user)

    def test_post_login_user_redirect(self):
        response = self.client.post(
            reverse("authors:login"), data={
                "username": "TheBest101", "password": "some$ecret"
            }
        )
        self.assertRedirects(response, reverse("posts:main"), status_code=303)
