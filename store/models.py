from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название категории")

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

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# 2. ТАБЛИЦА ТОВАРОВ
class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Изображение товара")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Категория")

    def __str__(self):
        return self.title


# 3. ТАБЛИЦА ЗАПАСОВ НА СКЛАДЕ
class Stock(models.Model):
    # OneToOneField гарантирует, что у одного товара может быть только одна запись о складских запасах (UNIQUE в SQL)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")

    def __str__(self):
        return f"Запас для {self.product.title}: {self.quantity} шт."


# 4. ТАБЛИЦА КОРЗИНЫ
class CartItem(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        # Этот блок запрещает добавлять один и тот же товар в корзину одного клиента дважды отдельными строками
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

    def __str__(self):
        return f"Заказ №{self.id} от {self.created_at.strftime('%d.%m.%Y')}"
