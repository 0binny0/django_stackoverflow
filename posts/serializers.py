
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.contrib.auth import get_user_model

from .models import Vote, Question, Answer

from rest_framework.serializers import ModelSerializer, BaseSerializer
from rest_framework.exceptions import ValidationError


class VoteSerializer(ModelSerializer):

    def validate_profile(self, value):
        try:
            get_user_model().objects.get(id=value.id)
        except get_user_model().DoesNotExist:
            raise ValidationError("Please login to vote")
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
        vote = self.context['type']
        instance.type = vote
        instance.save()
        post = self.context['post']
        if vote == "dislike":
            post.score = F("score") - 2
        else:
            post.score = F("score") + 2
        post.save()
        post.refresh_from_db()
        return instance


    class Meta:
        model = Vote
        fields = ['profile']


class CurrentPostStateSerializer(BaseSerializer):

    def to_representation(self, instance):
        '''Returns a dictionary that represents a question resource.
        It includes a property which indicates whether the aforementioned
        resource and its associated answers have been voted on.'''
        user = self.context['request'].user
        if isinstance(user, get_user_model()):
            question_voted_on = instance.vote.filter(
                profile=user.profile
            ).exists()
            answers_voted_on = instance.answers.exclude(
                profile=user.profile
            ).filter(vote__profile=user.profile)
            is_bookmarked = instance.bookmarks.filter(
                profile=user.profile
            ).exists()
            data = {
                "question_id": instance.id,
                "vote": question_voted_on,
                "bookmark": is_bookmarked,
                "answers": [
                    {"id": answer.id, "vote": answer.vote.get(
                        profile=user.profile
                    ).type}
                    for answer in answers_voted_on
                ] if answers_voted_on else None
            }
            if user.profile == instance.profile:
                data.update({"vote": False})
            elif question_voted_on:
                data.update({
                    "vote": instance.vote.get(profile=user.profile).type
                })
            return data
        return {'question_id': instance.id, 'vote': False}
