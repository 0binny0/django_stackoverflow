
import re

from django.contrib.auth import get_user_model

from rest_framework.serializers import (
    ModelSerializer, RegexField
)

from .validators import character_validator



class LoginSerializer(ModelSerializer):

    username = RegexField(
        re.compile("^(_?[a-zA-Z0-9]+_?)+"), min_length=6, max_length=20,
        validators=[character_validator]
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
