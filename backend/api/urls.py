from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, IngredientsView, Logout, RecipesView

router = DefaultRouter()
router.register(r'recipes', RecipesView)
router.register(r'ingredients', IngredientsView)
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('auth/token/login/', obtain_auth_token),
    path('auth/token/logout/', Logout.as_view()),
    path('auth/', include('djoser.urls')),
    path('', include(router.urls)),
]
