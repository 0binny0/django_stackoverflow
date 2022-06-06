
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser

from rest_framework.views import APIView
from rest_framework.status import (
    HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
)
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .models import Question, Answer, Vote
from .serializers import VoteSerializer


class UserVoteEndpoint(APIView):

    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def retrieve_user_post(self, id, model):
        models = {
            'question': Question,
            'answer': Answer
        }
        model_content_type = ContentType.objects.get_for_model(
            models[model]
        )
        post = model_content_type.get_object_for_this_type(id=id)
        return post

    def post(self, request, id):
        if isinstance(request.user, AnonymousUser):
            return Response(status=HTTP_400_BAD_REQUEST)
        post = self.retrieve_user_post(id, request.data.pop("post"))
        serializer = VoteSerializer(data={'profile': request.user.profile.id},
            context={'request': request, 'post': post}, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            x = serializer.save(
                profile=request.user.profile, type=request.data["type"],
                content_object=post
            )
            return Response(status=HTTP_201_CREATED)

    def put(self, request, id):
        post = self.retrieve_user_post(id, request.data.pop("post"))
        serializer = VoteSerializer(
            instance=post, data=request.data,
            context={'request': request}, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=HTTP_204_NO_CONTENT)

    def delete(self, request, id):
        post = self.retrieve_user_post(id, request.data.pop("post"))
        post.vote.get(profile=request.user.profile).delete()
        return Response(status=HTTP_204_NO_CONTENT)
