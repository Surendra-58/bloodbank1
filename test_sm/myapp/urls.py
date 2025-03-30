from django.urls import path
from . import views


# app_name = 'myapp'  # Set app_name as 'myapp'

urlpatterns = [
    path("login/", views.login_page, name='login'),
    path("", views.home, name='home'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),

    path('adminn/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-hospital/<int:hospital_id>/', views.approve_hospital, name='approve_hospital'),
    path('request-blood/', views.request_blood, name='request_blood'),
    path('manage-requests/', views.manage_blood_requests, name='manage_blood_requests'),
    path('update-request-status/<int:request_id>/', views.update_blood_request_status, name='update_blood_request_status'),
    path("pending-hospitals/", views.pending_hospitals, name="pending_hospitals"),

    path('userlist/', views.UserListView.as_view(), name='user_list'),
    path('update/<int:pk>/', views.UserUpdateView.as_view(), name='user_update'),
    path('delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),

    # path('user/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),

    path('save/<int:pk>/', views.save_user, name='save_user'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),


 ]

