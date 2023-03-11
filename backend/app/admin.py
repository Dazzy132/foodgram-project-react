from colorfield.fields import ColorField
from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    search_fields = ['name']


class IngredientsInlineAdmin(admin.TabularInline):
    model = models.Recipe.ingredients.through
    extra = 1


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'name', 'cooking_time',
                    'get_image', 'get_tags', 'get_ingredients',
                    'get_favorites_count']
    fields = ('author', 'name', 'image', 'get_image', 'text', 'cooking_time',
              'tags')
    readonly_fields = ['get_image']
    list_filter = ['author', 'tags']
    search_fields = ['author__username', 'name']
    inlines = [
        IngredientsInlineAdmin
    ]

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} height=40px weight=40px>')

    def get_tags(self, obj):
        return "\n, ".join([tag.name for tag in obj.tags.all()])

    def get_favorites_count(self, obj):
        return models.FavoriteRecipe.objects.filter(recipe=obj).count()

    def get_ingredients(self, obj):
        return "\n, ".join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    get_image.short_description = 'Фотография рецепта'
    get_tags.short_description = 'Теги рецепта'
    get_favorites_count.short_description = 'Количество добавлений в избранное'
    get_ingredients.short_description = 'Ингредиенты'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    formfield_overrides = {
        ColorField: {'widget': forms.TextInput(attrs={'type': 'color'})}
    }
    list_display = ['name', 'color', 'slug']
    list_editable = ['color']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(models.RecipeIngredient)
admin.site.register(models.FavoriteRecipe)
admin.site.register(models.ShoppingCart)

admin.site.index_title = 'Админка'
admin.site.site_title = 'Foodgram'
admin.site.site_header = 'Административная панель Foodgram'
