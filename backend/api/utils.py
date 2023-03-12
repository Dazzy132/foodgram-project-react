import django_filters
from app.models import Ingredient, Recipe, RecipeIngredient, Tag
from django.http import HttpResponse
from django_filters.widgets import BooleanWidget
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework.pagination import PageNumberPagination


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


def get_pdf_shopping_cart(request):
    """Генерация списка покупок в виде PDF формата"""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = ("attachment; "
                                       "filename=shopping_cart.pdf")

    p = canvas.Canvas(response)
    arial = ttfonts.TTFont("Arial", "data/arial.ttf")
    pdfmetrics.registerFont(arial)
    p.setFont("Arial", 14)

    ingredients = RecipeIngredient.objects.filter(
        recipe__cart__user=request.user
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
