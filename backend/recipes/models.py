from django.db import models


class Ingredient(models.Model):
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