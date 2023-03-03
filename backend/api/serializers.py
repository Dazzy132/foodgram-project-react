import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers

from app.models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                        Tag, UserProductList)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """Декодирование картинки"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователей Djoiser"""
    is_subscribed = serializers.SerializerMethodField(default=True)

    def get_is_subscribed(self, obj):
        author = get_object_or_404(User, username=obj.username)
        user = self.context.get('request').user

        if author.pk == user.pk:
            return False

        return Follow.objects.filter(follower=user, following=author).exists()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientGETSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient.pk'
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=False)
    ingredients = RecipeIngredientGETSerializer(
        many=True, read_only=True, source='recipe_ingredient'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        return FavoriteRecipe.objects.filter(
            recipe=obj, user=self.context.get('request').user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return UserProductList.objects.filter(
            recipe=obj, user=self.context.get('request').user
        ).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text',
                  'cooking_time', 'image', 'tags', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart')
        read_only_fields = ('author',)


class RecipePOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов (укороченный)"""
    author = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        write_only=True, queryset=User.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=False)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredient'
    )

    def update(self, instance, validated_data):
        print(validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.set(validated_data.get('tags', instance.tags))

        ingredients_data = validated_data.get(
            'recipe_ingredient', instance.ingredients
        )

        instance.ingredients.clear()
        for ing_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ing_data.get('id'),
                amount=ing_data.get('amount')
            )

        instance.save()
        return instance

    # def update(self, instance, validated_data):
    #     ingredients_data = validated_data.pop('recipe_ingredient')
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.image = validated_data.get('image', instance.image)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.cooking_time = validated_data.get(
    #         'cooking_time', instance.cooking_time
    #     )
    #     instance.tags.set(validated_data.get('tags', instance.tags))
    #
    #     instance.ingredients.all().delete()
    #     for ingredient_data in ingredients_data:
    #         ingredient_id = ingredient_data.get('id')
    #         if ingredient_id:
    #             ingredient = Ingredient.objects.get(pk=ingredient_id)
    #             ingredient.amount = ingredient_data.get('amount')
    #             ingredient.save()
    #         else:
    #             Ingredient.objects.create(recipe=instance, **ingredient_data)
    #     instance.save()
    #     return instance

    def create(self, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('recipe_ingredient')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient in ingredients_data:
            ing = get_object_or_404(Ingredient, name=ingredient.get('id'))
            amount = ingredient.get('amount')

            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ing, amount=amount
            )

        return recipe

    def to_representation(self, instance):
        return RecipeGETSerializer(
            instance, context={'request': self.context.get('request')}
        ).data

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'name', 'image', 'tags',
                  'text', 'cooking_time')
        # validators = [
        #     serializers.UniqueTogetherValidator(
        #         queryset=Recipe.objects.all(),
        #         fields=['author', 'name'],
        #         message='У вас уже создан такой рецепт.'
        #     )
        # ]


# TODO: ПЕРЕДЕЛАТЬ НА UserRegisterSerializer
class CustomUserRegisterSerializer(UserSerializer):
    """Сериализатор для регистрации пользователей Djoiser"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name',
                  'last_name')


# TODO: Возможно тут тоже передалть
class CustomUserProfileSerializer(UserSerializer):
    """Сериализатор для просмотра профиля пользователей Djoiser"""
    is_subscribed = serializers.SerializerMethodField(default=True)

    def get_is_subscribed(self, obj):
        author = get_object_or_404(User, username=obj.username)
        user = self.context.get('request').user
        if author.pk == user.pk:
            return False
        return Follow.objects.filter(follower=user, following=author).exists()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок"""
    follower = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    following = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    def validate_following(self, following):
        """Проверка на то, чтобы пользователи не могли подписываться на себя"""
        if following.pk == self.context.get('request').user.pk:
            raise serializers.ValidationError(
                'Вы не можете подписаться сам на себя'
            )
        return following

    def to_representation(self, instance):
        """Изменение ответа сериализатора"""
        user = instance.following
        user_recipes = user.recipes.all()
        recipes_count = user_recipes.count()

        user_serializer = CustomUserSerializer(user)
        recipes_serializer = RecipeGETSerializer(user_recipes, many=True)

        response = {}
        response.update(user_serializer.data)
        response['is_subscribed'] = True
        response['recipes'] = recipes_serializer.data
        response['recipes_count'] = recipes_count
        return response

    class Meta:
        fields = ('follower', 'following')
        model = Follow
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['follower', 'following'],
                message='Вы уже подписаны на этого автора.'
            )
        ]


class FollowUserSerializer(serializers.Serializer):
    """Сериализатор для POST запроса, который выведет информацию об авторе и
    его рецептов"""
    following = serializers.SlugRelatedField(
        queryset=Follow.objects.all(), slug_field='username'
    )
    recipes = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        recipes_filter = Recipe.objects.filter(author__follower=obj)
        return RecipeGETSerializer(recipes_filter, many=True).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        read_only=True
    )
    recipe = RecipeGETSerializer(read_only=True)

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe',)


class UserProductListSerializer(FavoriteRecipeSerializer):
    class Meta:
        model = UserProductList
        fields = ('user', 'recipe',)
