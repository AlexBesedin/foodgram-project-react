from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from .views import MyUserViewSet, TagViewSet, IngredientViewSet,RecipeViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'users', MyUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'users/<int:id>/subscribe/', MyUserViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'}), name='subscribe'),
    path(r'recipes/<int:id>/favorite/' , RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'}), name='favorite')
]