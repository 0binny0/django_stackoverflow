from django.shortcuts import render

from posts.views import Page
from .forms import RegisterUserForm

class RegisterNewUserPage(Page):

    template_name = "authors/form.html"
    extra_context={
        "title": "Register a New Account"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RegisterUserForm()
        return context
