from django.shortcuts import render, get_object_or_404
from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, Follow
from .utils import ListView, CreateView

from app.models import Recipe, Ingredient

from .serializers import RecipeSerializer, IngredientsSerializer, \
    CustomUserSerializer, FollowUserSerializer, FollowSerializer


class RecipesView(viewsets.ModelViewSet):
    model = Recipe
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientsView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['GET'], url_path='subscriptions')
    def subscriptions(self, request):
        current_user = self.request.user
        authors = Follow.objects.filter(follower=current_user)
        page = self.paginate_queryset(authors)
        data = FollowUserSerializer(page, many=True)
        return self.get_paginated_response(data.data)
        # authors_recipes = Recipe.objects.filter(
        #     author__following__follower__username=current_user.username
        # )

    @action(
        detail=False, methods=['POST', 'DELETE'],
        url_path='(?P<user_id>\d+)/subscribe',
        serializer_class=FollowSerializer
    )
    def subscribe(self, request, user_id):
        author = get_object_or_404(User, pk=user_id)
        serializer = self.get_serializer(data={'following': author.pk})

        if request.method == 'POST':
            if serializer.is_valid():
                serializer.save(follower=self.request.user, following=author)
                return Response(serializer.data)
            return Response(serializer.errors)

        follow = Follow.objects.filter(
            follower=self.request.user, following=author
        )

        if follow.exists():
            follow.delete()
            return Response({'Сообщение:': 'Вы отписались'})
        return Response({"Ошибка": "Пользователь не найден"})


# class FollowingsUserViewSet(ListView):
#     serializer_class = FollowUserSerializer
#
#     def get_queryset(self):
#         return Follow.objects.filter(follower=self.request.user)
#
#
# class FollowingUserViewSet(CreateView):
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer
#
#     def perform_create(self, serializer):
#         following = get_object_or_404(User, pk=self.kwargs.get("user_id"))
#         serializer.save(follower=self.request.user,
#                         following=following)


class Logout(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
