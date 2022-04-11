
from django import template
from django.urls import resolve, reverse

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


@register.simple_tag
def route(request, *args, **kwargs):
    url_name = resolve(request.path).url_name
    if url_name == "main":
        return f'{reverse("posts:main")}'
