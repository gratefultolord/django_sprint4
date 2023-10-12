from django.urls import include, path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path('posts/<int:pk>/', include([
        path('', views.PostDetailView.as_view(), name='post_detail'),
        path('edit/', views.PostUpdateView.as_view(), name='edit_post'),
        path('delete/', views.PostDeleteView.as_view(), name='delete_post'),
        path('comment/', views.add_comment, name='add_comment'),
        path('edit_comment/<int:comment_id>/', views.edit_comment,
             name='edit_comment'),
        path('delete_comment/<int:comment_id>', views.delete_comment,
             name='delete_comment'),
    ])),
    path(
        'profile/<username>/',
        views.UserPostsView.as_view(),
        name='profile'
    ),
    path(
        'edit_profile/',
        views.UserEditView.as_view(),
        name='edit_profile'
    ),
    path(
        'category/<slug:category>/',
        views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
]
