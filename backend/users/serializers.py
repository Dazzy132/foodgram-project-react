from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer
from .models import User


class CustomUserRegisterSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')
