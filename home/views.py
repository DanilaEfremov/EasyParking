from django.http import HttpResponse  # noqa: D100, EXE002
from django.shortcuts import render

from basket.utils import update_context_with_basket_data
from news.models import News


def home(request) -> HttpResponse:  # noqa: ANN001
    """Первая страница сайта.

    Args:
        request: запрос
    Returns:
        HttpResponse: Рендер домашней страницы.

    """
    context = { "news": News.objects.order_by("-created_at").all()[:3] }
    return render(request, "home.html", context=update_context_with_basket_data(request, context))
