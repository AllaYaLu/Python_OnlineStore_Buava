from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from store.models import Client, Order

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Электронная почта")
    first_name = forms.CharField(max_length=50, required=True, label="Имя")
    last_name = forms.CharField(max_length=50, required=True, label="Фамилия")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "patronymic", "email", "phone", "address")
        widgets = {
            "address": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Город, улица, дом, квартира"}
            ),
        }


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Сразу создаем или находим карточку Клиента для заказов
            Client.objects.get_or_create(
                email=user.email,
                defaults={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone or f"user_{user.id}",
                    "address": user.address or "Не указан",
                },
            )
            login(request, user)
            return redirect("product_list")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    user = request.user
    client = Client.objects.filter(email=user.email).first()
    orders = (
        Order.objects.filter(client=client).order_by("-created_at") if client else []
    )

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save()
            # Синхронизируем обновленные данные с моделью Client
            if client:
                client.first_name = updated_user.first_name
                client.last_name = updated_user.last_name
                client.patronymic = updated_user.patronymic
                if updated_user.phone:
                    client.phone = updated_user.phone
                if updated_user.address:
                    client.address = updated_user.address
                client.save()
            messages.success(request, "Данные профиля успешно сохранены!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=user)

    context = {
        "form": form,
        "orders": orders,
    }
    return render(request, "users/profile.html", context)
