
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from rest_framework.serializers import (
    ModelSerializer, RegexField, CharField
)
from rest_framework.exceptions import ValidationError

from .validators import character_validator



class LoginSerializer(ModelSerializer):

    username = RegexField(
        re.compile("^(_?[a-zA-Z0-9]+_?)+"),
        min_length=6, max_length=20,
        validators=[character_validator]
    )

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
