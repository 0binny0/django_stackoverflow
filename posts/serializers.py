
from django.contrib.contenttypes.models import ContentType

from .models import Vote, Question, Answer

from rest_framework.serializers import ModelSerializer,  ListField, HiddenField, CurrentUserDefault, SerializerMethodField
from rest_framework.exceptions import ValidationError


class VoteSerializer(ModelSerializer):

    def validate_type(self, value):
        user_vote = self.instance.vote.get(
            profile=self.context['request'].user.profile
        )
        if user_vote.type == value:
            raise ValidationError
        return value

    def validate_profile(self, value):
        if self.instance.profile.id == value.id:
            raise ValidationError("You cannot vote on your post")
        return value

    def create(self, validated_data):
        return self.Meta.model.objects.crate(**validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data['type']
        instance.save()
        return instance


    class Meta:
        model = Vote
        fields = ['type', 'profile']
