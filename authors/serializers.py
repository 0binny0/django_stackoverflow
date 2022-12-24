
import re

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password as review_user_password
from django.contrib.auth.hashers import check_password
from django.core.validators import RegexValidator
# from django.core.exceptions import ValidationError

from rest_framework.serializers import (
    ModelSerializer, BaseSerializer, RegexField, CharField, ReadOnlyField
)
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from .validators import character_validator, total_digits_validator


class LoginSerializer(ModelSerializer):

    username = CharField()
    password = CharField()

    def validate_username(self, value):
        try:
            user = self.Meta.model.objects.get(username=value)
        except self.Meta.model.DoesNotExist:
            msg = "No account registered with that username"
            raise ValidationError(msg)
        return value

    def validate(self, data):
        username_provided = data.get("username", None)
        password_provided = data.get("password", None)
        if username_provided:
            username = self.validate_username(username_provided)
            user = get_user_model().objects.get(username=username)
            if password_provided:
                pass_match = check_password(data['password'], user.password)
                if not pass_match:
                    raise ValidationError(
                        {"password": "Password mismatch"},
                        code="invalid_password"
                    )
            return data
        raise ValidationError({"password": "No username provided"})


    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterSerializer(ModelSerializer):

    username = RegexField(
        re.compile("^(_?[a-zA-Z0-9]+)+"),
        required=False,
        min_length=6, max_length=20,
        validators=[
            character_validator, total_digits_validator,
            UniqueValidator(get_user_model().objects.all())
        ]
    )

    password = CharField(
        required=False,
        min_length=7, max_length=12,
        validators=[RegexValidator("[<>`':;,.\"]", inverse_match=True)]
    )

    password2 = CharField(
        required=False,
        min_length=7, max_length=12,
        validators=[RegexValidator("[<>`':;,.\"]", inverse_match=True)]
    )

    def validate_password(self, value):
        try:
            password = review_user_password(value)
        except ValidationError:
            password2_value = self.initial_data.get("password2")
            if password2_value and value != password2_value:
                raise ValidationError(
                    {"non_field_errors": "password confirmation failed"}
                )
            else:
                raise
        return value


    def validate(self, data):
        username, password, password2 = [
            data[key].lower().strip() if data.get(key) else None for key in [
                "username", "password", "password2"
            ]
        ]
        if len(data) == 3 and (username == password
                        and username == password2 and password == password2):
                raise ValidationError(
                    {"non_field_errors": "registration failed"}
                )
        elif password != password2 and (len(data) == 3 or (len(data) == 2 and not username)):
                raise ValidationError(
                    {"non_field_errors": "password confirmation failed"}
                )
        elif username == password:
            raise ValidationError({"non_field_errors": "password cannot be username"})
        return data

    class Meta:
        model = get_user_model()
        fields = ["username", "password", "password2"]


class UserListingSerializer(BaseSerializer):

    def to_representation(self, instance):
        object = {
            'name': str(instance),
            'profile': {
                'url': reverse("authors:profile", kwargs={"id": instance.id}),
                'total_posts': instance.post_count,
                'date_joined': instance.date_joined,
                'last_login': instance.last_login
            }
        }
        return object
