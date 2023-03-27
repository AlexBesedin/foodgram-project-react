from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from djoser.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import MyUserSerializer, MyUserCreateSerializer, UserFollowSerializer, FollowSerializer
from users.models import MyUser, Follow


User = get_user_model()

class MyUserViewSet(UserViewSet):
    """Viewset для объектов модели User"""
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    

    @action(
        methods=['GET', ],
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        serializer = MyUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            if self.request.method == 'POST':
                return MyUserCreateSerializer
            return UserSerializer
        return super().get_serializer_class()

    @action(
        methods=['GET', 'HEAD'],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[IsAuthenticated, ]
        )     

    def subscriptions(self, request):
        """Выдает авторов, на кого подписан пользователь"""
        user = request.user
        queryset = user.following.all().values_list('author', flat=True)
        authors = MyUser.objects.filter(pk__in=queryset)
        serializer = UserFollowSerializer(authors, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=[IsAuthenticated, ])


    def subscribe(self, request, id):
        """Подписаться/отписаться на/от автора"""
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={
                    'user': user.id,
                    'author': author.id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            Subscription,
            user=user,
            author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   