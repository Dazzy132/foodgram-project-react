from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientsView, RecipesView,
                    TagViewSet, UserSubscribeViewSet)

router = DefaultRouter()
router.register(r'recipes', RecipesView, basename='recipes')
router.register(r'ingredients', IngredientsView)
router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:user_id>/subscribe/', UserSubscribeViewSet.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
]
