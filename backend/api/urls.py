from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .views import IngredientsView, RecipesView, CustomUserViewSet, Logout
# FollowingsUserViewSet, FollowingUserViewSet

router = DefaultRouter()
router.register(r'recipes', RecipesView)
router.register(r'ingredients', IngredientsView)
# router.register(r'users/(?P<user_id>\d+)/subscribe', FollowingUserViewSet,
#                 basename='follows')
# router.register(r'users/subscriptions', FollowingsUserViewSet,
#                 basename='follows')
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('auth/token/login/', obtain_auth_token),
    path('auth/token/logout/', Logout.as_view()),
    path('auth/', include('djoser.urls')),
    # path('users/<int:user_id>/subscribe/', FollowingUserViewSet),
    path('', include(router.urls)),
]
