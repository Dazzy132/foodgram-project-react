import django_filters
from rest_framework import mixins, viewsets
from app.models import Ingredient


# class TitleFilter(django_filters.FilterSet):
#     genre = django_filters.CharFilter(field_name='genre__slug')
#     category = django_filters.CharFilter(field_name='category__slug')
#
#     name = django_filters.CharFilter(field_name='name', lookup_expr='contains')
#     year = django_filters.NumberFilter(field_name='year')
#
#     class Meta:
#         model = Title
#         fields = ('genre', 'category', 'name', 'year')


class IngredientsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ('name',)