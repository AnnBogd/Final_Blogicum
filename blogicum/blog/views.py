"""View-функции для приложения blog."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.db.models import Count, QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView,
)

from .mixins import CommentMixin, OnlyAuthorMixin
from .models import Category, Post
from .forms import CommentForm, PostForm, UserProfileForm

POSTS_LIMIT = 10
User = get_user_model()


def get_posts_queryset(is_filtered=False, is_annotate=False) -> QuerySet:
    """Вернуть QuerySet с опубликованными постами и доп параметрами."""
    queryset = Post.objects.select_related('location', 'author', 'category')
    if is_filtered:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    if is_annotate:
        queryset = (queryset
                    .annotate(comment_count=Count('comments'))
                    .order_by('-pub_date'))
    return queryset


class ProfileListView(ListView):
    """CBV для отображения страницы пользователя.

    На странице пользователя выводятся его посты.
    """

    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/profile.html'

    @cached_property
    def profile_user(self) -> AbstractBaseUser:
        """Получить объект пользователя."""
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self) -> QuerySet:
        """Получить кверисет с постами определенного пользователя.

        Автор видит все свои посты, включая отложенные,
        а остальные пользователи — только опубликованные.
        """
        if self.request.user == self.profile_user:
            queryset = get_posts_queryset(is_annotate=True)
        else:
            queryset = get_posts_queryset(is_filtered=True, is_annotate=True)
        return queryset.filter(author=self.profile_user)

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
        return get_posts_queryset(is_filtered=True, is_annotate=True)


class CategoryListView(ListView):
    """CBV для отображения страницы с постами определенной категории."""

    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/category.html'

    @cached_property
    def category(self) -> Category:
        """Получить объект категории."""
        return get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug'])

    def get_queryset(self) -> QuerySet:
        """Получить кверисет с постами определенной категории."""
        return (
            get_posts_queryset(is_filtered=True, is_annotate=True)
            .filter(category=self.category)
        )

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
        needed_post = get_object_or_404(
            get_posts_queryset(is_filtered=False, is_annotate=True),
            pk=self.kwargs['post_id']
        )
        if self.request.user != needed_post.author and (
            not needed_post.is_published
            or not needed_post.category.is_published
            or needed_post.pub_date > timezone.now()
        ):
            raise Http404()
        return needed_post

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


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """CBV для редактирования постов.

    Доступно только для автора поста. Если пользователь не автор -
    редирект на страницу просмотра поста.
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self) -> str:
        """Настроить динамический редирект после редактирования публикации."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """CBV для удаления поста.

    Доступно только для автора поста. Если пользователь не автор -
    редирект на страницу просмотра поста.
    """

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self) -> str:
        """Настроить динамический редирект после удаления публикации."""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    """CBV для добавления комментария."""

    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form: CommentForm) -> HttpResponse:
        """Присвоить объекту комментария автора и пост."""
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
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
