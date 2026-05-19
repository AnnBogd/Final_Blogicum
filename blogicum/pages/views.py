"""View-функции для приложения pages."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Отобразить кастомную страницу с ошибкой 404.

    Args:
        request: экземпляр HttpRequest.
        exception: экземпляр Exception.

    Returns:
        HttpResponse: рендерит шаблон '404.html'.
    """
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    """Отобразить кастомную страницу с ошибкой проверки CSRF токена.

    Args:
        request: экземпляр HttpRequest.
        reason: строка.

    Returns:
        HttpResponse: рендерит шаблон '403csrf.html'.
    """
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request: HttpRequest) -> HttpResponse:
    """Отобразить кастомную страницу с ошибкой 500.

    Args:
        request: экземпляр HttpRequest.

    Returns:
        HttpResponse: рендерит шаблон '500.html'.
    """
    return render(request, 'pages/500.html', status=500)
