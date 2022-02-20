
from django.forms import Form, CharField
from django.forms.widgets import TextInput, Textarea


class QuestionForm(Form):

    title = CharField(
        max_length=55, widget=TextInput({"class": "question_input_field"}),
        error_messages={"max_length": "The title of your question is too long"}
    )

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
        attrs={"class": "question_input_field"}
    ), required=False, help_text="Add up to 4 tags for your question")
