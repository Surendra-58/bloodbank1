from django.urls import path
from . import views


app_name = 'blog'  # ✅ This registers the 'blog' namespace

urlpatterns = [
    path('', views.blog_feed, name='blog_feed'),
    path('create/', views.create_post, name='create_post'),
    path('share/<int:post_id>/', views.share_post, name='share_post'),
    path('toggle-like/<int:post_id>/', views.toggle_like, name='toggle_like'),

    path('comment/<int:post_id>/', views.comment_on_post, name='comment_on_post'),
    path('profile/<int:user_id>/', views.user_blog_profile, name='user_blog_profile'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),

    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]