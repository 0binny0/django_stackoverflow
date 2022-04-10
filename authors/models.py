from django.db.models import (
    Model, OneToOneField, ForeignKey, CharField, CASCADE
)
from django.contrib.auth.models import AbstractUser
from django.conf import settings


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

    def has_voted(self, post, type):
        if isinstance(post, Question):
            (vote, created) = Vote.objects.get_or_create(
                question=post, profile=post.profile
            ).exists()
        else:
            if isinstance(post, Answer):
                (vote, created) = Vote.objects.get_or_create(
                    answer=post, profile=post.profile
                ).exists()
        return (vote, created)
