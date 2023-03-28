from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from .views import MyUserViewSet, TagViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'users', MyUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'users/<int:id>/subscribe/', MyUserViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'}), name='subscribe'),
]
