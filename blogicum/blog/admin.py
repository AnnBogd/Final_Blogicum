"""Настройки админ-панели приложения blog."""

from django.contrib import admin

from .models import Category, Comment, Location, Post

COMMON_FIELDS = ('is_published', 'created_at')


class BaseAdmin(admin.ModelAdmin):
    """Базовая модель для дублирующейся конфигурации отображения."""

    list_display = COMMON_FIELDS
    list_editable = ('is_published',)
    list_filter = COMMON_FIELDS


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    """Конфигурация отображения категорий в административной панели."""

    list_display = (
        'title',
        'description',
        'slug',
    ) + BaseAdmin.list_display

    list_editable = ('description', ) + BaseAdmin.list_editable
    search_fields = ('title',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(BaseAdmin):
    """Конфигурация отображения местоположения в административной панели."""

    list_display = ('name',) + BaseAdmin.list_display
    search_fields = ('name',)
    list_display_links = ('name',)


@admin.register(Post)
class PostAdmin(BaseAdmin):
    """Конфигурация отображения публикаций в административной панели."""

    list_display = (
        'title',
        'author',
        'location',
        'category',
        'pub_date',
        'text',
    ) + BaseAdmin.list_display

    search_fields = (
        'title',
        'author__username',
        'category__title',
        'text',
    )

    list_filter = (
        'author',
        'category',
        'pub_date',
    ) + BaseAdmin.list_filter

    list_select_related = ('author', 'location', 'category',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Конфигурация отображения комментариев в административной панели."""

    list_display = ('text', 'post', 'created_at', 'author')
    search_fields = ('post__title', 'author__username', 'text')
    list_select_related = ('post', 'author')
    list_filter = ('created_at', 'author')
