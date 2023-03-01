from rest_framework import mixins, viewsets


class ListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class CreateView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass