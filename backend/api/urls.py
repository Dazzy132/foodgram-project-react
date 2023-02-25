from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from users.views import UserViewSet, CustomUserViewSet, Logout
from . import views

router = DefaultRouter()
router.register(r'recipes', views.RecipesView)
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/token/login/', obtain_auth_token),
    path('auth/token/logout/', Logout.as_view()),
    path('', include(router.urls)),
]