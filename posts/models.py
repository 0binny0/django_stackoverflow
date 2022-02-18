
from datetime import date, timedelta

from django.db.models import (
    Model, ManyToManyField, ForeignKey, CASCADE, SET_NULL, CharField,
     TextField, PositiveIntegerField, IntegerField, DateField,
     GenericIPAddressField, Manager, OuterRef, Subquery, Count, F
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
        return queryset.annotate(
            answer_tally=Count('answer')
        ).order_by("-date", "views", "-score")


    def interesting(self, profile):
        return self.get_queryset().filter(
            tags__name__in=profile.questions.values_list(
                "tags__name", flat=True
            )
        )

    def recent(self, profile):
        today = date.today()
        days_ago = today - timedelta(days=3)
        return self.get_queryset().filter(
            date__range=(days_ago, today)
        ).filter(
            tags__name__in=profile.questions.filter(
                date__range=(days_ago, today)
            ).values_list("tags__name", flat=True)
        ).distinct()

    def by_week(self, profile):
        today = date.today()
        weekago = today - timedelta(days=7)
        return self.get_queryset().filter(
            date__range=(weekago, today),
        ).filter(
            tags__name__in=profile.questions.filter(
                date__range=(weekago, today)
            ).values_list("tags__name", flat=True)
        ).distinct()

    def by_month(self, profile):
        today = date.today()
        monthago = today - timedelta(days=31)
        return self.get_queryset().filter(
            date__range=(monthago, today)
        ).filter(
            tags__name__in=profile.questions.values_list(
                "tags__name", flat=True
            )
        ).distinct()

    def unanswered(self):
        return self.get_queryset().filter(answer__isnull=True)



class Tag(Model):

    name = CharField(unique=True, max_length=25)


    class Meta:
        db_table = "tag"


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

    title = CharField(max_length=75, unique_for_date="date")
    tags = ManyToManyField(
        'Tag', related_name="questions", related_query_name="question"
    )
    views = IntegerField(default=0)
    objects = Manager()
    postings = QuestionSearchManager()


    class Meta:
        db_table = "question"
        ordering = ["-score" , "-date"]


    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title})"


class Answer(Post):
    question = ForeignKey(
        "Question", on_delete=CASCADE,
        related_name="answers", related_query_name="answer"
    )


    class Meta:
        db_table = "answer"


class Comment(Post):

    comment = None


    class Meta:
        db_table = "comment"



class Vote(Model):

    profile = ForeignKey(
        'authors.Profile', on_delete=SET_NULL, null=True,
        related_name="votes"
    )
    type = CharField(max_length=7)
    content_type = ForeignKey(ContentType, on_delete=CASCADE)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey()

    def save(self, *args, **kwargs):
        post = self.content_object
        if self.type == "like":
            post.score = F("score") + 1
        else:
            post.score = F("score") - 1
        post.save(update_fields=['score'])
        post.refresh_from_db()
        super().save(*args, **kwargs)


    class Meta:
        db_table = "vote"


class QuestionPageHit(Model):

    question = ForeignKey("Question", on_delete=CASCADE, related_name="_views")
    address = GenericIPAddressField()


    class Meta:
        db_table = "questionpagehit"


class Bookmark(Model):
    question = ForeignKey("Question", on_delete=CASCADE)
    profile = ForeignKey(
        "authors.Profile", on_delete=CASCADE, related_name="bookmarks"
    )


    class Meta:
        db_table = "bookmark"
