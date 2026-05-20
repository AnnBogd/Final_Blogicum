"""Формы приложения blog."""
from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для создания новых постов."""

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'location',
            'category',
            'image',
            'is_published'
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            )
        }


class CommentForm(forms.ModelForm):
    """Форма для написания комментария."""

    class Meta:
        model = Comment
        fields = ('text',)


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования данных пользователя в профиле."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
