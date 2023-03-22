from django.db import models
from django.db.models import DateTimeField
from users.models import MyUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MinLengthValidator


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
        constraints = [
            models.UniqueConstraint (
                fields = ('name', 'measurement_unit'), 
                name='ingredient_name_unit_unique'
                )
        ]
    
    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'

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
        validators = [
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Ваше значение не является цветом'
            )
        ]
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

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        MyUser,
        on_delete = models.CASCADE,
        related_name = 'recipe',
        verbose_name = 'Автор'
        )
    name = models.CharField(
        max_length=200,
        verbose_name = "Название"
        )
    text = models.TextField(
        verbose_name = "Описание"
        )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name = "Картинка рецепта",
        blank=True,
        null=True,
        )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(
            1, message='Мин. время приготовления 1 минута'), 
            ]
            )
    pub_date = models.DateTimeField(
        verbose_name='Время публикации',
        auto_now_add=True,
        )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
        )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes'
        )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    """ Модель связи ингредиента и рецепта. """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Рецепт'
        )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='amount',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinLengthValidator(1, 
        message='Минимальное количество ингредиентов 1')]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]


class Favorite(models.Model):
    """Модель списка избранного"""
    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Автор списка избранного'
        )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт из списка избранного'
        )
    date_added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True
    )        

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

class ShopingList(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Юзер списка покупок'
        )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Список покупок'
        )
    date_add = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True
    )    

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_list_recipe'
            )
        ]  