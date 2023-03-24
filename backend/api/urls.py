from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from .views import MyUserViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'users', MyUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]