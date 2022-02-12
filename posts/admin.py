from django.contrib import admin

from .models import Question, Answer, Tag

# class InlineAnswer(admin.StackedInline):
#     model = Answer
#     fieldsets = (
#         "Answers", {
#             "fields": (("date", "profile", "score"), "body"),
#             "classes": ("collapse", )
#         }
#     )
    #

class AdminTag(admin.ModelAdmin):

    fields = ('name',)


class AdminQuestion(admin.ModelAdmin):

    actions_on_bottom = False
    actions_on_bottom = True

    fieldsets = (
        (
            None, {
                "fields": (("title", "profile", "date"), "tags", "body")
            }
        ),
    )
    exclude = ("comment", )
    # readonly_fields = ("title", "body", "tags", "profile")

    # inlines = [
    #     InlineAnswer,
    # ]


admin.site.register(Question, AdminQuestion)
admin.site.register(Tag, AdminTag)
# admin.site.register(Answer, InlineAnswer)
