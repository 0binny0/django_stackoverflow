
from datetime import date, timedelta
from functools import reduce

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import (
    Model, ManyToManyField, ForeignKey, CASCADE, SET_NULL, CharField,
     TextField, PositiveIntegerField, IntegerField, DateField, BooleanField,
     GenericIPAddressField, Manager, OuterRef, Subquery, Count, F,
     UniqueConstraint, QuerySet, Q
)
from django.urls import resolve

from django.contrib.contenttypes.fields import (
    GenericForeignKey,  GenericRelation
)
from django.contrib.contenttypes.models import ContentType

from .utils import resolve_search_query


class QueryStringSearchManager(Manager):

    def lookup(self, tab, query=None):
        qs_options = {
            f"{self.unanswered.__name__}": self.unanswered,
            f"{self.active.__name__}": self.active,
            f"{self.newest.__name__}": self.newest,
            f"{self.score.__name__}": self.score
        }
        current_tab = tab.lower()
        if current_tab not in ['unanswered', 'active', 'newest', 'score']:
            current_tab = "newest"
        queryset = super().get_queryset().order_by("-date", "views", "-score")
        if query:
            query_data = resolve_search_query(query)
            if 'tags' in query_data and query_data['tags']:
                q_objects = map(
                    lambda tag: Q(name__iexact=tag), query_data['tags']
                )
                query = reduce(lambda q1, q2: q1 & q2, q_objects)
                tags = Tag.objects.filter(query)
                queryset = queryset.filter(tags__in=tags).distinct()
            if 'title' in query_data and query_data['title']:
                queryset = queryset.filter(title__contains=f"{query_data['title']}")
            if 'user' in query_data and query_data['user']:
                queryset = queryset.filter(profile_id=query_data['user'])
            queryset = qs_options.get(f"{tab}", "_newest")(queryset)
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
        return qs.filter(score__gte=0)


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
        if not isinstance(user, get_user_model()):
            return Question.objects.all()
        selected_tab = tab.lower()
        if selected_tab not in ['interesting', 'hot', 'week', 'month']:
            selected_tab = "interesting"
        return qs_options.get(selected_tab, "interesting")(user.profile)

    def interesting(self, profile):
        return self.get_queryset().filter(
            tags__name__in=profile.questions.values_list(
                "tags__name", flat=True
            )
        )

    def hot(self, profile):
        today = date.today()
        days_ago = today - timedelta(days=3)
        return self.get_queryset().filter(
            date__range=(days_ago, today)
        ).filter(
            tags__name__in=profile.questions.filter(
                date__range=(days_ago, today)
            ).values_list("tags__name", flat=True)
        ).distinct()

    def week(self, profile):
        today = date.today()
        weekago = today - timedelta(days=7)
        return self.get_queryset().filter(
            date__range=(weekago, today)
        ).filter(
            tags__name__in=profile.questions.values_list(
                "tags__name", flat=True
            )
        ).distinct()

    def month(self, profile):
        today = date.today()
        monthago = today - timedelta(days=31)
        return self.get_queryset().filter(
            date__range=(monthago, today)
        ).filter(
            tags__name__in=profile.questions.values_list(
                "tags__name", flat=True
            )
        ).distinct()


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

    question = ForeignKey("Question", on_delete=CASCADE, related_name="_views")
    profile = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    address = GenericIPAddressField()


    class Meta:
        managed = True
        db_table = "questionpagehit"


class Bookmark(Model):
    question = ForeignKey("Question", on_delete=CASCADE, related_name="bookmarks")
    profile = ForeignKey(
        "authors.Profile", on_delete=CASCADE, related_name="bookmarks"
    )


    class Meta:
        managed = True
        db_table = "bookmark"
