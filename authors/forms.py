
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class RegisterUserForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for label, field in self.fields.items():
            field.widget.attrs.update(
                {"class": "widget_style user_form_input"}
            )
            if label == "password2":
                field.widget.attrs.update({"disabled": True})


class LoginUserForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for label, field in self.fields.items():
            field.widget.attrs.update(
                {"class": "widget_style user_form_input"}
            )
