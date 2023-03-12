from http import HTTPStatus

from app.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.permissions import CurrentUserOrAdminOrReadOnly
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User

from .permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly, ReadOnly
from .serializers import (
    CustomUserSerializer,
    FavoriteRecipeSerializer,
    FollowCheckSubscribeSerializer,
    FollowSerializer,
    IngredientsSerializer,
    RecipeGETSerializer,
    RecipeIngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from .utils import (
    CustomPageNumberPagination,
    IngredientsFilter,
    RecipeFilter,
    get_pdf_shopping_cart,
)


class RecipesView(viewsets.ModelViewSet):
    """Представление для рецептов"""
    model = Recipe
    serializer_class = RecipeGETSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGETSerializer
        return RecipeSerializer

    def get_queryset(self):
        annotate_kwargs = {}
        if self.request.user.is_authenticated:
            annotate_kwargs = {
                'is_favorited': Exists(FavoriteRecipe.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef('pk'))
                ),
                'is_in_shopping_cart': Exists(ShoppingCart.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef('pk'))
                )
            }
        return (
            Recipe.objects
            .select_related('author')
            .prefetch_related('tags', 'ingredients')
            .annotate(**annotate_kwargs)
        )

    @transaction.atomic()
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['POST'],
        url_path=r'(?P<recipe_id>\d+)/favorite'
    )
    def favorite(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = FavoriteRecipeSerializer(
            data={"recipe": recipe.pk}, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, recipe=recipe)
        return Response(
            {"Message": "Рецепт успешно добавлен в избранное"},
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite_recipe = recipe.favorites.filter(user=self.request.user)
        if favorite_recipe.exists():
            favorite_recipe.delete()
            return Response(
                {'Message': "Рецепт успешно удален из избранного"},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"errors": "Этот рецепт не добавлен в избранное"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Предоставить список покупок пользователю в PDF формате"""
        return get_pdf_shopping_cart(request)

    @action(
        detail=False, methods=['POST'],
        url_path=r'(?P<recipe_id>\d+)/shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        serializer = ShoppingCartSerializer(
            data={'user': self.request.user.pk, 'recipe': recipe.pk},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, recipe=recipe)
        return Response(
            {'Message': 'Рецепт успешно добавлен в список покупок'},
            status=HTTPStatus.CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        del_recipe = recipe.cart.filter(user=self.request.user)
        if del_recipe.exists():
            del_recipe.delete()
            return Response(
                {'Message': "Рецепт успешно удален из списка покупок"},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Этого рецепта нет в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )


class IngredientsView(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    """Представление для пользователей Djoiser"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [CurrentUserOrAdminOrReadOnly | ReadOnly]

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, methods=['GET'], url_path='subscriptions')
    def subscriptions(self, request):
        """Страница всех подписок пользователя"""
        current_user = self.request.user
        authors = Follow.objects.filter(follower=current_user)
        page = self.paginate_queryset(authors)
        data = FollowSerializer(
            page, many=True, context={'request': self.request}
        )
        return self.get_paginated_response(data.data)


class UserSubscribeViewSet(APIView):
    """Подписки/Отписки на авторов рецептов"""
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """Подписка на пользователя по его ID"""
        author = get_object_or_404(User, pk=user_id)
        user = request.user

        serializer = FollowCheckSubscribeSerializer(
            data={"following": author.pk, "follower": user.pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        follow = Follow.objects.create(follower=user, following=author)
        serializer = FollowSerializer(follow, context={'request': request})
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, user_id):
        """Отписаться от пользователя по его ID"""
        author = get_object_or_404(User, pk=user_id)
        user = request.user

        serializer = FollowCheckSubscribeSerializer(
            data={"following": author.pk, "follower": user.pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        Follow.objects.filter(follower=user, following=author).delete()
        return Response({'Message:': 'Вы отписались'})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
