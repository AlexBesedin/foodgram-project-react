from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from djoser.views import UserViewSet
from djoser.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from collections import defaultdict

from .filters import IngredientFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    MyUserSerializer, MyUserCreateSerializer, 
    UserFollowSerializer, FollowSerializer, TagSerializer, 
    IngredientSerializer, RecipeSerializer, GetRecipeSerializer)
from users.models import MyUser, Follow
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShopingList


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
        methods=['GET', ],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[IsAuthenticated, ]
        )     

    def subscriptions(self, request):
        """Выдает авторов, на кого подписан пользователь"""
        user = request.user
        following_authors = MyUser.objects.filter(following__user=user)
        serializer = UserFollowSerializer(following_authors, many=True)
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
            Follow,
            user=user,
            author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   


class TagViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Tag"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    search_fields = ('^name', )
    pagination_class = None



class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Recipe"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    # filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Определяет какой сериализатор использовать"""
        if self.request.method in SAFE_METHODS and self.request.method == 'GET':
            return GetRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)


    @action(
        methods=['POST',],
        detail=False,
        url_path='recipes',
        url_name='recipes',
        permission_classes=[IsAuthenticated, ])

    def recipes(self, request):
        serializer = RecipeSerializer(data=request.data, context={'author': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['DELETE',],
        detail=False,
        url_path='recipes',
        url_name='recipes',
        permission_classes=[IsAuthenticated, ])

    def recipe_delete(self, request):
        recipe_id = request.query_params.get('id')
        if not recipe_id:
            return Response({'detail': 'Укажите идентификатор рецепта'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не найден'}, status=status.HTTP_404_NOT_FOUND)
        if recipe.author != request.user:
            return Response({'detail': 'Вы не автор этого рецепта'}, status=status.HTTP_403_FORBIDDEN)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        url_path='favorite',
        url_name='favorite',
        permission_classes=[IsAuthenticated, ])    


    def favorite(self, request, id):
        """Добавить/Удалить рецепт в/из избранное"""
        try:
            recipe = Recipe.objects.get(id=id)
            favorite = Favorite.objects.get(user=request.user, recipe=recipe)
            if request.method == 'DELETE':
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except (Recipe.DoesNotExist, Favorite.DoesNotExist):
            if request.method == 'POST':
                Favorite.objects.create(user=request.user, recipe=recipe)
                serializer = FollowSerializer(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=[IsAuthenticated, ])


    def download_shopping_cart(self, request):
        """Скачать список покупок"""
        # Получаем список всех рецептов, сохраненных в списке покупок текущего пользователя
        shop_list = ShopingList.objects.filter(user=request.user)
        recipes = [item.recipe for item in shop_list]

        # Создаем словарь, где ключами будут имена ингредиентов вместе с их единицами измерения, а значениями будут суммарные количество ингредиентов, необходимых для приготовления всех рецептов
        ingredients_list = defaultdict(float)
        for recipe in recipes:
            for recipe_ingredient in recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient
                key = f"{ingredient.name} - {ingredient.measurement_unit}"
                ingredients_list[key] += recipe_ingredient.amount

        # Формируем текстовое представление полученного словаря
        shopping_cart = ""
        for key, value in ingredients_list.items():
            shopping_cart += f"{key} - {value}\n"

    # Создаем PDF-файл, если нужно
        if request.GET.get('pdf'):
            pdf_file = io.BytesIO()
            p = canvas.Canvas(pdf_file)
            p.drawString(100, 750, "Shopping List")
            p.drawString(100, 700, shopping_cart)
            p.save()

            # Отправляем PDF-файл пользователю
            response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
            return response

        # Отправляем текстовый файл пользователю
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=[IsAuthenticated, ])    

    def shopping_cart(self, request, id ):
        """Добавить / удалить рецепт в список покупок"""
        try:
            recipe = Recipe.objects.get(id=id)
            shop_cart = ShopingList.objects.get(user=request.user, recipe=recipe)
            if request.method == 'DELETE':
                shop_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except (Recipe.DoesNotExist, ShopingList.DoesNotExist):
            if request.method == 'POST':
                shop_cart = ShopingList.objects.create(user=request.user, recipe=recipe)
                serializer = FollowSerializer(shop_cart.recipe)
                return Response({'message': 'Рецепт успешно добавлен в список покупок!', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'message': 'Ошибка! Рецепт не найден в списке покупок', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

