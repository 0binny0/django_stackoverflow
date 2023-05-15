
from functools import reduce
import re

from django.views.generic.base import TemplateView, RedirectView
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse
from django.core.paginator import Paginator

from authors.models import Profile
from .forms import SearchForm, QuestionForm, AnswerForm
from .models import Question, Tag, Answer, QuestionPageHit

from django.http import HttpResponseRedirect, Http404
from authors.http_status import SeeOtherHTTPRedirect

from .utils import get_page_links, resolve_search_query


class Page(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['search_form'] = SearchForm()
        return context



class QuestionListingPage(Page):

    template_name = "posts/main.html"
    extra_context = {
        "title": "Top Questions",
        "query_buttons": ["interesting", "hot", "week", "month"]
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab_index = self.request.GET.get("tab", "interesting").lower()
        questions = Question.postings.lookup(
            self.request.user, tab_index
        )[:21]
        context.update({"page": questions, "count": questions.count()})
        return context

    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)


class AskQuestionPage(Page):

    template_name = "posts/ask.html"
    extra_context = {
        'title': "Ask a public question"
    }

    def attach_question_tags(self, tags):
        question_tags = []
        for name in tags:
            try:
                tag = Tag.objects.get(name=name)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(name=name)
            finally:
                question_tags.append(tag)
        return question_tags

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = QuestionForm
        return context

    def post(self, request):
        context = self.get_context_data()
        form = context['form'](request.POST)
        if form.is_valid():
            tags = self.attach_question_tags(
                [tag.lower() for tag in form.cleaned_data.pop("tags")]
            )
            try:
                question = form.save(commit=False)
                question.profile = request.user.profile
                question.save()
            except IntegrityError:
                form.add_error(None, "This post is already posted")
                context['form'] = form
            else:
                question.tags.add(*tags)
                form.save_m2m()
                return SeeOtherHTTPRedirect(
                    reverse("posts:question", kwargs={
                        "question_id": question.id
                    })
                )
        context['form'] = form
        return self.render_to_response(context)


class EditQuestionPage(AskQuestionPage):

    template_name = "posts/ask.html"
    extra_context = {
        'title': "Edit your question"
    }

    def get(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        context = self.get_context_data()
        context['form'] = context['form'](instance=question)
        return self.render_to_response(
            context, headers={
                'Content-Type': "text/html"
            }
        )

    def post(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        context = self.get_context_data()
        form = context['form'](request.POST, instance=question)
        if form.is_valid():
            if form.has_changed():
                messages.success(request, "Question updated!")
            x = [tag.lower() for tag in form.cleaned_data.pop("tags")]
            tags = self.attach_question_tags(x)
            question = form.save()
            question.tags.set(tags)
            return SeeOtherHTTPRedirect(reverse(
                "posts:question", kwargs={"question_id": question_id}
            ))
        return self.render_to_response(context)


class PostedQuestionPage(Page):

    template_name = "posts/question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer_form'] = AnswerForm
        return context

    def get(self, request, question_id):
        context = self.get_context_data()
        question = get_object_or_404(Question, id=question_id)
        if question.profile.user != request.user and not question.visible:
            raise Http404
        hit = {"question": question, "profile": request.user, "address": request.META["REMOTE_ADDR"]}
        if hasattr(request.user, 'profile'):
            user_already_viewed = QuestionPageHit.objects.filter(**hit).exists()
            if not user_already_viewed:
                QuestionPageHit.objects.create(**hit)
        context |= {
            'question': question,
            'answer_count': question.answers.count(),
            'hit_count': question.page_hits.count()
        }

        return self.render_to_response(context)

    def post(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        context = self.get_context_data()
        form = context['answer_form'](request.POST)
        if form.is_valid():
            form.cleaned_data.update({"profile": request.user.profile})
            answer = Answer.objects.create(
                **form.cleaned_data, question=question
            )
            return SeeOtherHTTPRedirect(
                reverse("posts:question", kwargs={
                    "question_id": answer.question.id
                })
            )


class EditPostedAnswerPage(PostedQuestionPage):

    def get(self, request, question_id, answer_id):
        context = super().get(request, question_id).context_data
        answer = get_object_or_404(Answer, pk=answer_id)
        context.update({
            "answer_form": context['answer_form'](instance=answer),
            'answer': answer
        })
        return self.render_to_response(context)

    def post(self, request, question_id, answer_id):
        context = super().get_context_data()
        question = get_object_or_404(Question, pk=question_id)
        answer = get_object_or_404(Answer, pk=answer_id)
        if context['answer_form'](request.POST, instance=answer).is_valid():
            return SeeOtherHTTPRedirect(
                reverse("posts:question", kwargs={
                    'question_id': question.id
                })
            )
        return self.render_to_response(context)


class PaginatedPage(Page):

    template_name = "posts/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        r = self.request
        page_sizes = {
            '10': 10,
            '15': 15,
            '25': 25
        }
        size = r.GET.get('pagesize')
        if not size or size not in page_sizes.keys():
            size = '10'
        page_size = page_sizes.get(size)
        paginator = Paginator(Question.objects.none(), page_size)
        context.update({
            'paginator': paginator,
            'query_buttons': ["newest", "unanswered", "score"],
            'page_listing_limits': [f"{n}" for n in page_sizes.values()]
        })
        return context


class AllQuestionsPage(PaginatedPage):

    def get(self, request):
        context = super().get_context_data()
        tab_index = request.GET.get('tab', "newest")
        context['paginator'].object_list = Question.searches.lookup(tab_index)[0]
        page = context['paginator'].get_page(
            request.GET.get("page", 1)
        )
        context.update({
            'title': "All Questions",
            "page": page,
            "page_links": get_page_links(page),
            "count": page.paginator.count
        })
        return self.render_to_response(context)


class SearchResultsPage(PaginatedPage):

    def get(self, request):
        context = self.get_context_data()
        query_string = request.GET
        if not query_string or 'q' not in query_string:
            context |= {
                'title': 'Search'
            }
            self.template_name = "posts/search_menu.html"
            return self.render_to_response(context)
        search_query, tab_index = query_string.get('q'), query_string.get('tab', 'newest')
        title_or_tag_search = re.search(r"(?:title)|\[[a-zA-Z.0-9]+\]", search_query)
        if not title_or_tag_search:
            user_id_match = re.fullmatch(r"user:(\d+)", search_query)
            if user_id_match:
                searched_id = user_id_match.group(1)
                user_id = searched_id.replace("0", "")
                if not user_id:
                    user_id = 1
                return HttpResponseRedirect(reverse("authors:profile", kwargs={'id': int(user_id)}))
        queryset, query_data = Question.searches.lookup(tab_index, query=search_query)
        if query_data['tags'] and all(not query_data[search] for search in ['title', 'user', 'phrases']):
            tags = "".join([
                f"{tag}+" if i != len(query_data["tags"]) - 1 else f"{tag}"
                for i, tag in enumerate(query_data["tags"])
            ])
            return HttpResponseRedirect(reverse("posts:tagged", kwargs={'tags': tags}))
        else:
            context['search_form'].fields['q'].widget.attrs.update(
                {"value": search_query}
            )
            context['paginator'].object_list = queryset
            page = context['paginator'].get_page(
                request.GET.get("page", None)
            )
            context.update({
                'title': "Search Results",
                'query_data': query_data,
                'page': page,
                'page_links': get_page_links(page),
                'count': page.paginator.count
            })
        return self.render_to_response(context)


class SearchMenuPage(RedirectView):

    pattern_name = "posts:search_results"

    def get_redirect_url(self, *args, **kwargs):
        url = reverse(self.pattern_name)
        return f"{url}?q="


class SearchTaggedRedirect(RedirectView):

    pattern_name = "posts:main_paginated"


class TaggedSearchResultsPage(PaginatedPage):

    def get(self, request, tags):
        context = super().get_context_data()
        query = "".join(f" [{tag}] " for tag in tags.split("+"))
        tab_index = request.GET.get('tab', "newest")
        context['search_form'].fields['q'].widget.attrs.update({"value": query})

        queryset, query_data = Question.searches.lookup(tab_index, query=query)
        context['paginator'].object_list = queryset
        page = context['paginator'].get_page(
            request.GET.get("page", None)
        )
        tags = query_data['tags']
        context.update({
            "title": "All Questions" if len(tags) > 1 else f"Questions tagged {tags[0]}",
            'page': page,
            'page_links': get_page_links(page),
            'tags': tags,
            'count': page.paginator.count
        })
        return self.render_to_response(context)
