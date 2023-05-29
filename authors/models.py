from django.db.models import (
    Model, OneToOneField, ForeignKey, CharField, CASCADE
)
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.conf import settings
from django.db.models import Manager, Count, Subquery, OuterRef, F, Value, Avg, IntegerField, QuerySet
from django.db.models.functions import Concat

from posts.models import Question, Answer, Vote, Tag, Bookmark

class UserQueryManager(Manager):

    def get_queryset(self):
        return super().get_queryset().annotate(
            post_count=Count("profile__question")
        )

    def by_name(self, name):
        if not name:
            return self.get_queryset()
        return self.get_queryset().filter(
            username__icontains=name
        )

class User(AbstractUser):

    username = CharField(
        unique=True, max_length=16,
        error_messages={
            "unique": "Username not available"
        }
    )

    objects = UserManager()
    posted = UserQueryManager()


class Profile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    def get_tag_posts(self, order_by=None):
        tags = Tag.objects.filter(
            question__profile=self
        ).distinct()
        questions_with_tag = self.questions.filter(tags__name=OuterRef("name")).only("id")
        records = tags.annotate(
            times_posted=Count(Subquery(questions_with_tag)),
            avg_question_score=Avg("question__score", output_field=IntegerField())
        )
        if not order_by or order_by not in ['name', 'score']:
            order_by = "name"
        if order_by == "name":
            records = records.order_by(order_by)
        else:
            records = records.order_by("-avg_question_score")
        return {
            'records': records,
            'title': f"{tags.count()} Tags"
        }

    def get_question_posts(self, order_by=None):
        if not order_by or order_by == "newest":
            order_by = "date"
        questions = self.questions.all().order_by(f"-{order_by}")
        return {
            'records': questions,
            'title': f"{questions.count()} Questions"
        }

    def get_answer_posts(self, order_by=None):
        if not order_by or order_by == "newest":
            order_by = "-date"
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
        bookmarks = Bookmark.objects.filter(profile=self)
        if not sort:
            pass
        else:
            if sort == "score":
                bookmarks = bookmarks.order_by("-question__score")
            elif sort == "added":
                bookmarks = bookmarks.order_by("saved")
            else:
                bookmarks = bookmarks.order_by("-question__date")
        return {
            'records': bookmarks,
            'title': f"{bookmarks.count()} bookmarks"
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
