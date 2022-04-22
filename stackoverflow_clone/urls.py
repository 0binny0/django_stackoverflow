"""stackoverflow_clone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from posts import views as pv
from posts import endpoints as api
from authors import views as av
from authors import endpoints as api


posts_patterns = ([
    path("", pv.QuestionListingPage.as_view(), name="main"),
    path("questions/ask/", pv.AskQuestionPage.as_view(), name="ask"),
    path("questions/<question_id>/edit/", pv.EditQuestionPage.as_view(), name="edit"),
    path("questions/<question_id>/edit/answers/<answer_id>/", pv.EditPostedAnswerPage.as_view(), name="answer_edit"),
    path("questions/<question_id>/", pv.PostedQuestionPage.as_view(), name="question"),
    path("search", pv.SearchResultsPage.as_view(), name="search")
], "posts")

posts_api_patterns = []

authors_patterns =  ([
    path("signup/", av.RegisterNewUserPage.as_view(), name="register"),
    path("login/", av.LoginUserPage.as_view(), name="login"),
    path("logout/", av.LogoutUser.as_view(), name="logout")
], "authors")

authors_api_patterns = ([
    path("", api.AccountsEndpoint.as_view(), name="main")
], "api_authors")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("users/", include(authors_patterns, namespace="authors")),
    path("", include(posts_patterns, namespace="posts")),
    path("api/v1/users", include(authors_api_patterns), name="authors_api"),
    path("api/v1/questions", include(posts_api_patterns), name="posts_api"),
]
