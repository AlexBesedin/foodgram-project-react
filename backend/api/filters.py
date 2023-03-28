import django_filters
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')
    
    class Meta:
        model = Ingredient
        fields = ('name',)