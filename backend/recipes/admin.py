from django.contrib import admin

from .models import Tag

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
