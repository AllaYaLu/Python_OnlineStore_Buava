from django.contrib import admin
from django.utils.html import format_html

from .models import Badge, CartItem, Category, Client, Order, Product, Stock


class StockInline(admin.StackedInline):
    model = Stock
    extra = 1


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "badge_preview")
    list_display_links = ("id", "name")
    search_fields = ("name",)

    @admin.display(description="Предпросмотр бейджа")
    def badge_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold; font-size: 12px; display: inline-block;">{}</span>',
            obj.color,
            obj.text_color,
            obj.name,
        )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id",)
    list_editable = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_preview",
        "title",
        "price",
        "rent_price",
        "deal_type",
        "badge",
        "category",
    )
    list_display_links = ("id", "title")
    list_editable = ("price", "rent_price", "deal_type", "badge")
    list_filter = ("category", "deal_type", "badge")
    search_fields = ("title", "description")

    inlines = [StockInline]

    @admin.display(description="Фото")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height: 50px; border-radius: 6px;" />',
                obj.image.url,
            )
        return "Нет фото"


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity")
    list_editable = ("quantity",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)


admin.site.register(Client)
admin.site.register(CartItem)
