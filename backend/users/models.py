from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core import validators


class User(AbstractUser):
    """ Кастомная модель пользователя. """
    username = models.CharField(
        max_length=150,
        verbose_name = 'Логин', 
        unique=True,
        validators=[validators.RegexValidator(regex='^[\w.@+-]+\z')]
        )
    password = models.CharField(
        max_length=150,
        verbose_name = 'Пароль'
        )
    email = models.EmailField(
        max_length=254, 
        verbose_name = 'Email',
        unique=True
        )
    first_name = models.CharField(
        max_length=150,
        verbose_name = 'Имя'
        )
    last_name = models.CharField(
        max_length=150,
        verbose_name = 'Фамилия'
        )   
    is_subscribed = models.BooleanField(
        verbose_name = 'Подписан',
        default=True
        )


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )


    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    """Подписки на авторов"""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь: {self.user}, Автор: {self.author}'

    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValueError("Нельзя подписаться на самого себя")
        super().save(*args, **kwargs)