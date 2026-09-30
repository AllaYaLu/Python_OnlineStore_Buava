from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect

# Создаем свою форму регистрации на лету, которая точно знает про твою модель users.User
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model() # Функция автоматически найдет твою кастомную модель

def register(request):
    if request.method == 'POST':
        # Используем НАШУ новую кастомную форму вместо стандартной
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        # И здесь тоже меняем на CustomUserCreationForm
        form = CustomUserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})
