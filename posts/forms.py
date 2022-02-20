
from django.forms import ModelForm, CharField
from django.forms.widgets import TextInput

from .models import Question


class QuestionForm(ModelForm):

    tags = CharField(widget=TextInput(
        attrs={"required": False}
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for label, field in self.fields.items():
            field.widget.attrs.update({"class": "question_input_field"})
            if label == "tags":
                field.widget.attrs.update({"required": False})


    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']
