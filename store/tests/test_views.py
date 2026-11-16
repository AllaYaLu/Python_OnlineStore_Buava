from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import CartItem, Category, Client, Order, Product, Stock

User = get_user_model()


class StoreViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer1",
            email="buyer1@example.com",
            password="strongpassword123",
            first_name="Анна",
            last_name="Иванова",
        )
        self.category = Category.objects.create(name="Детективы")
        self.game = Product.objects.create(
            title="Место преступления",
            description="Увлекательный настольный детектив.",
            price=Decimal("3000.00"),
            rent_price=Decimal("500.00"),
            deal_type="both",
            category=self.category,
        )
        self.stock = Stock.objects.create(product=self.game, quantity=4)

    def test_home_and_catalog_pages_load(self):
        """Проверка доступности Главной страницы, Каталога и Детальной карточки."""
        home_resp = self.client.get(reverse("home"))
        self.assertEqual(home_resp.status_code, 200)
        self.assertContains(home_resp, "Место преступления")

        catalog_resp = self.client.get(reverse("product_list"))
        self.assertEqual(catalog_resp.status_code, 200)
        self.assertContains(catalog_resp, "Увлекательный настольный детектив.")

        detail_resp = self.client.get(
            reverse("product_detail", kwargs={"pk": self.game.pk})
        )
        self.assertEqual(detail_resp.status_code, 200)

    def test_add_to_cart_sale_and_rent_separately(self):
        """Проверка раздельного добавления покупки и аренды одной игры в корзину."""
        self.client.login(username="buyer1", password="strongpassword123")

        # Добавляем покупку
        self.client.post(
            reverse("add_to_cart", kwargs={"product_id": self.game.id}),
            {"deal_type": "sale"},
        )
        # Добавляем аренду
        self.client.post(
            reverse("add_to_cart", kwargs={"product_id": self.game.id}),
            {"deal_type": "rent"},
        )

        client_profile = Client.objects.get(email="buyer1@example.com")
        items = CartItem.objects.filter(client=client_profile)
        self.assertEqual(items.count(), 2)

        # Проверяем итоговую сумму в корзине (3000 + 500 = 3500)
        cart_resp = self.client.get(reverse("cart_detail"))
        self.assertEqual(cart_resp.status_code, 200)
        self.assertEqual(cart_resp.context["total_price"], Decimal("3500.00"))

    def test_create_order_clears_cart_and_reduces_stock(self):
        """Проверка оформления заказа: создается Order, корзина очищается, остаток уменьшается."""
        self.client.login(username="buyer1", password="strongpassword123")
        self.client.post(
            reverse("add_to_cart", kwargs={"product_id": self.game.id}),
            {"deal_type": "sale"},
        )

        order_resp = self.client.post(reverse("create_order"))
        self.assertEqual(order_resp.status_code, 200)

        client_profile = Client.objects.get(email="buyer1@example.com")
        self.assertEqual(Order.objects.filter(client=client_profile).count(), 1)
        self.assertEqual(Order.objects.first().total_amount, Decimal("3000.00"))
        self.assertEqual(CartItem.objects.filter(client=client_profile).count(), 0)

        # Проверяем, что остаток на складе уменьшился с 4 до 3
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 3)

    def test_compare_session_for_anonymous_user(self):
        """Проверка работы сравнения игр через сессию для неавторизованного гостя."""
        self.client.get(reverse("toggle_compare", kwargs={"product_id": self.game.id}))
        self.assertIn(self.game.id, self.client.session.get("compare_ids", []))

        compare_resp = self.client.get(reverse("compare_list"))
        self.assertEqual(compare_resp.status_code, 200)
        self.assertContains(compare_resp, "Место преступления")
