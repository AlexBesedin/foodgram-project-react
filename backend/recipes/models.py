from django.db import models


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        max_length = 200,
        verbose_name = "Название ингредиента",
        )
    measurement_unit = models.CharField(
        max_length = 200,
        verbose_name = "Единицы измерения",
    )    

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint (
                fields = ('name', 'measurement_unit'), name='ingredient_name_unit_unique')
        )


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        max_length = 200,
        verbose_name = "Название",
        unique=True,    
    )
    color = models.CharField(
        max_length = 7,
        verbose_name = "Цвет в HEX",
        unique=True,
    )
    slug = models.SlugField(
        max_length = 200,
        verbose_name = "Уникальный слаг",
        unique = True,
    )


    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'        