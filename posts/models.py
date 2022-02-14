
from datetime import date, timedelta

from django.db.models import (
    Model, ManyToManyField, ForeignKey, CASCADE, SET_NULL, CharField,
     TextField, PositiveIntegerField, IntegerField, DateField,
     GenericIPAddressField, Manager, OuterRef, Subquery
)

from django.contrib.contenttypes.fields import (
    GenericForeignKey,  GenericRelation
)
from django.contrib.contenttypes.models import ContentType


class QuestionSearchManager(Manager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            tags__name__in=profile.questions.values_list(
                "tags__name", flat=True
            )
        ).distinct()

    def by_week(self, profile):
        today = date.today()
        weekago = today - timedelta(days=7)
        return self.get_queryset().filter(
            date__range=(weekago, today)
        )


    def by_month(self, profile):
        queryset = self.by_week(profile)
        return queryset.filter()



class Tag(Model):

    name = CharField(unique=True, max_length=25)


class Post(Model):

    body = TextField()
    date = DateField(default=date.today)
    comment = ForeignKey('Comment', on_delete=CASCADE, null=True)
    profile = ForeignKey(
        'authors.Profile', on_delete=SET_NULL, null=True,
        related_name='%(class)ss',
        related_query_name="%(class)s"
    )
    vote = GenericRelation(
        'Vote', related_query_name="%(class)s"
    )
    score = IntegerField(default=0)


    class Meta:
        abstract = True


class Question(Post):

    title = CharField(max_length=75)
    tags = ManyToManyField(
        'Tag', related_name="questions", related_query_name="question"
    )
    objects = Manager()
    postings = QuestionSearchManager()


    class Meta:
        ordering = ["-score" , "-date"]


class Answer(Post):
    question = ForeignKey(
        "Question", on_delete=CASCADE,
        related_name="answers", related_query_name="answer"
    )


class Comment(Post):

    comment = None


class Vote(Model):

    profile = ForeignKey(
        'authors.Profile', on_delete=SET_NULL, null=True,
        related_name="votes"
    )
    type = CharField(max_length=7)
    content_type = ForeignKey(ContentType, on_delete=CASCADE)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey()


class QuestionPageHit(Model):

    question = ForeignKey("Question", on_delete=CASCADE, related_name="views")
    address = GenericIPAddressField()


class Bookmark(Model):
    question = ForeignKey("Question", on_delete=CASCADE)
    profile = ForeignKey(
        "authors.Profile", on_delete=CASCADE, related_name="bookmarks"
    )
