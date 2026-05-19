"""View-функции для приложения blog."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.db.models import Count, QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView,
)

from .models import Category, Comment, Post
from .forms import CommentForm, PostForm, UserProfileForm

POSTS_LIMIT = 10
User = get_user_model()


def get_published_posts() -> QuerySet:
    """Вернуть QuerySet с опубликованными постами."""
    return (
        Post.objects
        .select_related('location', 'author', 'category')
        .annotate(comment_count=Count('comments'))
        .filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        .order_by('-pub_date')
    )


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


class PostObjectMixin:
    """Переопределяет получение объекта поста по его id."""

    def get_object(self, queryset: QuerySet = None) -> Post:
        """Получить нужный пост по его id."""
        return get_object_or_404(Post, pk=self.kwargs['post_id'])


class CommentMixin:
    """Переопределяет методы получения объекта, редиректа и поле модели."""

    model = Comment

    def get_object(self, queryset: QuerySet = None) -> Comment:
        """Получить нужный комментарий по его id."""
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self) -> str:
        """Настроить динамический редирект после удаления комментария."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class ProfileListView(ListView):
    """CBV для отображения страницы пользователя.

    На странице пользователя выводятся его посты.
    """

    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/profile.html'

    def get_queryset(self) -> QuerySet:
        """Получить кверисет с постами определенного пользователя.

        Автор видит все свои посты, включая отложенные,
        а остальные пользователи — только опубликованные.
        """
        self.profile_user = get_object_or_404(
            User, username=self.kwargs['username'])
        if self.request.user == self.profile_user:
            return (
                Post
                .objects
                .filter(author=self.profile_user)
                .annotate(comment_count=Count('comments'))
                .select_related('location', 'author', 'category')
                .order_by('-pub_date')
            )
        return (
            get_published_posts()
            .filter(author=self.profile_user)
            .order_by('-pub_date')
        )

    def get_context_data(self, **kwargs: dict) -> dict:
        """Добавить объект пользователя в словарь контекста."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile_user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """CBV для изменения имени, фамилии, логина и адреса электронной почты.

    Доступно только авторизованным пользователям. После успешного
    изменения данных - редирект на страницу профиля.
    """

    model = User
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset: QuerySet = None) -> AbstractBaseUser:
        """Вернуть текущего аутентифицированного пользователя."""
        return self.request.user

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class IndexListView(ListView):
    """CBV для отображения главной страницы сайта."""

    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/index.html'

    def get_queryset(self) -> QuerySet:
        """Получить список опбликованных постов."""
        return get_published_posts()


class CategoryListView(ListView):
    """CBV для отображения страницы с постами определенной категории."""

    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet:
        """Получить кверисет с постами определенной категории."""
        self.category = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return get_published_posts().filter(category=self.category)

    def get_context_data(self, **kwargs: dict) -> dict:
        """Добавить объект категории в словарь контекста."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    """CBV для отображения определенного поста под указанным номером.

    Автор поста видит отложенные и снятые с публикации посты.
    """

    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset: QuerySet = None) -> Post:
        """Получение объекта поста с проверкой автора и флага опубликовано."""
        if self.request.user.is_authenticated:
            queryset = (
                get_published_posts()
                | Post.objects.filter(author=self.request.user).select_related(
                    'location', 'author', 'category'
                )
            )
        else:
            queryset = get_published_posts()
        return get_object_or_404(
            queryset,
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs) -> dict:
        """Добавить форму для комментариев в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV для отображения страницы создания публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form: PostForm) -> HttpResponse:
        """Добавление для публикации автора."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Настроить динамический редирект после создания публикации."""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(OnlyAuthorMixin, PostObjectMixin, UpdateView):
    """CBV для редактирования постов.

    Доступно только для автора поста. Если пользователь не автор -
    редирект на страницу просмотра поста.
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self) -> str:
        """Настроить динамический редирект после редактирования публикации."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(OnlyAuthorMixin, PostObjectMixin, DeleteView):
    """CBV для удаления поста.

    Доступно только для автора поста. Если пользователь не автор -
    редирект на страницу просмотра поста.
    """

    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self) -> str:
        """Настроить динамический редирект после удаления публикации."""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    """CBV для добавления комментария."""

    form_class = CommentForm
    comment_post = None
    template_name = 'blog/detail.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Найти нужный пост в самом начале запроса."""
        self.comment_post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: CommentForm) -> HttpResponse:
        """Присвоить объекту комментария автора и пост."""
        form.instance.author = self.request.user
        form.instance.post = self.comment_post
        return super().form_valid(form)


class CommentUpdateView(OnlyAuthorMixin, CommentMixin, UpdateView):
    """CBV для редактирования комментария.

    Доступно только для автора комментария. Если пользователь не автор -
    редирект на страницу просмотра поста.
    """

    form_class = CommentForm
    template_name = 'blog/comment.html'


class CommentDeleteView(OnlyAuthorMixin, CommentMixin, DeleteView):
    """CBV для удаления комментария.

    Доступно только для автора комментария. Если пользователь не автор -
    редирект на страницу просмотра поста.
    """

    template_name = 'blog/comment.html'
