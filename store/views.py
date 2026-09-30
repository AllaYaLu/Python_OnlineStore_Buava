from django.shortcuts import render, get_object_or_404, redirect 
from .models import Product, CartItem, Client, Order  
from .forms import CartForm

def product_list(request):
    # Извлекаем вообще все товары из нашей базы данных PostgreSQL
    products = Product.objects.all()
    
    # Кладывём их в словарь-контекст, чтобы HTML-шаблон их увидел
    context = {'products': products}
    
    # Отправляем пользователя на страницу со списком товаров
    return render(request, 'store/product_list.html', context)

# НАША НОВАЯ ФУНКЦИЯ ДЛЯ ОДНОГО ТОВАРА:
def product_detail(request, pk):
    # Ищет товар по его первичному ключу (ID). Если не находит — выдает ошибку 404.
    product = get_object_or_404(Product, pk=pk)
    
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)



def add_to_cart(request):
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            
            # Для учебного теста берём первого клиента из таблицы clients.
            # Если клиентов ещё нет, создадим тестового, чтобы сайт не падал.
            client, created = Client.objects.get_or_create(
                email="test_buyer@mail.ru",
                defaults={
                    "first_name": "Иван",
                    "last_name": "Тестовый",
                    "phone": "+79991112233",
                    "address": "Москва, ул. Ленина, д. 1"
                }
            )
            
            # Ищем, нет ли уже этого товара в корзине данного клиента
            cart_item, item_created = CartItem.objects.get_or_create(
                client=client,
                product=product,
                defaults={'quantity': quantity}
            )
            
            # Если товар уже был в корзине, просто увеличиваем его количество
            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()
                
            # Перенаправляем пользователя (пока на ту же страницу или на список товаров)
            return redirect('product_list')
    else:
        form = CartForm()
        
    return render(request, 'store/add_to_cart.html', {'form': form})



def cart_detail(request):
    # Как и в прошлом шаге, берем нашего тестового клиента
    client = Client.objects.filter(email="test_buyer@mail.ru").first()
    
    cart_items = []
    total_price = 0
    
    if client:
        # Извлекаем все товары из корзины этого клиента
        cart_items = CartItem.objects.filter(client=client).select_related('product')
        
        # Считаем стоимость для каждого товара и общую сумму корзины
        for item in cart_items:
            item.item_total = item.product.price * item.quantity
            total_price += item.item_total

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'store/cart_detail.html', context)


def create_order(request):
    # Берем нашего тестового клиента
    client = Client.objects.filter(email="test_buyer@mail.ru").first()
    
    if not client:
        return redirect('product_list')
        
    # Находим все товары в корзине этого клиента
    cart_items = CartItem.objects.filter(client=client)
    
    if not cart_items.exists():
        # Если корзина пуста, оформлять нечего — отправляем в каталог
        return redirect('product_list')
        
    # Считаем итоговую сумму заказа
    total_amount = 0
    for item in cart_items:
        total_amount += item.product.price * item.quantity
        
    # 1. Создаем новую запись в таблице заказов
    order = Order.objects.create(
        client=client,
        total_amount=total_amount,
        status='new' # Статус по умолчанию "Новый"
    )
    
    # 2. Очищаем корзину клиента (удаляем элементы из таблицы CartItem)
    cart_items.delete()
    
    # Передаем номер заказа на страницу успешного оформления
    return render(request, 'store/order_success.html', {'order': order})
