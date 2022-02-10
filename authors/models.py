from django.db.models import (
    Model, OneToOneField, ForeignKey, CharField, CASCADE
)
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):

    username = CharField(
        unique=True, max_length=16,
        error_messages={
            "unique": "Username not available"
        }
    )


class Profile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE)
