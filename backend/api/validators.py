from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow

follow_unique_validator = UniqueTogetherValidator(
    queryset=Follow.objects.all(),
    fields=('user', 'author'),
    message='Вы уже подписаны на этого автора'
)
