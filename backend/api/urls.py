from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomAuthToken, CustomUserViewSet, IngredientsView,
                    Logout, RecipesView, TagViewSet)

router = DefaultRouter()
router.register(r'recipes', RecipesView)
router.register(r'ingredients', IngredientsView)
router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('auth/token/login/', CustomAuthToken.as_view()),
    path('auth/token/logout/', Logout.as_view()),
    path('auth/', include('djoser.urls')),
    path('', include(router.urls)),
]
