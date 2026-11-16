from django.db.models import Sum

from .models import CartItem, Client, Favorite


def header_counters(request):
    # Сравнение (работает и для гостей, и для пользователей)
    compare_count = len(request.session.get("compare_ids", []))

    favorites_count = 0
    cart_count = 0

    if request.user.is_authenticated:
        favorites_count = Favorite.objects.filter(user=request.user).count()
        client = Client.objects.filter(email=request.user.email).first()
        if client:
            total_qty = CartItem.objects.filter(client=client).aggregate(
                total=Sum("quantity")
            )["total"]
            cart_count = total_qty or 0

    return {
        "compare_count": compare_count,
        "favorites_count": favorites_count,
        "cart_count": cart_count,
    }
