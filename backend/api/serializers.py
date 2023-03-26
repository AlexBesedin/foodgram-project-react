import re

from djoser.serializers import UserCreateSerializer, UserSerializer
from users.models import MyUser, Follow
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .validators import follow_unique_validator


class MyUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """
    
    class Meta:
        model = MyUser 
        fields = (
            'email', 
            'username', 
            'first_name', 
            'last_name', 
            'password'
            )


    def validate_username(self, value):
        if value.lower == 'me':
            raise ValidationError(
                'Использовать имя "me" в качестве "username" запрещено')
        if not re.match(r'^[\w.@+-]+$', value):
            raise ValidationError('Недопустимое имя пользователя')        
        return value        

    def create(self, validated_data):
        user = MyUser.objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class MyUserSerializer(UserSerializer):
    """Сериализатор модели User"""
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = MyUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
            )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context['request'].user
        if request.is_authenticated and request.following.filter(id=obj).exist():
            return True
        return False


class FollowSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Follow
        fields = (
            'id',
            'user',
            'author'
            )
        validators = [follow_unique_validator]


    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValueError("Нельзя подписаться на самого себя")
        super().save(*args, **kwargs)