import django_filters

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

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'
