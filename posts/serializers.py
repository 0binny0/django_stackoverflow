
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.contrib.auth import get_user_model

from .models import Vote, Question, Answer

from rest_framework.serializers import ModelSerializer, BaseSerializer
from rest_framework.exceptions import ValidationError


class VoteSerializer(ModelSerializer):

    def validate_profile(self, value):
        if self.context['post'].profile.id == value.id:
            raise ValidationError("You cannot vote on your post")
        return value

    def create(self, validated_data):
        post = self.context['post']
        if self.context['vote_type'] == "dislike":
            post.score = F("score") - 1
        else:
            post.score = F("score") + 1
        post.save()
        post.refresh_from_db()
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data['type']
        instance.save()
        post = self.context['post']
        if validated_data['type'] == "dislike":
            post.score = F("score") - 2
        else:
            post.score = F("score") + 2
        post.save()
        post.refresh_from_db()
        return instance


    class Meta:
        model = Vote
        fields = ['type', 'profile']


class CurrentPostStateSerializer(BaseSerializer):

    def to_representation(self, instance):
        if isinstance(self.context['request'].user, get_user_model()):
            user_profile = self.context['request'].user.profile
            question_voted_on = instance.vote.filter(
                profile=user_profile
            ).exists()
            answers_voted_on = instance.answers.exclude(
                profile=user_profile
            ).filter(vote__profile=user_profile)
            is_bookmarked = instance.bookmarks.filter(
                profile=user_profile
            ).exists()
            data = {
                "question_id": instance.id,
                "vote": question_voted_on,
                "bookmark": is_bookmarked,
                "answers": [
                    {"id": answer.id, "vote": answer.vote.get(
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
