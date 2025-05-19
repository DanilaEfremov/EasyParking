import structlog  # noqa: D100, EXE002
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from basket.utils import update_context_with_basket_data

from .forms import AddressUpdateForm, CustomPasswordChangeForm, CustomUserCreationForm, UserUpdateForm
from .models import add_tables

logger = structlog.get_logger(__name__)


def register_view(request) -> HttpResponse:  # noqa: ANN001
    """Регистрация покупателя."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            add_tables(user)
            login(request, user)
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request) -> HttpResponse:  # noqa: ANN001
    """Вход в систему."""
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы успешно вошли!")
            logger.info("User entered", user_id=user.id)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request) -> HttpResponse:  # noqa: ANN001
    """Выход покупателя из системы."""
    logout(request)
    messages.success(request, "Вы вышли из системы.")
    return redirect("home")


@login_required
def account(request) -> HttpResponse:  # noqa: ANN001
    """Профиль покупателя."""
    return render(
        request,
        "account.html",
        context=update_context_with_basket_data(request, {}),
    )


@login_required
def account_personal_change(request) -> HttpResponse:   # noqa: ANN001
     """Страница с изменением личных данных."""         # noqa: RUF002
     user = request.user
     if request.method == "POST":
         form = UserUpdateForm(request.POST, instance=user)
         if form.is_valid():
             form.save()
             return redirect("account")
     else:
         form = UserUpdateForm(instance=user)
     context = { "form": form }
     return render(
         request,
         "account_personal_change.html",
         context=update_context_with_basket_data(request, context),
     )


@login_required
def account_password_change(request) -> HttpResponse:  # noqa: ANN001
    """Страница с изменением пароля."""  # noqa: RUF002
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Обновляем сессию, чтобы не разлогинивало
            logger.info("User changed password", user=form.user, id=form.user.id)
            return redirect("account")
    else:
        form = CustomPasswordChangeForm(request.user)
    context = { "form": form }
    return render(
        request,
        "account_password_change.html",
        context=update_context_with_basket_data(request, context),
    )


@login_required
def account_address_change(request) -> HttpResponse:    # noqa: ANN001
    """Страница с изменением адреса."""                 # noqa: RUF002
    user = request.user.profile
    if request.method == "POST":
        form = AddressUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("account")
    else:
        form = AddressUpdateForm(instance=user)
    context = { "form": form }
    return render(request,"account_address_change.html", context=context)
