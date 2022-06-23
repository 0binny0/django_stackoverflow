

from django.forms import Form, ModelForm, CharField, MultiValueField
from django.forms.widgets import TextInput, Textarea, MultiWidget
from django.core.validators import RegexValidator

from .models import Question, Answer

class MultiTagWidget(MultiWidget):

    def __init__(self, *args, **kwargs):
        widgets = [TextInput(attrs=kwargs['attrs']) for i in range(4)]
        for i, w in enumerate(widgets):
            w.attrs.update({"placeholder": f"Tag {i}"})
        super().__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if not value:
            return ["", "", "", ""]
        return value


class TagField(MultiValueField):

    def __init__(self, *args, **kwargs):
        fields = []
        for i in range(4):
            field = CharField(**{
                "min_length": 1, "max_length": 25, "validators":[
                    RegexValidator("[<>`':;,.\"]", inverse_match=True)
                ]
            })
            if i == 0:
                field.error_messages = {
                    'incomplete': "Provide at least 1 tag for your question"
                }
                field.required = True
            else:
                field.required = False
            fields.append(field)
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        field_values = list(set([data.strip() for data in data_list if data]))
        return field_values


class PostingForm(ModelForm):

    body = CharField(
        widget=Textarea(
            attrs={
                "class": "question_input_shade fill_block_width adjust_box"
            }
        ), min_length=50
    )

    class Meta:
        model = None
        fields = ['body']


class QuestionForm(PostingForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].help_text = "Clarify your question with as much detail as possible"
        self.fields['body'].error_messages={
                'required': "Elaborate on your question",
                'min_length': "Add more info to your question"
            }

    title = CharField(
        min_length=20, max_length=80,
        widget=TextInput({"class": "question_input_shade fill_block_width"}),
        error_messages={
            "min_length": "Elaborate on your question title",
            "max_length": "The title of your question is too long"
        },
        help_text="Concisely describe the issue"
    )

    tags = TagField(
        widget=MultiTagWidget(
            attrs={
                "min_length": 1, "max_length": 25,
                "class": "question_input_shade inline_tag_input"
            }
        ), require_all_fields=False,
        help_text="Add up to 4 tags for your question"
    )

    def __str__(self):
        return f"{self.__class__.__name__}".lower()

    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']


class SearchForm(Form):

    q = CharField(widget=TextInput(
        attrs={
            "placeholder": "Search...", "class": "search_query_widget grey-outline",
            "autocomplete": "off"
        }
    ))


class AnswerForm(PostingForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].help_text = "Provide you knowledge relating to the topic here"
        self.fields['body'].error_messages = {
            'required': "No answer provided",
            'min_length': "Add more info to your answer"
        }


    class Meta:
        model = Answer
        fields = ['body', ]
