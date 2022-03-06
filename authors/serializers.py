
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.validators import RegexValidator

from rest_framework.serializers import (
    ModelSerializer, RegexField, CharField
)
from rest_framework.exceptions import ValidationError

from .validators import character_validator, total_digits_validator


class LoginSerializer(ModelSerializer):

    username = CharField(min_length=6, max_length=20)
    password = CharField(max_length=7, min_length=12)

    def validate(self, data):
        username_provided = data.get("username", None)
        password_provided = data.get("password", None)
        if username_provided:
            try:
                user = self.Meta.model.objects.get(username=data['username'])
            except self.Meta.model.DoesNotExist:
                msg = "No account registered with that username"
                raise ValidationError({"username": msg})
            else:
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
        re.compile("^(_?[a-zA-Z0-9]+_?)+"),
        min_length=6, max_length=20,
        validators=[character_validator, total_digits_validator]
    )

    password = CharField(
        min_length=7, max_length=12,
        validators=[RegexValidator("[<>`':;,.\"]", inverse_match=True)]
    )

    password2 = CharField(
        min_length=7, max_length=12,
        validators=[RegexValidator("[<>`':;,.\"]", inverse_match=True)]
    )


    def validate(self, data):
        username, password, password2 = [
            data.get("username", None), data.get("password", None),
            data.get("password2", None)
        ]
        if len(data) == 3 and (username == password
                        and username == password2 and password == password2):
                raise ValidationError(
                    {"non_field_errors": "registration failed"}
                )
        elif (len(data) == 3 or (len(data) == 2 and not username)
                                                and password != password2):
                raise ValidationError(
                    {"non_field_errors": "password confirmation failed"}
                )
        elif username == password:
            raise ValidationError({"password2": "password cannot be username"})
        return data

    class Meta:
        model = get_user_model()
        fields = ["username", "password", "password2"]
