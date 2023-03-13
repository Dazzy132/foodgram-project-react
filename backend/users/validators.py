import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """Кастомный валидатор для поля username"""

    if username.isdigit():
        raise ValidationError(
            "Логин не может состоять только из цифр!"
        )

    if len(username) < 3:
        raise ValidationError(
            "Длина логина должна быть больше 3х символов"
        )

    if re.match(r'^(me|admin|moderator)$', username, flags=re.IGNORECASE):
        raise ValidationError(
            f'Использовать {username} в качестве username запрещено!'
        )

    result = re.findall(r'[^\w-]', username)
    if result:
        raise ValidationError(
            f'Не используйте \'{" ".join(_ for _ in set(result))}\' в нике!'
        )
    return
