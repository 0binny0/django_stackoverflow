
from django.test import SimpleTestCase, TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.template.loader import render_to_string

from ..views import RegisterNewUserPage, LoginUserPage, UserProfilePage
from ..forms import RegisterUserForm, LoginUserForm
from ..models import Profile
from posts.models import Tag, Question

from posts.views import Page

import unittest
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


class TestUserProfilePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("ItsMe")
        Profile.objects.create(user=cls.user)
        cls.page_context = ["ItsMe", "Questions", "Answers", "Bookmarks", "Votes Cast"]
        all_users = get_user_model().objects.all()

    def test_user_profile_page_content(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("authors:profile", kwargs={'id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authors/profile.html")
        for page_element in self.page_context:
            with self.subTest(page_element=page_element):
                self.assertContains(response, page_element)


class TestViewUserQuestionsPostedPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.viewed_user = get_user_model().objects.create_user("ItsYou")
        Profile.objects.create(user=cls.viewed_user)
        request = RequestFactory().get(reverse("authors:profile", kwargs={'id': 1}))
        cls.view = UserProfilePage()
        cls.view.setup(request, id=1)
        cls.view_context = cls.view.get_context_data()

    def test_viewed_profile_of_user(self):
        self.assertIsInstance(self.view, Page)
        self.assertIn('user', self.view_context)
        self.assertEqual(self.view_context['object'], self.viewed_user)


class TestUserProfileContext(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.viewed_user = get_user_model().objects.create_user("ItsYou")
        Profile.objects.create(user=cls.viewed_user)
        cls.url = reverse("authors:profile", kwargs={'id': 1})

    def test_viewed_profile_of_user(self):
        response = self.client.get(f"{self.url}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authors/profile.html")
        self.assertContains(response, "ItsYou")
        for title in ['Questions', 'Answers', 'Tags', 'Bookmarks']:
            with self.subTest(title=title):
                self.assertContains(response, title)


# class TestUserQuestionProfileContext(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         viewed_user = get_user_model().objects.create_user("ItsYou")
#         Profile.objects.create(user=viewed_user)
#         cls.url = f"{reverse('authors:profile', kwargs={'id': 2})}?tab=questions"
#
#     def test_viewed_user_profile_questions_page(self):
#         for tab in ['questions', 'answers', ]
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "authors/profile.html")


class TestUserQuestionProfileTemplate(TestCase):

    @classmethod
    def setUpTestData(cls):
        tag1 = Tag.objects.create(name="Tag1")
        tag2 = Tag.objects.create(name="Tag2")
        user = get_user_model().objects.create_user("ItsNotYou")
        profile = Profile.objects.create(user=user)
        cls.question = Question.objects.create(
            title="Test Question ZZZ",
            body="Post content detailing the problem about Test Question ZZZ",
            profile=profile
        )
        cls.question.tags.add(*[tag1, tag2])
        cls.template = render_to_string(
            "authors/questions.html", {"question": cls.question}
        )
        cls.context = [
            "Test Question ZZZ", "Tag1", "Tag2"
        ]


    def test_template_profile_questions_listing(self):
        for string in self.context:
            with self.subTest(string=string):
                self.assertIn(string, self.template)




'''Note: TestCase is automatically creating a <User: AnonymousUser>;
         this is unexpected behavior, and the cause is unknown
'''
