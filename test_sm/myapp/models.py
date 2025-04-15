from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

from django.db.models import Q


# from django.contrib.auth import get_user_model
# from django.db.models.signals import post_save
# from django.dispatch import receiver

from django.core.validators import MinValueValidator





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
        extra_fields.setdefault("user_type", "1")

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
    user_type = models.CharField(default="3", choices=USER_TYPE, max_length=3)
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
    age = models.IntegerField(null=True, blank=True)  # Store age directly in the database, for user_type 3 only
        # New field to track the number of times a donor has donated
    donation_count = models.IntegerField(default=0)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def calculate_age(self):
        """Calculate and return the current age based on date of birth (dob)."""
        if self.dob:
            today = date.today()
            age = today.year - self.dob.year
            if (today.month, today.day) < (self.dob.month, self.dob.day):
                age -= 1
            return age
        return None

    def save(self, *args, **kwargs):
        """Ensure age updates on user save if the user_type is '3'."""
        if self.dob and self.user_type == "3":
            current_age = self.calculate_age()
            if self.age != current_age:
                self.age = current_age
        super().save(*args, **kwargs)

    def __str__(self):
        # If user_type is "3" (User), return first and last name
        if self.user_type == "3":
            return f"{self.last_name or ''}, {self.first_name or ''}"

        # If user_type is "2" (Hospital), return organization name
        if self.user_type == "2":
            return self.organization_name or "Organization Name"

        # Default return: email if other conditions are not met
        return self.email or "No Email"

class BloodRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    )
    
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': "1"})
    blood_group = models.CharField(max_length=4, choices=CustomUser.BLOOD_GROUPS)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class DonorResponse(models.Model):
    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': "3"})
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name="responses")
    is_accepted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Add is_deleted field
    is_select = models.BooleanField(default=False)  # Added field to track selection
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # If any DonorResponse is accepted, update the BloodRequest status to 'processing'
        if self.is_accepted:
            self.blood_request.status = "processing"
            self.blood_request.save()


class BloodDonationHistory(models.Model):
    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': "3"})
    blood_group = models.CharField(max_length=4, choices=CustomUser.BLOOD_GROUPS)
    blood_unit_donated = models.FloatField()
    location = models.CharField(max_length=255)  # Add this field to store location
    donation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} - {self.blood_group} - {self.donation_date}"

class BloodInventory(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': "1"})
    blood_group = models.CharField(max_length=4, choices=CustomUser.BLOOD_GROUPS)
    available_units = models.FloatField()
    # donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} - {self.blood_group} - {self.available_units} units"



# class AcceptedDonor(models.Model):
#     blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE)
#     donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': "3"})
#     is_donation_completed = models.BooleanField(default=False)
#     updated_at = models.DateTimeField(auto_now=True)


# Hospital:
from django.db import models
from .models import CustomUser

class HospitalBloodRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]

    hospital = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        limit_choices_to={'user_type': '2'},
        null=True,
        blank=True,
        related_name='hospital_requests'
    )

    # Snapshots to preserve even if hospital is deleted
    hospital_name_snapshot = models.CharField(max_length=100, null=True, blank=True)
    hospital_email_snapshot = models.EmailField(null=True, blank=True)
    hospital_contact_snapshot = models.CharField(max_length=15, null=True, blank=True)
    hospital_address_snapshot = models.TextField(null=True, blank=True)

    admin = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        limit_choices_to={'user_type': '1'},
        null=True,
        blank=True,
        related_name='admin_handled_requests'
    )

    blood_group = models.CharField(max_length=4, choices=CustomUser.BLOOD_GROUPS)
    units_requested = models.FloatField()
    units_approved = models.FloatField(null=True, blank=True)

    address = models.TextField()
    contact_number = models.CharField(max_length=15)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hospital_name_snapshot or 'Unknown Hospital'} - {self.blood_group} - {self.status}"
