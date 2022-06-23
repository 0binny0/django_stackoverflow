from django.db.models import (
    Model, OneToOneField, ForeignKey, CharField, CASCADE
)
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Manager, Count, Subquery, OuterRef, F

from posts.models import Question, Tag


from posts.models import Question, Answer

class User(AbstractUser):

    username = CharField(
        unique=True, max_length=16,
        error_messages={
            "unique": "Username not available"
        }
    )


class Profile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    def get_tag_posts(self):
        questions_with_tag = self.questions.filter(
            tags__name=OuterRef("name")).only("id")
        return Tag.objects.filter(
            question__profile_id=self
        ).distinct().order_by("name").annotate(
            count=Count(Subquery(questions_with_tag))
        )

    def get_question_posts(self):
        return self.questions.all()

    def get_answer_posts(self):
        return self.answers.all()

    def get_bookmarked_posts(self):
        pass
    # def has_voted(self, post, type):
    #     if isinstance(post, Question):
    #         (vote, created) = Vote.objects.get_or_create(
    #             question=post, profile=post.profile
    #         ).exists()
    #     else:
    #         if isinstance(post, Answer):
    #             (vote, created) = Vote.objects.get_or_create(
    #                 answer=post, profile=post.profile
    #             ).exists()
    #     return (vote, created)

    class Meta:
        permissions = [("can vote", "Can vote")]
