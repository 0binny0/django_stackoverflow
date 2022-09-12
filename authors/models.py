from django.db.models import (
    Model, OneToOneField, ForeignKey, CharField, CASCADE
)
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Manager, Count, Subquery, OuterRef, F, Value
from django.db.models.functions import Concat

from posts.models import Question, Answer, Vote, Tag

class User(AbstractUser):

    username = CharField(
        unique=True, max_length=16,
        error_messages={
            "unique": "Username not available"
        }
    )


class Profile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    def get_tag_posts(self, order_by=None):
        if not order_by:
            order_by = "-question__score"
        elif order_by == "name":
            pass
        else:
            order_by = "-question__score"
        questions_with_tag = Subquery(self.questions.filter(
            tags__name=OuterRef("name")).only('id'))
        tags = Tag.objects.filter(
            question__profile=self
        ).distinct()
        return {
            'records': tags.annotate(
                times_posted=Count(questions_with_tag)
            ).order_by("-times_posted"),
            'title': f"{tags.count()} Tags"
        }

    def get_question_posts(self, order_by=None):
        if not order_by or order_by == "newest":
            order_by = "date"
        if order_by == "score" or order_by == "date":
            questions = self.questions.all().order_by(f"-{order_by}")
        else:
            questions = self.questions.all().order_by("-answer__date")
        return {
            'records': questions,
            'title': f"{questions.count()} Questions"
        }

    def get_answer_posts(self, order_by=None):
        if not order_by or order_by == "newest":
            order_by = "date"
        else:
            order_by = f"-{order_by}"
        answers = self.answers.all().order_by(order_by).annotate(
            in_response_to=Concat(Value("Question:"), "question__title")
        )
        return {
            "records": answers,
            'title': f"{self.answers.count()} Answers"
        }

    def get_posts_voted_on(self, sort=None):
        votes = Vote.objects.filter(profile=self)
        return {
            'like': votes.filter(type="like").count(),
            'dislike': votes.filter(type="dislike").count(),
            'questions': Question.objects.filter(vote__profile=self).count(),
            'answers': Answer.objects.filter(vote__profile=self).count()
        }

    def get_bookmarked_posts(self, sort=None):
        questions = Question.objects.filter(bookmarks__profile=self)
        return {
            'records': questions,
            'title': f"{questions.count()} bookmarks"
        }

    def collect_profile_data(self):
        profile_posts = {
            "question": self.get_question_posts(),
            "answer": self.get_answer_posts(),
            "tag": self.get_tag_posts(),
            "bookmark": self.get_bookmarked_posts(),
        }
        for post_type, data in profile_posts.items():
            _queryset = data['records'][:5]
            profile_posts[post_type]['records'] = _queryset
        profile_posts.update({'votes': self.get_posts_voted_on()})
        return profile_posts

    class Meta:
        permissions = [("can vote", "Can vote")]
