from django.urls import path

from users.views import register

from . import views

urlpatterns = [
    # Главная страница приложения store будет открывать наш список товаров
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/order/', views.create_order, name='create_order'),
    path('register/', register, name='register'),
]

