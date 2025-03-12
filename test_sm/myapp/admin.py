

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


# class UserModel(UserAdmin):
#     ordering = ('email',)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "user_type", "gender", "created_at","is_superuser","is_active",)
    search_fields = ("email",)
    ordering = ("email",)

    # Remove 'username' and explicitly define fields
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("gender", "profile_pic", "address")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
        ("Other Info", {"fields": ("user_type", "fcm_token")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email","profile_pic","address", "password1", "password2", "user_type", "gender"),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)



# admin.site.register(CustomUser, UserModel)