
from functools import reduce

from django.views.generic.base import TemplateView
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.urls import reverse

from authors.models import Profile
from .forms import SearchForm, QuestionForm, AnswerForm
from .models import Question, Tag, Answer

from django.http import HttpResponseRedirect
from authors.http_status import SeeOtherHTTPRedirect


class Page(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['search_form'] = SearchForm()
        return context



class QuestionListingPage(Page):

    template_name = "posts/main.html"
    extra_context = {
        "title": "Top Questions",
        "query_buttons": ["Interesting", "Hot", "Week", "Month"]
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = Question.objects.all()
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
            tags = self.attach_question_tags(form.cleaned_data.pop("tags"))
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
            x = form.cleaned_data.pop("tags")
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
        context['question'] = question
        return self.render_to_response(context)


    def post(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        context = super.get_context_data()
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
                    'question_id': 1
                })
            )
<<<<<<< HEAD
        return self.render_to_response(context)
=======
>>>>>>> e164dce4f175d738bedeef8dd3164b14e016623f
