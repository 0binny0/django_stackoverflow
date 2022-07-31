
import re

from django import template
from django.urls import reverse

register = template.Library()

register.simple_tag(takes_context=True)
def previous_page_url(context):
    http_url = context['requested_url']
    page_number_pattern = re.compile(r"(?=page=)\d+")
    previous_page_url = page_number_pattern.sub(
        f"{int(page_number_pattern.search(http_url).group()) - 1}", http_url
    )
    return previous_page_url


register.simple_tag(takes_context=True)
def next_page_url(context):
    http_url = context['requested_url']
    page_number_pattern = re.compile(r"(?=page=)\d+")
    next_page_url = page_number_pattern.sub(
        f"{int(page_number_pattern.search(http_url).group()) + 1}", http_url
    )
    return next_page_url
