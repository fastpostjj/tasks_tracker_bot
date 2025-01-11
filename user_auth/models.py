from django.contrib.auth.models import AbstractUser
from django.db import models
from config.settings import NULLABLE


# Create your models here.

class User(AbstractUser):

    """
    Пользователь телеграм
    chat_id
    email
    phone
    """

    username = None
    chat_id = models.IntegerField(
        verbose_name="chat_id",
        unique=True,
        **NULLABLE
    )
    email = models.EmailField(
        verbose_name='почта',
        **NULLABLE
    )
    phone = models.CharField(
        max_length=35,
        verbose_name='телефон',
        **NULLABLE
    )
    is_subscripted = models.BooleanField(
        verbose_name="Подписан",
        default=False)

    USERNAME_FIELD = 'chat_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.chat_id}"
