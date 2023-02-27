# from djoser.views import UserViewSet
# from rest_framework import status
# from rest_framework.decorators import action
# from rest_framework.permissions import (AllowAny, IsAuthenticated,
#                                         IsAuthenticatedOrReadOnly)
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
#
# from .models import Follow, User
# from .serializers import CustomUserSerializer, FollowSerializer, FollowUserSerializer
# from .utils import CreateView, ListCreateDestroyViewSet, ListView
#
#
# class CustomUserViewSet(UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = CustomUserSerializer
#
#     @action(
#         detail=False,
#         methods=['GET'],
#         url_path='subscriptions'
#        )
#     def subscriptions(self, request):
#         authors = Follow.objects.filter(follower=self.request.user)
#         print(authors)
#         serializer = FollowUserSerializer(authors, many=True)
#         return Response(serializer.data)
#
#
# class Logout(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         request.user.auth_token.delete()
#         return Response(status=status.HTTP_200_OK)