from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from users.validators import validate_username


class User(AbstractUser):
    """Кастомная модель пользователя для расширения в будущем"""

    email = models.EmailField(_('email address'), blank=False, unique=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[validate_username],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = (
        'email', 'first_name', 'last_name', 'password'
    )
