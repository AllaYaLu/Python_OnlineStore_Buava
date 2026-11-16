from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from store.models import Badge, Category, Client, Favorite, Order, Product, Stock

User = get_user_model()


class StoreModelsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Стратегии")
        self.badge = Badge.objects.create(name="Хит", color="#E05A2B", text_color="#FFFFFF")
        self.product_sale = Product.objects.create(
            title="Сумерки Империи",
            price=Decimal("8500.00"),
            deal_type="sale",
            badge=self.badge,
            category=self.category,
        )
        self.stock = Stock.objects.create(product=self.product_sale, quantity=5)

    def test_product_in_stock_property(self):
        """Проверка свойства in_stock при положительном и нулевом остатке."""
        self.assertTrue(self.product_sale.in_stock)

        self.stock.quantity = 0
        self.stock.save()
        self.product_sale.refresh_from_db()
        self.assertFalse(self.product_sale.in_stock)

    def test_product_clean_validation_sale_and_rent(self):
        """Проверка бизнес-валидации цен в зависимости от типа сделки (продажа/аренда)."""
        # Товар 'Только продажа' без цены покупки должен вызывать ValidationError
        invalid_sale = Product(title="Ошибка продажи", deal_type="sale", price=None)
        with self.assertRaises(ValidationError):
            invalid_sale.full_clean()

        # Товар 'Только аренда' без цены аренды должен вызывать ValidationError
        invalid_rent = Product(title="Ошибка аренды", deal_type="rent", rent_price=None)
        with self.assertRaises(ValidationError):
            invalid_rent.full_clean()

        # Корректный товар 'Продажа и аренда' с обеими ценами проходит проверку
        valid_both = Product(
            title="Бункер",
            deal_type="both",
            price=Decimal("2500.00"),
            rent_price=Decimal("400.00"),
        )
        valid_both.full_clean()

    def test_favorite_uniqueness(self):
        """Проверка, что пользователь не может добавить один товар в избранное дважды."""
        user = User.objects.create_user(username="gamer", email="gamer@example.com", password="password123")
        Favorite.objects.create(user=user, product=self.product_sale)

        with self.assertRaises(IntegrityError):
            Favorite.objects.create(user=user, product=self.product_sale)
