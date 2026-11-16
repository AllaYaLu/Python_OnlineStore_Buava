import os
from decimal import Decimal
from io import BytesIO

from colorfield.fields import ColorField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import models
from PIL import Image


class Badge(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название бейджа")
    color = ColorField(default="#FF5722", verbose_name="Цвет фона бейджа")
    text_color = ColorField(default="#FFFFFF", verbose_name="Цвет текста")

    class Meta:
        verbose_name = "Бейдж"
        verbose_name_plural = "Бейджи"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=255, unique=True, verbose_name="Название категории"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


# 1. ТАБЛИЦА КЛИЕНТОВ
class Client(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    patronymic = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Отчество"
    )
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
    DEAL_TYPE_CHOICES = [
        ("sale", "Только продажа"),
        ("rent", "Только аренда"),
        ("both", "Продажа и аренда"),
    ]

    badge = models.ForeignKey(
        Badge, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Бейдж"
    )

    title = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Цена покупки",
    )
    rent_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Цена аренды (за сутки)",
    )
    deal_type = models.CharField(
        max_length=10,
        choices=DEAL_TYPE_CHOICES,
        default="sale",
        verbose_name="Тип предложения",
    )

    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name="Изображение товара"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title

    @property
    def in_stock(self):
        """Удобное свойство для шаблонов: возвращает True, если товар есть на складе."""
        return hasattr(self, "stock") and self.stock.quantity > 0

    def save(self, *args, **kwargs):
        """Автоматически конвертирует изображения .jfif в .jpg для корректного отображения в браузерах."""
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

    def clean(self):
        super().clean()
        if self.deal_type == "sale":
            if not self.price:
                raise ValidationError(
                    {
                        "price": "Для типа «Только продажа» необходимо указать цену покупки."
                    }
                )
            self.rent_price = None  # Обнуляем неиспользуемую цену, чтобы в базе не оставалось устаревших значений при смене типа сделки

        elif self.deal_type == "rent":
            if not self.rent_price:
                raise ValidationError(
                    {
                        "rent_price": "Для типа «Только аренда» необходимо указать цену аренды."
                    }
                )
            self.price = None  # Очищаем лишнюю цену покупки

        elif self.deal_type == "both":
            errors = {}
            if not self.price:
                errors["price"] = "Укажите цену покупки."
            if not self.rent_price:
                errors["rent_price"] = "Укажите цену аренды."
            if errors:
                raise ValidationError(errors)


# 3. ТАБЛИЦА ЗАПАСОВ НА СКЛАДЕ
class Stock(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        default=0, verbose_name="Количество на складе"
    )

    class Meta:
        verbose_name = "Запас на складе"
        verbose_name_plural = "Запасы на складе"

    def __str__(self):
        return f"Запас для {self.product.title}: {self.quantity} шт."


# 4. ТАБЛИЦА КОРЗИНЫ
class CartItem(models.Model):
    DEAL_CHOICES = [
        ("sale", "Покупка"),
        ("rent", "Аренда"),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    deal_type = models.CharField(
        max_length=10, choices=DEAL_CHOICES, default="sale", verbose_name="Тип сделки"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"
        unique_together = ("client", "product", "deal_type")


# 5. ТАБЛИЦА ЗАКАЗОВ
class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("paid", "Оплачен"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
    ]

    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Клиент")
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Итоговая сумма"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус заказа",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания заказа"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.id} от {self.created_at.strftime('%d.%m.%Y')}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Товар",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} -> {self.product.title}"
