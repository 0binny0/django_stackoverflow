from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.views import View

from posts.views import Page
from .forms import RegisterUserForm, LoginUserForm
from .models import Profile

from .http_status import SeeOtherHTTPRedirect

class RegisterNewUserPage(Page):

    template_name = "authors/form.html"
    extra_context={
        "title": "Register a New Account"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RegisterUserForm
        return context

    def get(self, request):
        context  = self.get_context_data()
        context.update({"form": context['form']()})
        return self.render_to_response(context)

    def post(self, request):
        context = self.get_context_data()
        form = context['form'](self.request.POST or None)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return SeeOtherHTTPRedirect(reverse("posts:main"))
        return self.render_to_response(context)


class LoginUserPage(Page):

    template_name = "authors/form.html"
    extra_context = {
        'title': "Login into your account"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginUserForm
        return context

    def post(self, request):
        context = self.get_context_data()
        form = context['form'](request, request.POST)
        if form.is_valid():
            user = get_object_or_404(
                get_user_model(), username=form.cleaned_data["username"]
            )
            login(request, user)
            return SeeOtherHTTPRedirect(reverse("posts:main"))
        return self.render_to_response(context)


class LogoutUser(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("posts:main"))
