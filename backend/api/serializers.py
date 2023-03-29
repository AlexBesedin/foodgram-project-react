import re

from djoser.serializers import UserCreateSerializer, UserSerializer
from users.models import MyUser, Follow
from recipes.models import Recipe, Tag, Ingredient, ShopingList, Recipe, RecipeIngredient, Favorite
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .validators import (follow_unique_validator, color_validator, 
                        shopping_cart_validator, recipe_ingredient_validators, favorite_validator)
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
        extra_kwargs = {'password': {'write_only': True}}

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
    recipes = serializers.SerializerMethodField()
    # recipes = FollowShowRecipeSerializer(many=True, read_only=True)
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
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = RecipeSerializer(recipes, many=True, context=self.context)
        return serializer.data    


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели RecipeIngredient"""
    id = serializers.ReadOnlyField(source='ingredient__id')
    name = serializers.ReadOnlyField(source='ingredient__name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient__measurement_unit'
        ) 

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 
            'name', 
            'measurement_unit', 
            'amount'
            )
        validators = [recipe_ingredient_validators] 


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов для GET-рецептов."""
    tags = TagSerializer(many=True)
    author = MyUserSerializer(read_only=True)
    ingredients  = RecipeIngredientSerializer(
        source='amount',
        many=True,
        read_only=True,)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)  
    image = Base64ImageField()  

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            'pub_date'
            )
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user,
                                       recipe_id=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShopingList.objects.filter(
            user=request.user, recipe_id=obj).exists()        


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'pub_date'
            )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""

    class Meta:
        models = Favorite
        fields = (
            'user',
            'recipe'
            )
        validators = [favorite_validator]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowShowRecipeSerializer(
            instance.recipe, context=context).data    


class ShopingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShopingList
        fields = (
            'user',
            'recipe'
            )
        validators = [shopping_cart_validator]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowShowRecipeSerializer(
            instance.recipe, context=context).data    