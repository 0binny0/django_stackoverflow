
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from django.db.models import F

from rest_framework.views import APIView
from rest_framework.status import (
    HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_200_OK
)
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .models import Question, Answer, Vote
from .serializers import VoteSerializer, CurrentPostStateSerializer

def retrieve_user_post(id, model):
    models = {
        'question': Question,
        'answer': Answer
    }
    model_content_type = ContentType.objects.get_for_model(
        models[model]
    )
    post = model_content_type.get_object_for_this_type(id=id)
    return post

class UserVoteEndpoint(APIView):

    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    throttle_classes = []

    def get(self, request, id):
        question = Question.objects.get(id=id)
        serializer = CurrentPostStateSerializer(
            question, context={'request': request}
        )
        return Response(data=serializer.data)

    def post(self, request, id):
        if isinstance(request.user, AnonymousUser):
            return Response(status=HTTP_400_BAD_REQUEST)
        post = retrieve_user_post(id, request.data['post'])
        serializer = VoteSerializer(data={'profile': request.user.profile.id},
            context={'post': post, 'vote_type': request.data['type']} , partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(type=request.data["type"], content_object=post)
            return Response(status=HTTP_201_CREATED)

    def put(self, request, id):
        post = retrieve_user_post(id, request.data.pop("post"))
        vote = post.vote.get(profile=request.user.profile)
        serializer = VoteSerializer(
            instance=vote, data=request.data,
            context={"post": post, "type": request.data['type']}, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            updated_vote = serializer.save()
            return Response(status=HTTP_204_NO_CONTENT)

    def delete(self, request, id):
        post = retrieve_user_post(id, request.data.pop("post"))
        vote = post.vote.get(profile=request.user.profile)
        if vote.type == "dislike":
            post.score = F("score") + 1
        else:
            post.score = F("score") - 1
        post.save()
        post.refresh_from_db()
        vote.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class PageStatusEndpoint(APIView):

    def get(self, request, id):
        question = Question.objects.get(id=id)
        return Response({
            'posted': question.profile.user == request.user, 'visible': question.visible
        }, status=HTTP_200_OK)

    def put(self, request, id):
        post = retrieve_user_post(id, request.query_params['post'])
        if isinstance(post, Question):
            if not post.visible:
                Question.objects.filter(id=id).update(visible=True)
            else:
                Question.objects.filter(id=id).update(visible=False)
        else:
            post.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def delete(self, request, id):
        post = retrieve_user_post(id, request.query_params['post'])
        post.delete()
        return Response(status=HTTP_204_NO_CONTENT)
