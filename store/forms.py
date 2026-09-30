from django import forms
from .models import Product

class CartForm(forms.Form):
    # Поле выбора товара (выпадающий список)
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(), 
        label="Выберите товар"
    )
    # Поле для ввода количества товара
    quantity = forms.IntegerField(
        min_value=1, 
        initial=1, 
        label="Количество"
    )
