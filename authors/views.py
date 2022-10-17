from django.urls import reverse
from django.http import HttpResponseRedirect, QueryDict, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages
from django.views import View
from django.http import HttpResponse
from django.core.paginator import Paginator

from posts.views import Page
from .forms import RegisterUserForm, LoginUserForm, ProfileSearchQueryForm
from .models import Profile, User

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
            profile = Profile.objects.create(user=user)
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


class UserProfilePage(Page, SingleObjectMixin):

    template_name = "authors/profile.html"
    model = get_user_model()
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        try:
            self.object = self.get_object()
        except ValueError:
            raise Http404()
        context = super().get_context_data(object=self.object)
        context |= {
            'page_options': [
                'Summary', 'Questions', 'Answers', 'Tags', 'Bookmarks'
            ]
        }
        return context

    def get(self, request, id):
        context = self.get_context_data()
        query_page_filter = request.GET.get("tab", "summary").lower()
        post_queries = ['bookmarks', 'questions', 'answers', 'tags']
        profile_url_path = reverse('authors:profile', kwargs={'id': self.object.id})
        if query_page_filter not in post_queries:
                context |= context['object'].profile.collect_profile_data()
                context |= {
                    'query_page_filter': "summary",
                    'form': ProfileSearchQueryForm,
                    'url': {
                        f"profile_{post}": f"{profile_url_path}?tab={post}&sort=newest"
                        for post in post_queries
                    }
                }
        else:
            order_by = request.GET.get("sort")
            if query_page_filter == "tags":
                query_tabs = ['name', 'score']
                query = context['object'].profile.get_tag_posts
            elif query_page_filter == "bookmarks":
                query_tabs = ['newest', 'score', 'added']
                query = context['object'].profile.get_bookmarked_posts
            elif query_page_filter == "questions":
                query_tabs = ['newest', 'score', 'views']
                query = context['object'].profile.get_question_posts
            else:
                query_tabs = ['newest', 'score']
                query = context['object'].profile.get_answer_posts
            if not order_by or order_by not in query_tabs:
                order_by = query_tabs[0]
            paginator = Paginator(query(order_by)['records'], 10)
            page = paginator.get_page(request.GET.get('page', 1))
            query_string = QueryDict(
                f"tab={query_page_filter}&page={page}&sort={order_by}"
            )
            context |= {
                'page': page,
                'page_query_filter': query_page_filter,
                'requested_url': f"{request.path}?{query_string.urlencode()}",
                'form': ProfileSearchQueryForm,
                'query_tabs': query_tabs
            }
        return self.render_to_response(context)
