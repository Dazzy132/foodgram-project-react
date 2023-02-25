from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from djoser.views import UserViewSet
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import CustomUserSerializer, CustomUserRegisterSerializer


class CustomUserRegisterViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserRegisterSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class Logout(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)