import re

from djoser.serializers import UserCreateSerializer, UserSerializer
from users.models import MyUser, Follow
from recipe.models import Recipe
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
    is_subscribed = serializers.SerializerMethodField()

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


class SecondRecipeSerializer(ModelSerializer):
    """Сериализатор для отображени модели Recipe для эндпоинта api/users/{id}/subscribe/"""
     image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
            )
        read_only_fields = '__all__'    


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор модели подписки на авторов"""

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


class UserFollowSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых только что подписался пользователь.  
    В выдачу добавляются рецепты."""
    recipe = SecondRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
            )

    def get_count_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()        