from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Ingredient, Recipe
from users.models import Follow, User

from .serializers import (CustomUserProfileSerializer, CustomUserSerializer,
                          FollowSerializer, FollowUserSerializer,
                          IngredientsSerializer, RecipeSerializer)


class RecipesView(viewsets.ModelViewSet):
    """Представление для рецептов"""
    model = Recipe
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientsView(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


class CustomUserViewSet(UserViewSet):
    """Представление для пользователей Djoiser"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    @action(
        detail=False, methods=['GET'], url_path='(?P<user_id>\d+)',
        serializer_class=CustomUserProfileSerializer
    )
    def profile(self, request, user_id):
        """Страница профиля пользователя"""
        user = get_object_or_404(User, pk=user_id)
        serializer = self.get_serializer(user)
        print(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='subscriptions')
    def subscriptions(self, request):
        """Страница всех подписок пользователя"""
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
        """Подписка на пользователя по его ID"""
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


class Logout(APIView):
    """Представление для token/logout"""
    permission_classes = [AllowAny]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
