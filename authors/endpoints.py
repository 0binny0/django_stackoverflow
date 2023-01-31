

from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .serializers import RegisterSerializer, LoginSerializer, UserListingSerializer


class AccountsEndpoint(APIView):

    def get(self, request):
        query_string = request.query_params.copy()
        if 'search' in query_string:
            if query_string['search']:
                users = get_user_model().posted.by_name(query_string['search'])
                if not users:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                users = get_user_model().posted.by_name("")
            serializer = UserListingSerializer(users, many=True)
            return Response(data={"users": serializer.data})
        action = query_string.pop("action")[0]
        if action == "login":
            serializer = LoginSerializer
        else:
            serializer = RegisterSerializer
        serialized_object = serializer(data=query_string, partial=True)
        if serialized_object.is_valid(raise_exception=True):
            return Response(data=serialized_object.validated_data)



class UserListingEndpoint(APIView):

    def get(self, request):
        username_query = request.query_params['search']
        users_containing_name = get_user_model().posted.by_name(username=username_query)
        if not users_containing_name:
            return Response(status=204)
        users = UserListingSerializer(users=users_containing_name, many=True)
        return Response(data=users, status=200)
