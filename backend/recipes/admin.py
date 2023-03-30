from django.contrib import admin


from .models import Recipe, Ingredient, Tag, RecipeIngredient, Favorite, ShopingList

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    empty_value_display = '<--пусто-->'
    list_filter = ('name', 'slug',)
    search_fields = ('name', 'slug',)


class IngredientsInRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through


class IngredientAdmin(admin.ModelAdmin):
    inlines = [
        IngredientsInRecipeInline,
    ]
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-empty-'


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        IngredientsInRecipeInline,
    ]
    exclude = ('ingredients',)
    list_display = ('id', 'author', 'name', 'count_favorites')
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-empty-'

    def count_favorites(self, obj):
        return obj.favorite.count()


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShopingList)        