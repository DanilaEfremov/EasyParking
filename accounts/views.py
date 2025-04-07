from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
import structlog

from .forms import CustomUserCreationForm, UserUpdateForm, CustomPasswordChangeForm, AddressUpdateForm
from .models import add_tables
from shop.views import calculate_cart_total

logger = structlog.get_logger(__name__)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            add_tables(user)
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли!')
            logger.info(f"user {user.id} entered")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы.')
    return redirect('home')


@login_required
def account(request):
    total, count = calculate_cart_total(request)
    context = {
        'items_count': count,
        'subtotal': total,
        'delivery_price': 0,
    }
    """Страница с информацией о пользователе."""
    return render(request, 'accounts/account.html', context=context)


@login_required
def account_personal_change(request):
     """Страница с изменением личных данных."""
     total, count = calculate_cart_total(request)
     user = request.user
     if request.method == 'POST':
         form = UserUpdateForm(request.POST, instance=user)
         if form.is_valid():
             form.save()
             return redirect('account')
     else:
         form = UserUpdateForm(instance=user)
     context = {
         'items_count': count,
         'subtotal': total,
         'delivery_price': 0,
         'form': form,
     }
     return render(request, 'accounts/account_personal_change.html', context=context)


@login_required
def account_password_change(request):
     """Страница с изменением пароля."""
     total, count = calculate_cart_total(request)
     if request.method == 'POST':
         form = CustomPasswordChangeForm(request.user, request.POST)
         if form.is_valid():
             user = form.save()
             update_session_auth_hash(request, user)  # Обновляем сессию, чтобы не разлогинивало
             logger.info(f"user {user.id} changed password")
             return redirect('account')
     else:
         form = CustomPasswordChangeForm(request.user)
     context = {
         'items_count': count,
         'subtotal': total,
         'delivery_price': 0,
         'form': form,
     }
     return render(request, 'accounts/account_password_change.html', context=context)\



@login_required
def account_adress_change(request):
     """Страница с изменением адреса."""
     total, count = calculate_cart_total(request)
     user = request.user.profile
     if request.method == 'POST':
         form = AddressUpdateForm(request.POST, instance=user)
         if form.is_valid():
             form.save()
             return redirect('account')
     else:
         form = AddressUpdateForm(instance=user)
     context = {
         'items_count': count,
         'subtotal': total,
         'delivery_price': 0,
         'form': form,
     }
     return render(request, 'accounts/account_adress_change.html', context=context)