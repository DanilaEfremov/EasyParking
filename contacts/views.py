from django.http import HttpResponse  # noqa: D100, EXE002
from django.shortcuts import render

from basket.utils import update_context_with_basket_data


def contacts(request) -> HttpResponse:  # noqa: ANN001
    """Страница 'Контакты'."""
    return render(request, "contact-us.html", context=update_context_with_basket_data(request, {}))

