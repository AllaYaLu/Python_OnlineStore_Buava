from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import BooleanField, Case, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache

from .models import CartItem, Category, Client, Favorite, Order, Product


def _get_or_create_client(user):
    """Вспомогательная функция: связывает авторизованного User с карточкой Client."""
    client, _ = Client.objects.get_or_create(
        email=user.email or f"{user.username}@example.com",
        defaults={
            "first_name": user.first_name or user.username,
            "last_name": user.last_name or "",
            "patronymic": getattr(user, "patronymic", "") or "",
            "phone": getattr(user, "phone", "") or f"user_{user.id}",
            "address": getattr(user, "address", "") or "Не указан",
        },
    )
    return client


def home(request):
    """Главная страница: компактные карточки БЕЗ длинного описания."""
    products = (
        Product.objects.select_related("category", "badge", "stock")
        .annotate(
            is_available=Case(
                When(stock__quantity__gt=0, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
        .order_by("-is_available", "-id")[:8]
    )

    categories = Category.objects.all()
    favorite_ids = (
        list(
            Favorite.objects.filter(user=request.user).values_list(
                "product_id", flat=True
            )
        )
        if request.user.is_authenticated
        else []
    )
    compare_ids = request.session.get("compare_ids", [])

    context = {
        "products": products,
        "categories": categories,
        "favorite_ids": favorite_ids,
        "compare_ids": compare_ids,
    }
    return render(request, "store/home.html", context)


def product_list(request):
    """Страница Каталог: карточки С описанием, фильтрами по категориям, типу сделки и поиском."""
    products = Product.objects.select_related("category", "badge", "stock").annotate(
        is_available=Case(
            When(stock__quantity__gt=0, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    )

    categories = Category.objects.all()

    category_id = request.GET.get("category")
    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))

    deal_type = request.GET.get("deal")
    if deal_type in ("sale", "rent"):
        products = products.filter(Q(deal_type=deal_type) | Q(deal_type="both"))

    search_query = request.GET.get("q", "").strip()
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    sort_by = request.GET.get("sort", "")
    if sort_by == "price_asc":
        products = products.order_by("-is_available", "price", "rent_price")
    elif sort_by == "price_desc":
        products = products.order_by("-is_available", "-price", "-rent_price")
    else:
        products = products.order_by("-is_available", "-id")

    favorite_ids = (
        list(
            Favorite.objects.filter(user=request.user).values_list(
                "product_id", flat=True
            )
        )
        if request.user.is_authenticated
        else []
    )
    compare_ids = request.session.get("compare_ids", [])

    context = {
        "products": products,
        "categories": categories,
        "selected_category": int(category_id)
        if category_id and category_id.isdigit()
        else None,
        "selected_deal": deal_type,
        "search_query": search_query,
        "sort_by": sort_by,
        "favorite_ids": favorite_ids,
        "compare_ids": compare_ids,
    }
    return render(request, "store/product_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category", "badge", "stock"), pk=pk
    )
    is_favorite = (
        Favorite.objects.filter(user=request.user, product=product).exists()
        if request.user.is_authenticated
        else False
    )
    is_compared = product.id in request.session.get("compare_ids", [])
    return render(
        request,
        "store/product_detail.html",
        {"product": product, "is_favorite": is_favorite, "is_compared": is_compared},
    )


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
    return redirect(request.META.get("HTTP_REFERER", "product_list"))


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related(
        "product", "product__badge", "product__stock"
    )
    products = [f.product for f in favorites]
    return render(request, "store/favorites.html", {"products": products})


def toggle_compare(request, product_id):
    get_object_or_404(Product, id=product_id)
    compare_ids = request.session.get("compare_ids", [])
    if product_id in compare_ids:
        compare_ids.remove(product_id)
    else:
        if len(compare_ids) < 4:  # Ограничим сравнение до 4 игр
            compare_ids.append(product_id)
    request.session["compare_ids"] = compare_ids
    return redirect(request.META.get("HTTP_REFERER", "product_list"))


def compare_list(request):
    compare_ids = request.session.get("compare_ids", [])
    products = Product.objects.filter(id__in=compare_ids).select_related(
        "category", "badge", "stock"
    )
    return render(request, "store/compare.html", {"products": products})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not product.in_stock:
        messages.error(request, f"К сожалению, «{product.title}» сейчас нет на складе.")
        return redirect(request.META.get("HTTP_REFERER", "product_list"))

    deal_type = request.POST.get("deal_type", "sale")
    client = _get_or_create_client(request.user)
    cart_item, created = CartItem.objects.get_or_create(
        client=client, product=product, deal_type=deal_type
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    action_label = "в аренду" if deal_type == "rent" else "для покупки"
    cart_url = reverse("cart_detail")
    catalog_url = reverse("product_list")

    # Формируем удобное сообщение с быстрыми переходами
    msg = mark_safe(
        f"Игра <strong>«{product.title}»</strong> добавлена в корзину ({action_label})! "
        f'<a href="{cart_url}" class="toast-link">Перейти в корзину</a> или '
        f'<a href="{catalog_url}" class="toast-link">выбрать ещё в каталоге</a>.'
    )
    messages.success(request, msg)

    # Возвращаем пользователя ровно на ту страницу, где он нажал кнопку
    return redirect(request.META.get("HTTP_REFERER", "product_list"))


@never_cache
@login_required
def cart_detail(request):
    client = _get_or_create_client(request.user)
    items = (
        CartItem.objects.filter(client=client)
        .select_related("product", "product__stock")
        .order_by("id")
    )
    total_price = 0
    for item in items:
        unit_price = (
            item.product.rent_price if item.deal_type == "rent" else item.product.price
        )
        item.subtotal = (unit_price or 0) * item.quantity
        total_price += item.subtotal
    return render(
        request, "store/cart_detail.html", {"items": items, "total_price": total_price}
    )


@login_required
def update_cart_item(request, item_id, action):
    client = _get_or_create_client(request.user)
    item = get_object_or_404(CartItem, id=item_id, client=client)

    if action == "increase":
        # Проверяем, хватает ли товара на складе
        max_stock = item.product.stock.quantity if hasattr(item.product, "stock") else 0
        if item.quantity < max_stock:
            item.quantity += 1
            item.save()
    elif action == "decrease":
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    return redirect("cart_detail")


@login_required
def remove_cart_item(request, item_id):
    client = _get_or_create_client(request.user)
    item = get_object_or_404(CartItem, id=item_id, client=client)
    item.delete()
    return redirect("cart_detail")


@login_required
def create_order(request):
    client = _get_or_create_client(request.user)
    items = CartItem.objects.filter(client=client).select_related(
        "product", "product__stock"
    )
    if items.exists():
        total_price = sum(
            (
                (
                    item.product.rent_price
                    if item.deal_type == "rent"
                    else item.product.price
                )
                or 0
            )
            * item.quantity
            for item in items
        )
        order = Order.objects.create(client=client, total_amount=total_price)
        for item in items:
            if hasattr(item.product, "stock"):
                item.product.stock.quantity = max(
                    0, item.product.stock.quantity - item.quantity
                )
                item.product.stock.save()
        items.delete()
        return render(request, "store/order_success.html", {"order": order})
    return redirect("product_list")
