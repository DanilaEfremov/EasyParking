from django.http import HttpResponse  # noqa: D100, EXE002
from django.shortcuts import render

from basket.utils import update_context_with_basket_data


def about(request) -> HttpResponse:  # noqa: ANN001
    """Страница 'О себе'."""  # noqa: RUF002
    return render(request, "about.html", context=update_context_with_basket_data(request, {}))
