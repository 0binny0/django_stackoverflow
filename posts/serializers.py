
from django.contrib.contenttypes.models import ContentType

from .models import Vote, Question, Answer

from rest_framework.serializers import ModelSerializer, BaseSerializer
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
        if self.context['post'].profile.id == value.id:
            raise ValidationError("You cannot vote on your post")
        return value

    def create(self, validated_data):
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data['type']
        instance.save()
        return instance


    class Meta:
        model = Vote
        fields = ['type', 'profile']


class CurrentPostStateSerializer(BaseSerializer):

    def to_representation(self, instance):
        user_profile = self.context['request'].user.profile
        question_voted_on = instance.vote.filter(profile=user_profile).exists()
        answers_voted_on = instance.answers.exclude(profile=user_profile).filter(
            vote__profile=user_profile
        )
        is_bookmarked = instance.bookmarks.filter(profile=user_profile).exists()
        data = {
            "question_id": instance.id,
            "vote": question_voted_on,
            "bookmark": is_bookmarked,
            "answers": [
                {"id": instance.id, "vote": answer.vote.get(
                    profile=user_profile
                ).type}
                for answer in answers_voted_on
            ] if answers_voted_on else None
        }
        if user_profile == instance.profile:
            data.update({"vote": False})
        elif question_voted_on:
            data.update({
                "vote": instance.vote.get(profile=user_profile).type
            })
        return data
