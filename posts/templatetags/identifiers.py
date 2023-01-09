from urllib.parse import quote
import re

from django.http import QueryDict
from django import template
from django.urls import resolve, reverse
from django.utils.http import urlencode
from django.utils.html import escape

from ..models import Question, Answer, Bookmark

register = template.Library()

@register.inclusion_tag("posts/posted.html", takes_context=True)
def voting_booth(context, post):
    if isinstance(post, Question):
        id = f"question_{post.id}"
    else:
        id = f"answer_{post.id}"
    if isinstance(post, Answer):
        url = reverse("posts:answer_edit", kwargs={
            "question_id": post.question.id,
            "answer_id": post.id
        })
    else:
        url = reverse("posts:edit", kwargs={"question_id": post.id})
    return {'post': post, "id": id, "url": url, 'request': context['request']}

@register.simple_tag(takes_context=True)
def route(context, button=None):
    request = context['request']
    query_string = request.GET.urlencode()
    button = button.lower()
    url_name = resolve(request.path).url_name
    if url_name == "main":
        url = re.sub(r"/(?=\?)", "", f'{reverse("posts:main")}?tab={button}')
        return url
    elif url_name == "main_paginated":
        url = re.sub(r"/(?=\?)", "", f"{reverse('posts:main_paginated')}?tab={button}")
        return url
    elif url_name == "tagged":
        tags = "+".join(tag for tag in context['tags'])
        url = re.sub(r"/(?=\?)", "", f"{reverse('posts:tagged', kwargs={'tags': tags})}?tab={button}")
        return url
    re_button_pattern = re.compile(r"(?<=tab=)\w+")
    search_query_filter = re_button_pattern.search(query_string)
    if not search_query_filter:
        url = re.sub(r"/(?=\?)", "", f"{reverse('posts:search_results')}?{query_string}&tab={button}")
        return url
    query_string = re_button_pattern.sub(button, query_string)
    url = re.sub(r"/(?=\?)", "", f"{reverse('posts:search_results')}?{query_string}")
    return url

@register.simple_tag(takes_context=True)
def set_page_number_url(context, page=None, limit=None):
    request = context['request']
    request_resolver = resolve(request.path)
    app = request_resolver.app_name
    query_string = QueryDict(request.META['QUERY_STRING'])
    query_tab, search_query = [
        query_string.get("tab", "newest"), query_string.get("q")
    ]
    tab = query_tab if query_tab in context['query_buttons'] else context['query_buttons'][0]
    if page is not None:
        '''
            a Page object is Falsey in a boolean context
                * page ---> False
                * page is Not None --- True
        '''
        page_data = {
            "pagesize": page.paginator.per_page,
            "page": page.number,
            "tab": tab,
        }
    else:
        page_data = {
            'pagesize': limit,
            'page': 1,
            'tab': tab
        }
    # if app == "authors":
    #     _path = "authors:profile"
    # else:
    _path = f"{app}:{request_resolver.url_name}"
    page_name = request_resolver.url_name
    if page_name == "user_listing":
        del page_data['tab']
        del page_data['pagesize']
        if 'search' in query_string:
            page_data['search'] = query_string['search']
        path = reverse(_path)
        query_string = urlencode(page_data)
        url = re.sub(r"(?<=users)\/", "", f"{path}?{query_string}")
        return url
    query_string = urlencode(page_data)
    if page_name == "profile":
        id = re.search(
            r"(?<=users/)\d+", request.path
        )[0]
        path =  reverse(_path, kwargs={'id': int(id)})
        url = re.sub(r"\/(?=\?)", "", context['requested_url'])
        return url
    if page_name == "tagged":
        tags = "+".join(tag for tag in context['tags'])
        path = reverse(_path, kwargs={'tags': tags})
        query_string = urlencode(page_data)
        url = re.sub(r"(?<=users)\/", "", f"{path}?{query_string}")
        return url
    if page_name == "search" and search_query:
        page_data.update({'q': search_query})
    path = reverse(_path)
    url = re.sub(r"(?<=users)\/", "", f"{path}?{query_string}")
    return url


@register.simple_tag(takes_context=True)
def set_previous_page_url(context, page):
    if page.has_previous():
        current_url = set_page_number_url(context, page)
        page_pattern = r"(?<=page=)(?P<page_num>\d+)"
        current_page = int(re.search(
            page_pattern, current_url
        ).groupdict().get("page_num"))
        x = re.sub(page_pattern, f"{current_page - 1}", current_url)
        return re.sub(page_pattern, f"{current_page - 1}", current_url)
    return

@register.simple_tag(takes_context=True)
def set_next_page_url(context, page):
    current_url = set_page_number_url(context, page)
    page_pattern = r"(?<=page=)(?P<page_num>\d+)"
    current_page = int(re.search(
        page_pattern, current_url
    ).groupdict().get("page_num"))
    return re.sub(page_pattern, f"{current_page + 1}", current_url)

@register.simple_tag
def set_post_id(post):
    if isinstance(post, Question):
        return f"question/{post.id}/"
    return f"answer/{post.id}/"

@register.simple_tag(takes_context=True)
def if_main_topic(context, post):
    is_question = isinstance(post, Question)
    if is_question:
        user = context['request'].user
        if hasattr(user, 'profile'):
            bookmark = post.bookmarks.filter(profile=user.profile)
            return [post, bookmark if bookmark else False]
    return None

@register.simple_tag(takes_context=True)
def is_bookmarked(context, question):
    request = context['request']
    if hasattr(request.user, 'profile'):
        current_user_bookmarked_question = question.bookmarks.filter(
            profile=request.user.profile
        ).exists()
        viewed_profile = int(re.search(r"(?<=users/)\d+", request.path)[0])
        if current_user_bookmarked_question and viewed_profile == request.user.id:
            return True
    return False
