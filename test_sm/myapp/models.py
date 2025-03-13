from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.db import models
from django.contrib.auth.models import AbstractUser




class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)  #calling model using email not username
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "admin")

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    USER_TYPE = (("1", "Admin"), ("2", "Hospital"), ("3", "User"))
    GENDER = [("M", "Male"), ("F", "Female"),("O","Other")]
    BLOOD_GROUPS = (
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),

    )

    first_name = models.CharField(max_length=15,null=True,blank=True,default='N/A')
    last_name = models.CharField(max_length=15,null=True,blank=True,default='N/A')
    
    
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    is_approved = models.BooleanField(default=False)  # New field for staff approval
    user_type = models.CharField(default=3, choices=USER_TYPE, max_length=3)
    gender = models.CharField(max_length=1, choices=GENDER,null=True,blank=True)
    profile_pic = models.ImageField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=4, choices=BLOOD_GROUPS,null=True,blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    identity = models.ImageField(null=True,blank=True)
    organization_name = models.CharField(max_length=80, null=True,blank=True)
    # organization_identity = models.ImageField(null=True,blank=True)
    # is_organization = models.BooleanField(default=False)  # New field to track organizations
    address = models.TextField(null=True,blank=True)
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        # If user_type is "3" (User), return first and last name
        if self.user_type == "3":
            return f"{self.last_name or ''}, {self.first_name or ''}"

        # If user_type is "2" (Hospital), return organization name
        if self.user_type == "2":
            return self.organization_name or "Organization Name"

        # Default return: email if other conditions are not met
        return self.email or "No Email"