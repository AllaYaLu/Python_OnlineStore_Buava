from django.db.models import Sum

from .models import CartItem, Client, Favorite


def header_counters(request):
    # 1. Сравнение (работает и для гостей, и для пользователей)
    compare_count = len(request.session.get("compare_ids", []))

    # 2. Избранное и Корзина (для авторизованных пользователей)
    favorites_count = 0
    cart_count = 0

    if request.user.is_authenticated:
        favorites_count = Favorite.objects.filter(user=request.user).count()
        client = Client.objects.filter(email=request.user.email).first()
        if client:
            # Считаем общее количество штук в корзине (если поле пустое, вернет 0)
            total_qty = CartItem.objects.filter(client=client).aggregate(
                total=Sum("quantity")
            )["total"]
            cart_count = total_qty or 0

    return {
        "compare_count": compare_count,
        "favorites_count": favorites_count,
        "cart_count": cart_count,
    }
