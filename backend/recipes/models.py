from django.db import models
from users.models import User


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
                fields = ('name', 'measurement_unit'), 
                name='ingredient_name_unit_unique'
                )
        )
    
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
            validators.RegexValidator(
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
        User,
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
        validators=[validators.MinValueValidator(
            1, message='Мин. время приготовления 1 минута'), ])
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
    amount =  models.PositiveIntegerField(
        verbose_name='Количество',
        validators = [validators.MinLengthValidator(
            1, message='Минимальное количество ингредиентов 1')]
        )