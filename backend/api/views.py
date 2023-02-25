from django.shortcuts import render
from rest_framework import viewsets
from app import models
from . import serializers


class RecipesView(viewsets.ModelViewSet):
    model = models.Recipe
    queryset = models.Recipe.objects.select_related('author')
    serializer_class = serializers.RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
