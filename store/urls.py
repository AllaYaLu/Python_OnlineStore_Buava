from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    # Корзина и заказ
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/<str:action>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("order/create/", views.create_order, name="create_order"),
    # Избранное и Сравнение
    path("favorites/", views.favorite_list, name="favorite_list"),
    path("favorites/toggle/<int:product_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("compare/", views.compare_list, name="compare_list"),
    path("compare/toggle/<int:product_id>/", views.toggle_compare, name="toggle_compare"),
]