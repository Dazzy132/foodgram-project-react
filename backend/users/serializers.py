# from djoser.serializers import UserSerializer
# from rest_framework import serializers
# from api.serializers import RecipeSerializer
#
# from .models import Follow, User
#
#
# class CustomUserSerializer(UserSerializer):
#     class Meta:
#         model = User
#         fields = ('email', 'username', 'first_name', 'last_name')
#
#
# class FollowSerializer(serializers.ModelSerializer):
#     follower = serializers.SlugRelatedField(
#         slug_field='username',
#         default=serializers.CurrentUserDefault(),
#         read_only=True
#     )
#     following = serializers.PrimaryKeyRelatedField(read_only=True)
#
#     class Meta:
#         fields = ('follower', 'following')
#         model = Follow
#
#
# class FollowUserSerializer(serializers.Serializer):
#     following = serializers.SlugRelatedField(
#         queryset=Follow.objects.all(), slug_field='username'
#     )
#
#     class Meta:
#         # model = Follow
#         fields = ('following',)