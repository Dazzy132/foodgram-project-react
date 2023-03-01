from colorfield.fields import ColorField
from django import forms
from django.contrib import admin

from . import models


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['author', 'name', 'text', 'cooking_time',
                    'image', 'get_tags', 'get_ingredients']

    def get_tags(self, obj):
        return "\n".join([tag.name for tag in obj.tags.all()])

    def get_ingredients(self, obj):
        return "\n".join([ingredient.name for ingredient in obj.ingredients.all()])


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    formfield_overrides = {
        ColorField: {'widget': forms.TextInput(attrs={'type': 'color'})}
    }
    list_display = ['name', 'color', 'slug']
    list_editable = ['color']
    prepopulated_fields = {'slug': ('name',)}


# @admin.register(models.RecipeIngredient)
# class RecipeIngredientAdmin(admin.ModelAdmin):
#     list_display = ['recipe', 'ingredient', 'amount']
#
#
# @admin.register(models.FavoriteRecipe)
# class RecipeIngredientAdmin(admin.ModelAdmin):
#     list_display = ['user', 'recipe']
#
#
# @admin.register(models.UserProductList)
# class RecipeIngredientAdmin(admin.ModelAdmin):
#     list_display = ['user', 'recipe']

admin.site.register(models.RecipeIngredient)
admin.site.register(models.FavoriteRecipe)
admin.site.register(models.UserProductList)