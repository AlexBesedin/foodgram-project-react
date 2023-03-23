import re

from djoser.serializers import UserCreateSerializer, UserSerializer
from users.models import MyUser
from rest_framework import serializers
from django.core.exceptions import ValidationError


class MyUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """
    
    class Meta:
        models = MyUser 
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


    def validate_username(self, value):
        if value.lower == 'me':
            raise ValidationError(
                'Использовать имя "me" в качестве "username" запрещено')
        if not re.match(r'^[\w.@+-]+$', value):
            raise ValidationError('Недопустимое имя пользователя')        
        return value        


class MyUserSerializer(UserSerializer):
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
