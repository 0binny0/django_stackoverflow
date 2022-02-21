
from .models import Tag

from rest_framework.serializers import ModelSerializer,  ListField
from rest_framework.exceptions import ValidationError


class TagSerializer(ModelSerializer):

    name = ListField()

    def validate_name(self, value):
        if len(value) > 4:
            raise ValidationError("Tag limit exceeded: 4 tags per question")
        return value


    class Meta:
        model = Tag
        fields = ('name', )
