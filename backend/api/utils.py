import django_filters
from django_filters.widgets import BooleanWidget
from rest_framework.pagination import PageNumberPagination

from app.models import Ingredient, Recipe, Tag


class IngredientsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author_id')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        widget=BooleanWidget(),
        label='В корзине.'
    )
    is_favorited = django_filters.BooleanFilter(
        widget=BooleanWidget(),
        label='В избранных.'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'
