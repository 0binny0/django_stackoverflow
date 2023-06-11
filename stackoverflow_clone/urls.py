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
from django.urls import path, include, re_path, reverse

from posts import views as pv
from posts import endpoints as posts_api
from authors import views as av
from authors import endpoints as authors_api


posts_patterns = ([
    path(r"", pv.QuestionListingPage.as_view(), name="main"),
    re_path(r"questions/ask/?$", pv.AskQuestionPage.as_view(), name="ask"),
    re_path(r"questions/(?P<question_id>\d+)/edit/?$", pv.EditQuestionPage.as_view(), name="edit"),
    re_path(r"questions/(?P<question_id>\d+)/edit/answers/(?P<answer_id>\d+)/?$", pv.EditPostedAnswerPage.as_view(), name="answer_edit"),
    re_path(r"questions/(?P<question_id>\d+)/?$", pv.PostedQuestionPage.as_view(), name="question"),
    re_path(r"questions/tagged/(?P<tags>[0-9a-zA-Z\.\-#]+(?:\+[\s0-9a-zA-Z\.\-#]+)*)$", pv.TaggedSearchResultsPage.as_view(), name="tagged"),
    re_path(r"questions/tagged/$", pv.SearchTaggedRedirect.as_view(), name="tagged_redirect"),
    re_path(r"questions/search/$", pv.SearchMenuPage.as_view(), name="search_menu"),
    re_path(r"questions/search$", pv.SearchResultsPage.as_view(), name="search_results"),
    re_path(r"questions/?$", pv.AllQuestionsPage.as_view(), name="main_paginated"),

], "posts")

votes_api_patterns = ([
    path("<int:id>/", posts_api.UserVoteEndpoint.as_view(), name="vote")
], "posts")

post_api_patterns = ([
    path("<int:id>", posts_api.PageStatusEndpoint.as_view(), name="post")
], "posts")

bookmark_api_patterns = ([
    path("<int:id>/", posts_api.BookmarkedPostEndpoint.as_view(), name="bookmark")
], "posts")

authors_patterns =  ([
    re_path(r"/signup/", av.RegisterNewUserPage.as_view(), name="register"),
    re_path(r"/login/", av.LoginUserPage.as_view(), name="login"),
    re_path(r"/logout/", av.LogoutUser.as_view(), name="logout"),
    re_path(r"/(?P<id>\d+)/?$", av.UserProfilePage.as_view(), name="profile"),
    re_path(r"/?$", av.UserDirectory.as_view(), name="user_listing"),
], "authors")

authors_api_patterns = ([
    re_path(r"$", authors_api.AccountsEndpoint.as_view(), name="main")
], "api_authors")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("users", include(authors_patterns, namespace="authors")),
    path("", include(posts_patterns, namespace="posts")),
    path("api/v1/users", include(authors_api_patterns), name="authors_api"),
    path("api/v1/votes/", include(votes_api_patterns, namespace="api_votes")),
    path("api/v1/posts/", include(post_api_patterns, namespace="api_posts")),
    path("api/v1/bookmarks/", include(bookmark_api_patterns, namespace="api_bookmarks"))
]
