from django.core.paginator import Paginator  # noqa: D100, EXE002
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from basket.utils import update_context_with_basket_data

from .models import News


def news(request) -> HttpResponse:  # noqa: ANN001
    """Страница со списком всех новостей.

    Args:
        request (WSGIRequest): запрос
    Returns:
        HttpResponse: шаблон страницы со списком всех новостей.

    """  # noqa: RUF002
    template = "partials/news.html" if request.htmx else "news.html"
    news = News.objects.all().order_by("-created_at")
    paginator = Paginator(news, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = { "page_obj": page_obj }
    return render(request, template_name=template, context=update_context_with_basket_data(request, context))


def news_detail(request, news_id: int) -> HttpResponse:  # noqa: ANN001
    """Страница с деталями новости.

    Args:
        request (WSGIRequest): запрос
        news_id (int): id новости, которую необходимо показать
    Returns:
        HttpResponse: шаблон страницы с новостью, которую запрашивает пользователь

    """  # noqa: RUF002
    context = { "news": get_object_or_404(News, id=news_id) }
    return render(request, "news_detail.html", context=update_context_with_basket_data(request, context))

