from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, IngredientsView, RecipesView, TagViewSet

router = DefaultRouter()
router.register(r'recipes', RecipesView, basename='recipes')
router.register(r'ingredients', IngredientsView)
router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
