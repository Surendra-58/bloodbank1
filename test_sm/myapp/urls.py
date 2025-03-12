from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login_page, name='login'),
    path("", views.home, name='home'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),

 ]

