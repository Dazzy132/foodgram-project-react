from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from app.models import Ingredient, Recipe, RecipeIngredient, Tag, \
    FavoriteRecipe, UserProductList
from users.models import Follow, User

from .serializers import (CustomUserSerializer,
                          FavoriteRecipeSerializer, FollowSerializer,
                          FollowUserSerializer, IngredientsSerializer,
                          RecipeGETSerializer, RecipeIngredientSerializer,
                          RecipePOSTSerializer, TagSerializer,
                          UserProductListSerializer)
from .utils import CustomPageNumberPagination, IngredientsFilter, RecipeFilter


class RecipesView(viewsets.ModelViewSet):
    """Представление для рецептов"""
    model = Recipe
    serializer_class = RecipeGETSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Вернуть рецепты с аннотированными полями.
            # Exists - подзапросы в БД.
            # OuterRef - подзапрос в БД для того, чтобы сделать вычисления. В
            # качестве аргументов будет выступать поле КАЖДОГО рецепта
            return Recipe.objects.annotate(
                is_favorited=Exists(FavoriteRecipe.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(UserProductList.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef('pk'))
                )
            )
        else:
            # Value - созданное нами поле. Первое значение, второе тип поля
            return Recipe.objects.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )

    @action(
        detail=False, methods=['POST', 'DELETE'],
        url_path='(?P<recipe_id>\d+)/favorite',
        serializer_class=FavoriteRecipeSerializer
    )
    def favorite(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(serializer.data)
            return Response(serializer.errors)

        recipe = recipe.favorites.get(user=self.request.user)
        recipe.delete()
        return Response({'Message': "Рецепт успешно убран из избранных"})

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = ("attachment; "
                                           "filename=shopping_cart.pdf")

        p = canvas.Canvas(response)
        arial = ttfonts.TTFont("Arial", "data/arial.ttf")
        pdfmetrics.registerFont(arial)
        p.setFont("Arial", 14)

        ingredients = RecipeIngredient.objects.filter(
            recipe__products__user=request.user
        ).values_list(
            "ingredient__name", "amount", "ingredient__measurement_unit"
        )

        ingr_list = {}
        for name, amount, unit in ingredients:
            if name not in ingr_list:
                ingr_list[name] = {"amount": amount, "unit": unit}
            else:
                ingr_list[name]["amount"] += amount
        height = 700

        p.drawString(100, 750, "Список покупок")
        for i, (name, data) in enumerate(ingr_list.items(), start=1):
            p.drawString(
                80, height, f"{i}. {name} – {data['amount']} {data['unit']}"
            )
            height -= 25
        p.showPage()
        p.save()
        return response

    @action(
        detail=False, methods=['POST', 'DELETE'],
        url_path='(?P<recipe_id>\d+)/shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST':
            serializer = UserProductListSerializer(
                data=request.data, context={'request': self.request})
            if serializer.is_valid():
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(serializer.data)
            return Response(serializer.errors)

        recipe = recipe.products.get(user=self.request.user)
        recipe.delete()
        return Response({'Message': "Рецепт успешно убран из списка покупок"})

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipePOSTSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientsView(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    """Представление для пользователей Djoiser"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['GET'], url_path='subscriptions')
    def subscriptions(self, request):
        """Страница всех подписок пользователя"""
        current_user = self.request.user
        authors = Follow.objects.filter(follower=current_user)
        page = self.paginate_queryset(authors)
        data = FollowUserSerializer(page, many=True)
        return self.get_paginated_response(data.data)

    @action(
        detail=False, methods=['POST', 'DELETE'],
        url_path='(?P<user_id>\d+)/subscribe',
        serializer_class=FollowSerializer,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, user_id):
        """Подписка на пользователя по его ID"""
        author = get_object_or_404(User, pk=user_id)

        recipes_limit = self.request.query_params.get('recipes_limit', None)
        if recipes_limit:
            serializer = self.get_serializer(
                data={'following': author, 'follower': self.request.user},
                context={
                    'request': self.request,
                    'recipes_limit': recipes_limit
                }
            )
        else:
            serializer = self.get_serializer(
                data={'following': author, 'follower': self.request.user},
                context={'request': self.request}
            )

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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
