"""Миксины для CBV приложения blog."""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Comment


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для проверки автора поста или комментария.

    Если пользователь не автор — редирект на страницу просмотра поста.
    """

    def test_func(self) -> bool:
        """Проверить, является ли пользователь автором объекта."""
        return (self.request.user.is_authenticated
                and self.get_object().author == self.request.user)

    def handle_no_permission(self):
        """Редирект на страницу просмотра поста."""
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs['post_id']
        )


class CommentMixin:
    """Переопределяет методы получения объекта, редиректа и поле модели."""

    model = Comment

    def get_object(self, queryset: QuerySet = None) -> Comment:
        """Получить нужный комментарий по его id и id поста."""
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post_id=self.kwargs['post_id']
        )

    def get_success_url(self) -> str:
        """Настроить динамический редирект после удаления комментария."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
