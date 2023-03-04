from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets, filters
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, \
    IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow, User

from .serializers import (
    CustomUserProfileSerializer, CustomUserSerializer,FavoriteRecipeSerializer,
    FollowSerializer, FollowUserSerializer, IngredientsSerializer,
    RecipeGETSerializer, RecipeIngredientSerializer, RecipePOSTSerializer,
    TagSerializer, UserProductListSerializer, CustomObtainTokenSerializer
)

from .utils import IngredientsFilter


class RecipesView(viewsets.ModelViewSet):
    """Представление для рецептов"""
    model = Recipe
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeGETSerializer

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

        # Todo: Изменить тут логику, ибо при повторной отправке будет ошибка
        recipe = recipe.favorites.get(user=self.request.user)
        recipe.delete()
        return Response({'Message': "Рецепт успешно убран из избранных"})

    @action(
        detail=False, methods=['GET'], url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = get_object_or_404(User, username=self.request.user.username)
        all_products = user.products.select_related('recipe')

        # TODO: ПЕРЕДЕЛАТЬ
        response = {}
        for product in all_products:
            for ingredient in product.recipe.recipeingredient_set.all():
                if ingredient.ingredient.name in response:
                    response[ingredient.ingredient.name] += ingredient.amount
                else:
                    response[ingredient.ingredient.name] = ingredient.amount

        return Response(response)

    @action(
        detail=False, methods=['POST', 'DELETE'],
        url_path='(?P<recipe_id>\d+)/shopping_cart',
        serializer_class=UserProductListSerializer
    )
    def shopping_cart(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(serializer.data)
            return Response(serializer.errors)

        # Todo: Изменить тут логику, ибо при повторной отправке будет ошибка
        recipe = recipe.products.get(user=self.request.user)
        recipe.delete()
        return Response({'Message': "Рецепт успешно убран из списка покупок"})

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipePOSTSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# + Сделать фильтрацию по имени (частичное вхождение)
# + Здесь пагинация не нужна
class IngredientsView(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    pagination_class = [AllowAny]


# + Список пользователей, Регистрация пользователей, Текущий пользователь,
# + Изменение пароля
class CustomUserViewSet(UserViewSet):
    """Представление для пользователей Djoiser"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    # + Профиль пользователей (по id)
    @action(
        detail=False, methods=['GET'], url_path='(?P<user_id>\d+)',
        serializer_class=CustomUserSerializer,
        permission_classes=[AllowAny]
    )
    def profile(self, request, user_id):
        """Страница профиля пользователя"""
        user = get_object_or_404(User, pk=user_id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='subscriptions')
    def subscriptions(self, request):
        """Страница всех подписок пользователя"""
        current_user = self.request.user
        authors = Follow.objects.filter(follower=current_user)
        page = self.paginate_queryset(authors)
        data = FollowUserSerializer(page, many=True)
        return self.get_paginated_response(data.data)

    # + Доступно только авторизованным пользователям
    # TODO: Сделать фильтрацию по recipes_limit
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
                data={'following': author.pk},
                context={
                    'request': self.request,
                    'recipes_limit': recipes_limit
                }
            )
        else:
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


# + Список Тегов, Получение тега
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# + Удаление токена авторизации
class Logout(APIView):
    """Представление для token/logout"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_201_CREATED)


# + Получить токен авторизации
class CustomAuthToken(APIView):
    serializer_class = CustomObtainTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key}, status=status.HTTP_201_CREATED
        )


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
