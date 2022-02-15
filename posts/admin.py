from django.contrib import admin
from django.contrib.contenttypes import admin as generic_admin

from .models import Question, Answer, Tag, Vote, QuestionPageHit


class InlineVote(generic_admin.GenericTabularInline):

    model = Vote


class InlineQuestionPageHit(admin.TabularInline):

    model = QuestionPageHit


class AdminPost(admin.ModelAdmin):

    exclude = ("comment", )


class InlineAnswer(admin.StackedInline):

    model = Answer
    classes = ("collapse", )
    readonly_fields = ('question', 'profile', 'body')



class AdminQuestion(AdminPost):

    fields = (('title', 'profile', 'date', "score"), "body", "tags")
    date_heirarchy = "date"
    inlines = [
        InlineAnswer,
        InlineQuestionPageHit
    ]
    filter_horizontal = ("tags", )


class AdminAnswer(AdminPost):

    fields = (('date', 'profile', ), ("question", "score"), "body")


class AdminTag(admin.ModelAdmin):
    pass


class AdminVote(generic_admin.GenericStackedInline):
    pass


class AdminPageHit(admin.ModelAdmin):

    fields = ("question", "address")


admin.site.register(Question, AdminQuestion)
admin.site.register(Answer, AdminAnswer)
admin.site.register(Tag, AdminTag)
