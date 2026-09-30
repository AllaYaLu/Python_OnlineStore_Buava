from django.contrib import admin
from .models import Category, Client, Product, Stock, CartItem, Order

# 1. Простая регистрация моделей
admin.site.register(Category)
admin.site.register(Client)
admin.site.register(CartItem)

# 2. Продвинутая регистрация для товаров (чтобы видеть цену и категорию списком)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'category') # Какие колонки показывать в таблице
    list_filter = ('category',)                         # Фильтр справа
    search_fields = ('title', 'description')            # Строка поиска по названию

# 3. Продвинутая регистрация для склада
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')

# 4. Продвинутая регистрация для заказов (чтобы удобно следить за статусами)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',) # Позволяет менять статус заказа прямо из общего списка!
