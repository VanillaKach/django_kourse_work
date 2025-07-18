from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager  # Импорт менеджера


class User(AbstractUser):
    username = None  # Отключаем username
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'  # Используем email для аутентификации
    REQUIRED_FIELDS = []  # Убираем username из обязательных полей

    objects = UserManager()  # Подключаем кастомный менеджер

    def __str__(self):
        return self.email
