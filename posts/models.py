
from datetime import datetime, timedelta
from functools import reduce

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import (
    Model, ManyToManyField, ForeignKey, CASCADE, SET_NULL, CharField,
     TextField, PositiveIntegerField, IntegerField, DateField, DateTimeField, BooleanField,
     GenericIPAddressField, Manager, OuterRef, Subquery, Count, F,
     UniqueConstraint, QuerySet, Q
)
from django.urls import resolve
from django.utils import timezone
from django.contrib.contenttypes.fields import (
    GenericForeignKey,  GenericRelation
)
from django.contrib.contenttypes.models import ContentType

import pytz

from .utils import resolve_search_query


class QueryStringSearchManager(Manager):

    def lookup(self, tab, query=None):
        qs_options = {
            f"{self.unanswered.__name__}": self.unanswered,
            f"{self.newest.__name__}": self.newest,
            f"{self.score.__name__}": self.score
        }
        current_tab = tab.lower()
        if current_tab not in qs_options.keys():
            current_tab = "newest"
        queryset = super().get_queryset().order_by("-date", "views", "-score")
        if query:
            query_data = resolve_search_query(query)
            if 'tags' in query_data and query_data['tags']:
                '''Combining many Q() objects and passing into query'''
                # https://docs.djangoproject.com/en/4.2/topics/db/queries/#complex-lookups-with-q-objects
                q_objects = map(
                    lambda tag: Q(name__iexact=tag), query_data['tags']
                )
                tab_query = reduce(lambda q1, q2: q1 | q2, q_objects)
                tags = Tag.objects.filter(tab_query)
                if tags.count() != len(tab_query):
                    return [], query_data
                else:
                    for tag in tags:
                        _queryset = queryset.filter(tags__name=str(tag)).distinct()
                        queryset = _queryset
            if 'title' in query_data and query_data['title']:
                queryset = queryset.filter(title__contains=f"{query_data['title']}")
            if 'user' in query_data and query_data['user']:
                queryset = queryset.filter(profile_id=query_data['user'])
            if 'phrases' in query_data and query_data['phrases']:
                q_objects = map(lambda phrase: Q(body__contains=phrase), query_data['phrases'])
                phrase_query = reduce(lambda q1, q2: q1 | q2, q_objects)
                queryset = queryset.filter(phrase_query)
            queryset = qs_options.get(f"{current_tab}", "newest")(queryset)
            return queryset, query_data
        queryset = qs_options.get(current_tab, "newest")(queryset)
        return queryset, None

    def unanswered(self, qs):
        return qs.annotate(
            total_answers=Count('answer')
        ).filter(total_answers__exact=0)

    def active(self, qs):
        return qs.annotate(
            total_answers=Count("answer")
        ).filter(total_answers__gt=0)

    def newest(self, qs):
        return qs

    def score(self, qs):
        return qs.filter(score__gte=0).order_by("date", "vote")


class QuestionSearchManager(Manager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("tags")
        return queryset.annotate(
            answer_tally=Count('answer')
        ).order_by("-date", "views", "-score")

    def lookup(self, user, tab="interesting"):
        qs_options = {
            f"{self.interesting.__name__}": self.interesting,
            f"{self.hot.__name__}": self.hot,
            f"{self.week.__name__}": self.week,
            f"{self.month.__name__}": self.month,
        }
        selected_tab = tab.lower()
        tabs = list(qs_options.keys())
        if selected_tab not in tabs:
            selected_tab = tabs[0]
        return qs_options.get(selected_tab, "interesting")(user)

    def interesting(self, user):
        if not hasattr(user, 'profile'):
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(
                tags__name__in=user.profile.questions.values_list(
                    "tags__name", flat=True
                )
            )
        return queryset

    def hot(self, user):
        today = datetime.now(pytz.utc)
        days_ago = today - timedelta(days=3)
        if not hasattr(user, 'profile'):
            queryset = self.get_queryset().filter(
                date__range=(days_ago, today)
            )
        else:
            queryset = self.get_queryset().filter(
                date__range=(days_ago, today)
            ).filter(
                tags__name__in=user.profile.questions.filter(
                    date__range=(days_ago, today)
                ).values_list("tags__name", flat=True)
            ).distinct()
        return queryset

    def week(self, user):
        today = datetime.now(pytz.utc)
        weekago = today - timedelta(days=7)
        if not hasattr(user, 'profile'):
            queryset = self.get_queryset().filter(
                date__range=(weekago, today)
            )
        else:
            queryset = self.get_queryset().filter(
                date__range=(weekago, today)
            ).filter(
                tags__name__in=user.profile.questions.values_list(
                    "tags__name", flat=True
                )
            ).distinct()
        return queryset

    def month(self, user):
        today = datetime.now(pytz.utc)
        monthago = today - timedelta(days=31)
        if not hasattr(user, 'profile'):
            queryset = self.get_queryset().filter(
                date__range=(monthago, today)
            )
        else:
            queryset = self.get_queryset().filter(
                date__range=(monthago, today)
            ).filter(
                tags__name__in=user.profile.questions.values_list(
                    "tags__name", flat=True
                )
            ).distinct()
        return queryset


class Tag(Model):

    name = CharField(unique=True, max_length=25)


    class Meta:
        managed = True
        db_table = "tag"


    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return f"/questions/posted/{self.name}"


class Post(Model):

    body = TextField()
    date = DateTimeField(default=timezone.now)
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
        managed = True


class Question(Post):

    title = CharField(
        max_length=80, unique_for_date="date",
        help_text="Concisely state the problem you're having",
        error_messages={
            "max_length": "The title of your question is too long"
        }
    )
    tags = ManyToManyField(
        'Tag', related_name="questions", related_query_name="question"
    )
    views = IntegerField(default=0)
    visible = BooleanField(default=True)
    objects = Manager()
    postings = QuestionSearchManager()
    searches = QueryStringSearchManager()

    def __str__(self):
        return self.title


    class Meta(Post.Meta):
        db_table = "question"
        ordering = ["-score" , "-date"]
        constraints = [UniqueConstraint(fields=[
            'title', 'date', 'profile'
        ], name="duplicated_post_by_date")]


    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title})"


class Answer(Post):
    question = ForeignKey(
        "Question", on_delete=CASCADE,
        related_name="answers", related_query_name="answer"
    )


    class Meta(Post.Meta):
        db_table = "answer"


class Comment(Post):

    comment = None


    class Meta(Post.Meta):
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

    # def save(self, *args, **kwargs):
    #     post = self.content_object
    #     if self.type == "like":
    #         post.score = F("score") + 1
    #     else:
    #         post.score = F("score") - 1
    #     post.save(update_fields=['score'])
    #     post.refresh_from_db()
    #     super().save(*args, **kwargs)


    class Meta:
        managed = True
        db_table = "vote"


class QuestionPageHit(Model):

    question = ForeignKey("Question", on_delete=CASCADE, related_name="page_hits")
    profile = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    address = GenericIPAddressField()


    class Meta:
        managed = True
        db_table = "questionpagehit"


class Bookmark(Model):
    question = ForeignKey("Question", on_delete=CASCADE, related_name="bookmarks", related_query_name="bookmark")
    profile = ForeignKey(
        "authors.Profile", on_delete=CASCADE, related_name="bookmarks"
    )
    saved = DateField(default=timezone.now)


    class Meta:
        managed = True
        db_table = "bookmark"
