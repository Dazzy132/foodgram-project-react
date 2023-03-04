from colorfield.fields import ColorField
from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']


class IngredientsInlineAdmin(admin.TabularInline):
    model = models.Recipe.ingredients.through
    extra = 1


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'name', 'text', 'cooking_time',
                    'get_image', 'get_tags', 'get_ingredients']
    fields = ('name', 'image', 'get_image', 'text', 'tags')
    readonly_fields = ['get_image']
    inlines = [
        IngredientsInlineAdmin
    ]

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} height=40px weight=40px>')

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


admin.site.index_title = 'Админка'
admin.site.site_title = 'Foodgram'
admin.site.site_header = 'Административная панель Foodgram'