
from django.forms import ModelForm, CharField
from django.forms.widgets import TextInput, Textarea

from .models import Question


class QuestionForm(ModelForm):

    body = CharField(
        widget=Textarea(attrs={"class": "question_input_field"}),
        min_length=50,
        help_text="Clarify your question with as much detail as possible",
        error_messages={
            'required': "Elaborate on your question",
            'min_length': "Add more info to your question"
        }
    )

    tags = CharField(widget=TextInput(
        attrs={"required": False, "class": "question_input_field"}
    ), help_text="Add up to 4 tags for your question")


    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']
