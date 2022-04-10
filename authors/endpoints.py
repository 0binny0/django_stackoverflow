
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import RegisterSerializer, LoginSerializer


class AccountsEndpoint(APIView):

    def get(self, request):
        query_string = request.query_params.copy()
        action = query_string.pop("action")[0]
        if action == "login":
            serializer = LoginSerializer
        else:
            serializer = RegisterSerializer
        serialized_object = serializer(data=query_string, partial=True)
        if serialized_object.is_valid(raise_exception=True):
            return Response(data=serialized_object.validated_data)
