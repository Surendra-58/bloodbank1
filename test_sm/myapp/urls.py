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
    path('add_user/', views.add_user, name='add_user'),

    path('userlist/', views.UserListView.as_view(), name='user_list'),
    path('update/<int:pk>/', views.UserUpdateView.as_view(), name='user_update'),
    path('delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),

    # path('user/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),

    path('save/<int:pk>/', views.save_user, name='save_user'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),

    #admin blood request
    path('admin/blood-requests/', views.admin_blood_requests, name='admin_blood_requests'),
    path('admin/blood-request/<int:request_id>/', views.view_blood_request, name='view_blood_request'),
    path('admin/blood-request/delete/<int:request_id>/', views.delete_blood_request, name='delete_blood_request'),
    # path('admin/donor-response/delete/<int:response_id>/', views.delete_donor_response, name='delete_donor_response'),
    path('select-donor/<int:response_id>/', views.select_donor, name='select_donor'),
    path("unselect-donor/<int:response_id>/", views.unselect_donor, name="unselect_donor"),
    path('save_blood_donation/<int:response_id>/', views.save_blood_donation, name='save_blood_donation'),


    # Donor
    path('donor/dashboard/', views.donor_dashboard, name='donor_dashboard'),  
    path('donor/available-requests/', views.available_blood_requests, name='available_blood_requests'),  
    path('donor/response/<int:request_id>/', views.donor_response, name='donor_response'), 

    path('inventory/', views.blood_inventory, name='blood_inventory'),
    path('inventory/add/<int:inventory_id>/', views.add_blood_units, name='add_blood_units'),
    path('inventory/subtract/<int:inventory_id>/', views.subtract_blood_units, name='subtract_blood_units'),
    path('inventory/update/<int:inventory_id>/', views.update_blood_inventory, name='update_blood_inventory'),
    # path('inventory/delete/<int:inventory_id>/', views.delete_blood_inventory, name='delete_blood_inventory'),
    path('admin/blood-inventory/clear/<int:inventory_id>/', views.clear_blood_inventory, name='clear_blood_inventory'),


 ]

