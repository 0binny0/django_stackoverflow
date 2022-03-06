
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import RegisterSerializer


class RegisterEndpoint(APIView):

    def get(self, request):
        serializer = RegisterSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            return Response(data=serializer.validated_data)
