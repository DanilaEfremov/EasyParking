from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from shop.views import calculate_cart_total
from .models import News


def home(request):
    context = {
        'news': News.objects.order_by('-created_at').all()[:3]
    }
    if request.user.is_authenticated:
        total, count = calculate_cart_total(request)
        context.update({
            'items_count': count,
            'subtotal': total,
            'delivery_price': 0,
            # 'news': news,
        })
    return render(request, 'home.html', context)


def news_detail(request, news_id):
    """Страница с деталями новости."""
    context = {
        'news': get_object_or_404(News, id=news_id)
    }
    if request.user.is_authenticated:
        total, count = calculate_cart_total(request)
        context.update({
            'items_count': count,
            'subtotal': total,
            'delivery_price': 0,
        })
    return render(request, 'news_detail.html', context=context)


def news(request):
    template = 'partials/news.html' if request.htmx else 'news.html'
    news = News.objects.all().order_by('-created_at')
    paginator = Paginator(news, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    if request.user.is_authenticated:
        total, count = calculate_cart_total(request)
        context.update({
            'items_count': count,
            'subtotal': total,
            'delivery_price': 0,
        })
    return render(request, template_name=template, context=context)

