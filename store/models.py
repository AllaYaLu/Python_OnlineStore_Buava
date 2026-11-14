import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from PIL import Image


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


# 1. ТАБЛИЦА КЛИЕНТОВ
class Client(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Номер телефона")
    address = models.TextField(verbose_name="Адрес доставки")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# 2. ТАБЛИЦА ТОВАРОВ
class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Изображение товара")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Категория")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image:
            file_root, ext = os.path.splitext(self.image.name)
            if ext.lower() == ".jfif":
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=85)

                new_name = f"{os.path.basename(file_root)}.jpg"
                self.image.save(new_name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)


# 3. ТАБЛИЦА ЗАПАСОВ НА СКЛАДЕ
class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")

    class Meta:
        verbose_name = "Запас на складе"
        verbose_name_plural = "Запасы на складе"

    def __str__(self):
        return f"Запас для {self.product.title}: {self.quantity} шт."


# 4. ТАБЛИЦА КОРЗИНЫ
class CartItem(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"
        unique_together = ('client', 'product')

    def __str__(self):
        return f"{self.product.title} в корзине {self.client.first_name}"


# 5. ТАБЛИЦА ЗАКАЗОВ
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('paid', 'Оплачен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    ]

    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Клиент")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая сумма")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new', verbose_name="Статус заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заказа")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.id} от {self.created_at.strftime('%d.%m.%Y')}"
