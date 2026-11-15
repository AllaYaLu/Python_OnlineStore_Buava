from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    patronymic = models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
