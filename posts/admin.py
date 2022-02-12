from django.contrib import admin
from django.contrib.contenttypes import admin as generic_admin

from .models import Question, Answer, Tag, Vote, QuestionPageHit


class InlineVote(generic_admin.GenericTabularInline):

    model = Vote


class InlineQuestionPageHit(admin.TabularInline):

    model = QuestionPageHit


class AdminPost(admin.ModelAdmin):

    exclude = ("comment", )
    inlines = [
        InlineAdminVote
    ]


class InlineAnswer(admin.StackedInline):

    model = Answer
    classes = ("collapse", )
    readonly_fields = ('question', 'profile', 'body')



class AdminQuestion(AdminPost):

    fields = (('title', 'profile', 'date', ), "body", "tags")
    # raw_id_fields = ('tags', )
    inlines = [
        InlineAnswer,
        InlineVote,
        InlineQuestionPageHit
    ]
    filter_horizontal = ("tags", )


class AdminAnswer(AdminPost):

    fields = (('date', 'profile', ), "question", "body")


class AdminTag(admin.ModelAdmin):
    pass


class AdminVote(generic_admin.GenericStackedInline):
    pass


class AdminPageHit(admin.ModelAdmin):

    fields = ("question", "address")


admin.site.register(Question, AdminQuestion)
admin.site.register(Answer, AdminAnswer)
admin.site.register(Tag, AdminTag)
