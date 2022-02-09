from django.db.models import CharField
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    username = CharField(
        unique=True, max_length=16,
        error_messages={
            "unique": "Username not available"
        }
    )
