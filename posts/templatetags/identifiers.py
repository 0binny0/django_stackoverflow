from urllib.parse import quote
import re

from django.http import QueryDict
from django import template
from django.urls import resolve, reverse
from django.utils.http import urlencode
from django.utils.html import escape

register = template.Library()

@register.inclusion_tag("posts/posted.html")
def voting_booth(post, *args, **kwargs):
    context = {
        'question': kwargs.get("question"),
        'answer': kwargs.get("answer"),
        'comment': kwargs.get("comment"),
    }
    if all(context[key] for key in context):
        id = "".join(
            f"{key}{value}_" if i < 2 else f"{key}{value}"
            for i, (key, value) in enumerate(context.items())
        )
        return {
            'post': post,
            'id': id
        }
    valid_keys = list(filter(lambda x: context[x], context.keys()))
    id = "".join(
        (f"{key}{context[key]}_"
        if context[key] and i < (len(valid_keys) - 1)
        else f"{key}{context[key]}")
        for i, key in enumerate(valid_keys)
    )
    if context['question'] and context['answer']:
        url = reverse("posts:answer_edit", kwargs={
            "question_id": context['question'],
            "answer_id": context['answer']
        })
    else:
        url = reverse("posts:edit", kwargs={"question_id": context['question']})
    return {'post': post, "id": id, "url": url}

@register.simple_tag(takes_context=True)
def route(context, button=None):
    request = context['request']
    query_data = request.GET
    button = button.lower()
    url_name = resolve(request.path).url_name
    if url_name == "main":
        return f'{reverse("posts:main")}?tab={button}'
    elif url_name == "main_paginated":
        return f"{reverse('posts:main_paginated')}?tab={button}"
    elif url_name == "tagged":
        tags = "+".join(tag for tag in context['tags'])
        return f"{reverse('posts:tagged', kwargs={'tags': tags})}?tab={button}"
    query_string = "&".join(map(
        lambda query: (
            f"{query[0]}={quote(query[1])}"
            if query[0] == 'title' else (
                f"{query[0]}={query[1]}"
                if query[0] != "tags" else
                f"{quote('+'.join(f'[{tag}]' for tag in query[1]))}"
            )
        )
        , filter(lambda q: q[1], query_data.items())
    ))
    return f"{reverse('posts:search')}?{query_string}&tab={button}"

@register.simple_tag(takes_context=True)
def set_page_number_url(context, page=None, limit=None):
    request = context['request']
    request_resolver = resolve(request.path)
    query_string = QueryDict(request.META['QUERY_STRING'])
    query_tab, search_query = [
        query_string.get("tab", "newest"), query_string.get("q")
    ]
    if page:
        page_data = {
            "pagesize": page.paginator.per_page,
            "page": page.number,
            "tab": query_tab,
        }
    else:
        page_data = {
            'pagesize': limit,
            'page': 1,
            'tab': query_tab
        }
    _path = f"posts:{request_resolver.url_name}"
    if request_resolver.url_name == "tagged":
        tags = "+".join(tag for tag in context['tags'])
        path = reverse(_path, kwargs={'tags': tags})
        query_string = urlencode(page_data)
        return f"{path}?{query_string}"
    if request_resolver.url_name == "search" and search_query:
        page_data.update({'q': search_query})
    query_string = urlencode(page_data)
    path = reverse(_path)
    return f"{path}?{query_string}"


@register.simple_tag(takes_context=True)
def set_previous_page_url(context, page):
    if page.has_previous():
        current_url = set_page_number_url(context, page)
        page_pattern = r"(?<=page:)(?P<page_num>\d+)"
        current_page = int(re.search(
            page_pattern, current_url
        ).get("page_num"))
        return re.sub(page_pattern, f"{current_page - 1}", current_url)
    return

# @register.simple_tag(takes_context=True)
# def set_previous_page_url(context, page):
#     current_url = set_page_number_url(context, page)
#     page_pattern = r"(?<=page:)(?P<page_num>\d+)"
#     current_page = int(re.search(
#         page_pattern, current_url
#     ).get("page_num"))
#     return re.sub(page_pattern, f"{current_page - 1}", current_url)

@register.simple_tag(takes_context=True)
def set_next_page_url(context, page):
    current_url = set_page_number_url(context, page)
    page_pattern = r"(?<=page:)(?P<page_num>\d+)"
    current_page = int(re.search(
        page_pattern, current_url
    ).get("page_num"))
    return re.sub(page_pattern, f"{current_page + 1}", current_url)
