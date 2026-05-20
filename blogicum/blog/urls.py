"""URL для приложения blog."""

from django.urls import include, path

from .views import (
    CategoryListView,
    CommentCreateView,
    CommentDeleteView,
    CommentUpdateView,
    IndexListView,
    PostCreateView,
    PostDetailView,
    PostDeleteView,
    PostUpdateView,
    ProfileListView,
    ProfileUpdateView
)

app_name = 'blog'

posts_pattern_urls = [
    path(
        'edit_comment/<int:comment_id>/',
        CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'delete_comment/<int:comment_id>/',
        CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'comment/',
        CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'delete/',
        PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'edit/',
        PostUpdateView.as_view(),
        name='edit_post'
    ),
    path('', PostDetailView.as_view(), name='post_detail'),
]

urlpatterns = [
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path(
        'edit_profile/',
        ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path('posts/<int:post_id>/', include(posts_pattern_urls)),
    path(
        'category/<slug:category_slug>/',
        CategoryListView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/<str:username>/',
        ProfileListView.as_view(),
        name='profile'
    ),
    path('', IndexListView.as_view(), name='index'),
]
