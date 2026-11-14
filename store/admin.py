from django.contrib import admin
from django.utils.html import format_html

from .models import CartItem, Category, Client, Order, Product, Stock

admin.site.register(Client)
admin.site.register(CartItem)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id",)
    list_editable = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "image_preview", "title", "price", "category")
    list_display_links = ("id", "title")
    list_filter = ("category",)
    search_fields = ("title", "description")

    @admin.display(description="Фото")
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 6px;" />', obj.image.url)
        return "Нет фото"


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

    
    