import re

from djoser.serializers import UserCreateSerializer, UserSerializer
from users.models import MyUser, Follow
from recipes.models import Recipe, Tag, Ingredient, ShopingList
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .validators import follow_unique_validator, color_validator, shopping_cart_validator
from drf_extra_fields.fields import Base64ImageField



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
        if request.is_authenticated and request.following.filter(id=obj.id).exists():
            return True
        return False



class FollowShowRecipeSerializer(serializers.ModelSerializer):
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
        read_only_fields = fields   


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


    def validate(self, data):
        """Проверяем, что пользователь не подписывается на самого себя."""
        request_user = self.context['request'].user
        author = data.get('author')
        if request_user == author:
            raise serializers.ValidationError("Нельзя подписаться на самого себя")
        return data



class UserFollowSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых только что подписался пользователь.  
    В выдачу добавляются рецепты."""
    recipes = FollowShowRecipeSerializer(many=True, read_only=True)
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
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов """
    
    color = serializers.CharField(
        validators=[color_validator]
        )

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""

    class Meta:
        model = Ingredient  
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


# class RecipeSerializer(serializers.ModelSerializer):
#     pass 


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""

    class Meta:
        models = Favorite
        fields = (
            'user',
            'recipe'
            )
        validators = [favorite_validator]


class ShopingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShopingList
        fields = (
            'user',
            'recipe'
            )
        validators = [shopping_cart_validator]    