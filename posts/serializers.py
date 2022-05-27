
from django.contrib.contenttypes.models import ContentType

from .models import Vote, Question, Answer

from rest_framework.serializers import ModelSerializer,  ListField
from rest_framework.exceptions import ValidationError

class QuestionSerializer(ModelSerializer):

    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']


class AnswerSerializer(ModelSerializer):

    class Meta:
        model = Answer
        fields = ['body']


class VoteSerializer(ModelSerializer):

    def validate_type(self, value):
        vote_selection, resource_url = self.initial_data.values()
        models = {
            'questions': Question,
            'answers': Answer
        }
        voted_model_type, id = resource_url.split("/")[:2]
        model_content_type = ContentType.objects.get_for_model(
            models[voted_model_type]
        )
        try:
            post = model_content_type.get_object_for_this_type(
                id=id, vote__profile=self.context['request'].user.profile
            )
        except model_content_type.model_class().DoesNotExist:
            return value
        else:
            user_vote = post.vote.get(
                profile=self.context['request'].user.profile
            )
            if user_vote.type == value:
                raise ValidationError
            return value

    class Meta:
        model = Vote
        fields = ['type']
