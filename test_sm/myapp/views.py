
from django.contrib.auth.models import User
from .models import *
from django.db.models import Q
from datetime import date
from datetime import datetime
from django.db import transaction
from django.db.models import F
# F('donation_count') + 1 updates the donation_count directly in the database.
# It avoids potential race conditions when multiple updates happen at the same time


# import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, UpdateView, DeleteView, DetailView

from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views

from .forms import AdminProfileUpdateForm, CustomPasswordChangeForm, HospitalProfileUpdateForm



from .models import CustomUser, BloodRequest, DonorResponse 


#forms
from .forms import Login_form
from .forms import RegisterForm




# Create your views here.


def login_page(request):
    if request.method == "POST":
        form = Login_form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate using username instead of email (Modify if using CustomUser)
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.user_type == "2" and not user.is_approved:
                    messages.error(request, "Your account is pending approval by the admin.")
                else:
                    login(request, user)
                    return redirect("home")  # Redirect after login
            else:
                messages.error(request, "Invalid Email or Password")


    else:
        form = Login_form()

    context = {'form': form}
    return render(request, 'login.html', context)



def register_page(request):
    if request.method == "POST":
        print("Form submitted!")  # Debugging line
        print("POST Data:", request.POST)
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password

            if user.user_type == "2":  # If hospital staff
                user.is_approved = False  # Require admin approval
                messages.info(request, "Your registration is pending approval by the admin.")
                print("User Type:", user.user_type)
                print("Is Approved:", user.is_approved)

            else:
                user.is_approved = True  # Normal users are approved immediately
                messages.success(request, "Registration successful. Please log in.")

            # Calculate and update age if dob is provided
            if user.dob:
                user.age = user.calculate_age()
                user.save()  # Save the user with updated age

            user.save()
            print(user)
            messages.success(request, "Registration successful.")
            return redirect("login")  # Redirect to login page
        else:
            messages.error(request, "Error in registration. Please check your details.")
            print(form.errors)
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'register.html', context)

def logout_page(request):
    if request.user.is_authenticated:  # Use request.user instead of user
        logout(request)
    return redirect('login')  # Redirect to the login page after logout


# Check if the user is admin
def is_admin(user):
    return user.is_authenticated and user.user_type == "1"

def is_donor(user):
    return user.is_authenticated and user.user_type == "3"

def is_hospital(user):
    return user.is_authenticated and user.user_type == "2"

@login_required
def home(request):
    if request.user.user_type == "1":
        updated_count = update_ages()
        messages.success(request, f"Age updated for {updated_count} users.")
        return redirect("admin_dashboard")

    elif request.user.user_type == "2":
        return redirect("hospital_dashboard")  
    elif request.user.user_type == "3":
        return redirect("donor_dashboard")  
    else:
        messages.error(request, "Invalid user type.")
        return redirect("login")  # Redirect to login if user type is unknown


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, "admin/admin_dashboard.html")

@login_required
@user_passes_test(is_hospital)
def hospital_dashboard(request):
    return render(request, "hospital/hospital_dashboard.html")

@login_required
@user_passes_test(is_donor)
def donor_dashboard(request):
    return render(request, "donor/donor_dashboard.html")

@login_required
@user_passes_test(is_admin)
def approve_hospital(request, hospital_id):
    hospital = get_object_or_404(CustomUser, id=hospital_id, user_type="2")
    hospital.is_approved = True
    hospital.save()
    messages.success(request, "Hospital approved successfully.")
    return redirect("admin_dashboard")






@login_required
@user_passes_test(is_admin)
def pending_hospitals(request):
    query = request.GET.get('q', '')  # Get search query
    hospitals = CustomUser.objects.filter(user_type="2", is_approved=False)

    if query:
        hospitals = hospitals.filter(
            Q(organization_name__icontains=query) | Q(email__icontains=query)
        )

    return render(request, "admin/pending_hospitals.html", {"hospitals": hospitals, "query": query})




class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'admin/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        query = self.request.GET.get('q', '')  # Get search input
        users = CustomUser.objects.filter(user_type__in=[2, 3])

        if query:
            users = users.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )

        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')  # Pass query back to template
        return context

class UserDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'admin/user_detail.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if 'from_pending' is in the request (passed via GET parameter)
        context['from_pending'] = self.request.GET.get('from_pending', False)
        return context


# View for updating a user's information
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'email', 'is_approved', 'gender', 'profile_pic', 
              'dob', 'blood_group', 'contact_number', 'identity', 'organization_name', 'address']
    template_name = 'admin/user_form.html'
    context_object_name = 'user'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User details updated successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the user details.')
        return super().form_invalid(form)

# View for deleting a user
class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'admin/user_confirm_delete.html'
    context_object_name = 'user'
    success_url = reverse_lazy('user_list')

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect(self.success_url)

# Save view (admin can save user updates)
@staff_member_required
def save_user(request, pk):
    user = CustomUser.objects.get(id=pk)
    if request.method == "POST":
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
    return render(request, 'admin/save_user.html', {'user': user})


# add user
@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Save the user
            messages.success(request, 'User added successfully!')
            return redirect('user_list')  # Redirect to the user list after success
        else:
            messages.error(request, 'There were errors in your form. Please check the details and try again.')
    else:
        form = RegisterForm()

    return render(request, 'admin/add_user.html', {'form': form})


# Update the age for all users with user_type == "3"
def update_ages():
    today = date.today()
    users = CustomUser.objects.filter(user_type="3", dob__isnull=False)
    updated_count = 0

    for user in users:
        new_age = user.calculate_age()  # Access the calculate_age method from the user instance
        if user.age != new_age:
            user.age = new_age
            user.save(update_fields=["age"])  # Update the age field only
            updated_count += 1

    return updated_count

@login_required
@user_passes_test(is_admin)
def blood_inventory(request):
    """View and ensure all blood inventory records exist for the admin."""
    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    
    # Ensure all blood groups exist in inventory for the logged-in admin
    for bg in blood_groups:
        BloodInventory.objects.get_or_create(admin=request.user, blood_group=bg, defaults={'available_units': 0})
    
    # Fetch inventory for the logged-in admin
    inventory = BloodInventory.objects.filter(admin=request.user)
    
    return render(request, 'admin/blood_inventory.html', {'inventory': inventory})



@login_required
@user_passes_test(is_admin)
def add_blood_units(request, inventory_id):
    """Add blood units to inventory."""
    inventory = get_object_or_404(BloodInventory, id=inventory_id, admin=request.user)

    if request.method == "POST":
        units_to_add = float(request.POST['units'])
        inventory.available_units += units_to_add
        inventory.save()
        messages.success(request, f"Added {units_to_add} units to {inventory.blood_group} inventory.")
        return redirect('blood_inventory')

    return render(request, 'admin/add_blood_units.html', {'inventory': inventory})

@login_required
@user_passes_test(is_admin)
def subtract_blood_units(request, inventory_id):
    """Subtract blood units from inventory."""
    inventory = get_object_or_404(BloodInventory, id=inventory_id, admin=request.user)

    if request.method == "POST":
        units_to_subtract = float(request.POST['units'])
        
        if units_to_subtract > inventory.available_units:
            messages.error(request, "Not enough units available to subtract.")
        else:
            inventory.available_units -= units_to_subtract
            inventory.save()
            messages.success(request, f"Subtracted {units_to_subtract} units from {inventory.blood_group} inventory.")

        return redirect('blood_inventory')

    return render(request, 'admin/subtract_blood_units.html', {'inventory': inventory})

@login_required
@user_passes_test(is_admin)
def update_blood_inventory(request, inventory_id):
    """Update blood inventory record."""
    inventory = get_object_or_404(BloodInventory, id=inventory_id, admin=request.user)

    if request.method == "POST":
        new_units = float(request.POST['units'])
        inventory.available_units = new_units
        inventory.save()
        messages.success(request, f"Updated {inventory.blood_group} inventory to {new_units} units.")
        return redirect('blood_inventory')

    return render(request, 'admin/update_blood_inventory.html', {'inventory': inventory})



@login_required
@user_passes_test(is_admin)
def clear_blood_inventory(request, inventory_id):
    """Clear the available units (set to 0) for a given blood group."""
    inventory = get_object_or_404(BloodInventory, id=inventory_id, admin=request.user)
    
    if request.method == "POST":
        inventory.available_units = 0
        inventory.save()
        messages.success(request, f"Cleared all units for the {inventory.blood_group} blood group.")
        return redirect('blood_inventory')
    
    return redirect('admin/blood_inventory', {'inventory': inventory})  # In case of a non-POST request


@login_required
@user_passes_test(is_admin)
def request_blood(request):
    if request.method == "POST":
        blood_group = request.POST.get("blood_group")
        location = request.POST.get("location")

        # Create the BloodRequest object
        blood_request = BloodRequest.objects.create(
            admin=request.user,
            blood_group=blood_group,
            location=location,
        )

        # Send notifications to eligible donors (age between 18 and 50, user_type=3, and matching blood group)
        eligible_donors = CustomUser.objects.filter(
            user_type="3",  # User type = 3 (donors)
            blood_group=blood_group,  # Blood group must match
            age__gte=18,  # Age greater than or equal to 18
            age__lte=50  # Age less than or equal to 50
        )

        # Send notifications to each eligible donor
        for donor in eligible_donors:
            # Assuming you have a notification system in place (e.g., Firebase)
            # Example: send_notification(donor.fcm_token, "New Blood Request", f"A new blood request for {blood_group} blood is available.")
            print(f"Notification sent to {donor.email} for blood group {blood_group}")

        messages.success(request, "Blood request created successfully and sent to eligible donors.")
        return redirect("admin_dashboard")

    return render(request, "admin/blood_requests.html", {"blood_groups": CustomUser.BLOOD_GROUPS})




@login_required
@user_passes_test(is_admin)
def delete_blood_request(request, request_id):
    # Delete a blood request
    blood_request = get_object_or_404(BloodRequest, id=request_id, admin=request.user)
    blood_request.delete()
    
    messages.success(request, "Blood request deleted successfully.")
    return redirect('admin_blood_requests')



@login_required
@user_passes_test(is_donor)
def donor_response(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'accept':
            weight = request.POST.get("weight")
            height_str = request.POST.get("height")

            if not weight or not height_str:
                messages.error(request, "Weight and height are required to accept the request.")
                return redirect("donor_dashboard")

            try:
                weight = float(weight)
                
                # Split the height input into feet and inches
                feet, inches_part = height_str.split('.')
                feet = int(feet)
                inches_part = float(inches_part)  # Use the decimal as inches part
                
                # Convert the height into inches
                total_height_in_inches = feet * 12 + inches_part
                
                # Convert inches to meters
                height_in_meters = total_height_in_inches * 0.0254

                # Calculate BMI
                bmi = weight / (height_in_meters ** 2)
            except Exception:
                messages.error(request, "Invalid height or weight input.")
                return redirect("donor_dashboard")

            # Display BMI with healthy range message
            if bmi < 18.5:
                messages.warning(request, f"Your BMI is {bmi:.2f}, which indicates you are underweight. You cannot accept this blood request. The healthy BMI range is between 18.5 and 24.9.")
                return redirect("donor_dashboard")
            elif bmi > 24.9:
                messages.warning(request, f"Your BMI is {bmi:.2f}, which indicates you are overweight. You cannot accept this blood request. The healthy BMI range is between 18.5 and 24.9.")
                return redirect("donor_dashboard")
            else:
                DonorResponse.objects.create(
                    donor=request.user,
                    blood_request=blood_request,
                    is_accepted=True,
                    is_deleted=False
                )
                messages.success(request, f"Your BMI is {bmi:.2f}, which is healthy! You have accepted the blood request.")
        
        elif action == 'reject':
            DonorResponse.objects.create(
                donor=request.user,
                blood_request=blood_request,
                is_accepted=False,
                is_deleted=True
            )
            messages.success(request, "You have rejected the blood request.")

        return redirect("donor_dashboard")

    return render(request, "donor/blood_request_detail.html", {"blood_request": blood_request})



@login_required
@user_passes_test(is_donor)
def available_blood_requests(request):
    available_requests = BloodRequest.objects.filter(
        blood_group=request.user.blood_group
    ).exclude(
        responses__donor=request.user,
        responses__is_accepted=True
    ).exclude(
        responses__donor=request.user,
        responses__is_deleted=True
    ).exclude(
        responses__donor=request.user,
        responses__is_saved=True 
    )

    return render(request, "donor/available_blood_requests.html", {
        "available_requests": available_requests
    })




# @login_required
# @user_passes_test(is_admin)
# def save_blood_donation(request, response_id):
#     with transaction.atomic():
#         donor_response = DonorResponse.objects.get(id=response_id)

#         if request.method == "POST":
#             blood_unit_donated = request.POST['blood_unit_donated']
#             blood_group = donor_response.blood_request.blood_group

#             # Create Blood Donation History
#             BloodDonationHistory.objects.create(
#                 donor=donor_response.donor,
#                 blood_group=blood_group,
#                 blood_unit_donated=blood_unit_donated
#             )

#             # Update donation count
#             donor = donor_response.donor
#             donor.donation_count = F('donation_count') + 1  # Atomic update
#             donor.save()

#             # Update Inventory
#             inventory, created = BloodInventory.objects.get_or_create(
#                 admin=donor_response.blood_request.admin,
#                 blood_group=blood_group,
#                 defaults={'available_units': 0}
#             )
#             inventory.available_units += float(blood_unit_donated)
#             inventory.save()

#             # Remove donor from list
#             # donor_response.delete()
#             # Mark the response as saved instead of deleting
#             donor_response.is_saved = True
#             donor_response.save()

#             # Redirect
#             return redirect('view_blood_request', request_id=donor_response.blood_request.id)

#     return render(request, 'admin/blood_donation_form.html', {'donor_response': donor_response})
# @login_required
# @user_passes_test(is_admin)
# def save_blood_donation(request, response_id):
#     with transaction.atomic():
#         donor_response = DonorResponse.objects.get(id=response_id)

#         if request.method == "POST":
#             blood_unit_donated = request.POST['blood_unit_donated']
#             blood_group = donor_response.blood_request.blood_group
#             location = donor_response.blood_request.location  # Get the location from the blood request

#             # Create Blood Donation History, including location
#             BloodDonationHistory.objects.create(
#                 donor=donor_response.donor,
#                 blood_group=blood_group,
#                 blood_unit_donated=blood_unit_donated,
#                 location=location  # Save the location of the donation
#             )

#             # Update donation count
#             donor = donor_response.donor
#             donor.donation_count = F('donation_count') + 1  # Atomic update
#             donor.save()

#             # Update Inventory
#             inventory, created = BloodInventory.objects.get_or_create(
#                 admin=donor_response.blood_request.admin,
#                 blood_group=blood_group,
#                 defaults={'available_units': 0}
#             )
#             inventory.available_units += float(blood_unit_donated)
#             inventory.save()

#             # Mark the response as saved instead of deleting it
#             donor_response.is_saved = True
#             donor_response.save()

#             # Redirect
#             return redirect('view_blood_request', request_id=donor_response.blood_request.id)

#     return render(request, 'admin/blood_donation_form.html', {'donor_response': donor_response})
@login_required
@user_passes_test(is_admin)
def save_blood_donation(request, response_id):
    with transaction.atomic():
        donor_response = DonorResponse.objects.get(id=response_id)

        if request.method == "POST":
            blood_unit_donated = request.POST['blood_unit_donated']
            blood_group = donor_response.blood_request.blood_group
            location = donor_response.blood_request.location

            # 🛑 Avoid duplicate history entry
            history_exists = BloodDonationHistory.objects.filter(
                donor=donor_response.donor,
                blood_group=blood_group,
                location=location
            ).exists()

            if not history_exists:
                BloodDonationHistory.objects.create(
                    donor=donor_response.donor,
                    blood_group=blood_group,
                    blood_unit_donated=blood_unit_donated,
                    location=location
                )

                donor = donor_response.donor
                donor.donation_count = F('donation_count') + 1
                donor.save()

                inventory, created = BloodInventory.objects.get_or_create(
                    admin=donor_response.blood_request.admin,
                    blood_group=blood_group,
                    defaults={'available_units': 0}
                )
                inventory.available_units += float(blood_unit_donated)
                inventory.save()

            donor_response.is_saved = True
            donor_response.save()

            return redirect('view_blood_request', request_id=donor_response.blood_request.id)

    return render(request, 'admin/blood_donation_form.html', {'donor_response': donor_response})




@login_required
@user_passes_test(is_admin)
def admin_blood_requests(request):
    # List all blood requests created by the admin (newest first)
    blood_requests = BloodRequest.objects.filter(admin=request.user).order_by('-created_at')

    return render(request, 'admin/admin_blood_requests.html', {'blood_requests': blood_requests})


# @login_required
# @user_passes_test(is_admin)
# def view_blood_request(request, request_id):
#     # Get the specific blood request
#     blood_request = get_object_or_404(BloodRequest, id=request_id, admin=request.user)
    
#     # Get all accepted donors for this request
#     selected_donors = DonorResponse.objects.filter(blood_request=blood_request, is_accepted=True, is_select=True).order_by('-created_at')
#     unselected_donors = DonorResponse.objects.filter(blood_request=blood_request, is_accepted=True, is_select=False).order_by('-created_at')

#     return render(request, 'admin/view_blood_request.html', {
#         'blood_request': blood_request,
#         'selected_donors': selected_donors,
#         'unselected_donors': unselected_donors
#     })

@login_required
@user_passes_test(is_admin)
def view_blood_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id, admin=request.user)

    # Show only donors who haven't donated yet
    selected_donors = DonorResponse.objects.filter(
        blood_request=blood_request, 
        is_accepted=True, 
        is_select=True,
        is_saved=False
    ).order_by('-created_at')

    unselected_donors = DonorResponse.objects.filter(
        blood_request=blood_request, 
        is_accepted=True, 
        is_select=False
    ).order_by('-created_at')

    return render(request, 'admin/view_blood_request.html', {
        'blood_request': blood_request,
        'selected_donors': selected_donors,
        'unselected_donors': unselected_donors
    })


@login_required
@user_passes_test(is_admin)
def select_donor(request, response_id):
    donor_response = get_object_or_404(DonorResponse, id=response_id)
    
    if request.method == "POST":
        donor_response.is_select = True  # Assuming `is_select` is a boolean field
        donor_response.save()
        
        return redirect('view_blood_request', request_id=donor_response.blood_request.id)  # Redirect back to the blood request page

    return redirect('admin_blood_requests')  # Fallback redirection

@login_required
@user_passes_test(is_admin)
def unselect_donor(request, response_id):
    if request.method == "POST":
        donor_response = get_object_or_404(DonorResponse, id=response_id)
        donor_response.is_select = False  # Mark as unselected
        donor_response.save()
        messages.success(request, "Donor has been unselected.")
        return redirect('view_blood_request', request_id=donor_response.blood_request.id)





def custom_password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, '✅ Your password has been changed successfully.')
            return redirect('donor_profile')
        else:
            # Add detailed error messages
            if 'old_password' in form.errors:
                messages.error(request, '❌ Invalid old password.')
            if 'new_password2' in form.errors:
                messages.error(request, '❌ New passwords do not match.')
            if 'new_password1' in form.errors:
                messages.error(request, '❌ ' + form.errors['new_password1'][0])  # Show custom validation message
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'donor/password_change_modal.html', {'form': form})



@login_required
@user_passes_test(is_donor)
def donor_profile(request):
    """Shows a summary: profile picture, name, email, total donations, and buttons."""
    user = request.user
    context = {
        'user': user,
        'donation_count': user.donation_count,
    }
    return render(request, 'donor/profile_summary.html', context)

@login_required
@user_passes_test(is_donor)
def donor_profile_detail(request):
    """Shows all donor information and full blood donation history."""
    user = request.user
    donation_history = BloodDonationHistory.objects.filter(donor=user)

    donation_data = []
    for donation in donation_history:
        donation_data.append({
            'blood_group': donation.blood_group,
            'unit': donation.blood_unit_donated,
            'location': donation.location,  # Location now comes from BloodDonationHistory
            'donated_at': donation.donation_date,  # Fixed the field name
        })

    context = {
        'user': user,
        'donation_data': donation_data
    }
    return render(request, 'donor/profile_detail.html', context)





@login_required
def update_donor_profile(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name') or 'N/A'
        user.last_name = request.POST.get('last_name') or 'N/A'
        user.email = request.POST.get('email')
        
        # Convert dob (date of birth) to a datetime object if it's not empty
        dob = request.POST.get('dob')
        if dob:
            user.dob = datetime.strptime(dob, '%Y-%m-%d').date()  # Convert to date object
        
        user.blood_group = request.POST.get('blood_group') or None
        user.gender = request.POST.get('gender') or None
        # user.age = request.POST.get('age') or None
        user.contact_number = request.POST.get('contact_number') or None
        user.address = request.POST.get('address') or None

        # Handle file uploads
        if 'profile_pic' in request.FILES:
            user.profile_pic = request.FILES['profile_pic']
        if 'identity' in request.FILES:
            user.identity = request.FILES['identity']

        user.save()
        messages.success(request, "Your profile has been updated.")
        return redirect('donor_profile')

    context = {
        'user': user,
        'genders': CustomUser.GENDER,
        'blood_groups': CustomUser.BLOOD_GROUPS,
    }
    return render(request, 'donor/update_profile.html', context)


# Your custom admin check
def is_admin(user):
    return user.is_authenticated and user.user_type == "1"

@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'admin/profile_summary.html', context)

@login_required
@user_passes_test(is_admin)
def admin_profile_update(request):
    user = request.user
    if request.method == 'POST':
        form = AdminProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated successfully.')
            return redirect('admin_profile')
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        form = AdminProfileUpdateForm(instance=user)

    return render(request, 'admin/profile_update.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, '✅ Your password has been changed successfully.')
            return redirect('admin_profile')
        else:
            if 'old_password' in form.errors:
                messages.error(request, '❌ Invalid old password.')
            if 'new_password2' in form.errors:
                messages.error(request, '❌ New passwords do not match.')
            if 'new_password1' in form.errors:
                messages.error(request, '❌ ' + form.errors['new_password1'][0])
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'admin/change_password.html', {'form': form})


    #Hospital

@login_required
@user_passes_test(is_hospital)
def hospital_profile(request):
    hospital = request.user
    context = {
        'hospital': hospital
    }
    return render(request, 'hospital/profile_summary.html', context)

@login_required
@user_passes_test(is_hospital)
def hospital_profile_detail(request):
    hospital = request.user
    context = {
        'hospital': hospital
    }
    return render(request, 'hospital/profile_detail.html', context)

@login_required
@user_passes_test(is_hospital)
def hospital_profile_update(request):
    user = request.user
    if request.method == 'POST':
        form = HospitalProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated successfully.')
            return redirect('hospital_profile')
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        form = HospitalProfileUpdateForm(instance=user)

    return render(request, 'hospital/profile_update.html', {'form': form})

@login_required
@user_passes_test(is_hospital)
def hospital_password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, '✅ Your password has been changed successfully.')
            return redirect('hospital_profile')
        else:
            if 'old_password' in form.errors:
                messages.error(request, '❌ Invalid old password.')
            if 'new_password2' in form.errors:
                messages.error(request, '❌ New passwords do not match.')
            if 'new_password1' in form.errors:
                messages.error(request, '❌ ' + form.errors['new_password1'][0])
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'hospital/change_password.html', {'form': form})




# Admin to handle hospital request.


# @login_required
# def admin_manage_hospital_requests(request):
#     if request.user.user_type != "1":
#         return redirect('home')

#     pending_requests = HospitalBloodRequest.objects.filter(status='pending')
#     processing_requests = HospitalBloodRequest.objects.filter(status='processing')

#     context = {
#         'pending_requests': pending_requests,
#         'processing_requests': processing_requests,
#     }
#     return render(request, 'admin/hospital_requests.html', context)

# @login_required
# def admin_accept_request(request, request_id):
#     if request.user.user_type != "1":
#         return redirect('home')

#     if request.method == 'POST':
#         blood_request = get_object_or_404(HospitalBloodRequest, id=request_id)

#         try:
#             approved_units = float(request.POST.get('approved_units', 0))
#             if approved_units <= 0:
#                 messages.error(request, "Approved units must be greater than 0.")
#                 return redirect('admin_manage_hospital_requests')

#             blood_request.admin = request.user
#             blood_request.units_approved = approved_units
#             blood_request.status = 'processing'
#             blood_request.save()

#             messages.success(request, "Request accepted and moved to processing.")
#         except ValueError:
#             messages.error(request, "Invalid unit value.")

#     return redirect('admin_manage_hospital_requests')

# @login_required
# def admin_reject_request(request, request_id):
#     if request.user.user_type != "1":
#         return redirect('home')

#     blood_request = get_object_or_404(HospitalBloodRequest, id=request_id)
#     blood_request.status = 'rejected'
#     blood_request.save()

#     messages.info(request, "Request rejected.")
#     return redirect('admin_manage_hospital_requests')

# @login_required
# def admin_mark_delivered(request, request_id):
#     if request.user.user_type != "1":
#         return redirect('home')

#     blood_request = get_object_or_404(HospitalBloodRequest, id=request_id)

#     inventory = BloodInventory.objects.filter(
#         admin=request.user,
#         blood_group=blood_request.blood_group
#     ).first()

#     if inventory and inventory.available_units >= blood_request.units_approved:
#         inventory.available_units -= blood_request.units_approved
#         inventory.save()

#         blood_request.status = 'delivered'
#         blood_request.save()

#         messages.success(request, "Request marked as delivered and inventory updated.")
#     else:
#         messages.error(request, "Not enough inventory to fulfill this request.")

#     return redirect('admin_manage_hospital_requests')

# @login_required
# def admin_mark_failed(request, request_id):
#     if request.user.user_type != "1":
#         return redirect('home')

#     blood_request = get_object_or_404(HospitalBloodRequest, id=request_id)
#     blood_request.status = 'failed'
#     blood_request.save()

#     messages.warning(request, "Request marked as failed.")
#     return redirect('admin_manage_hospital_requests')
@login_required
def admin_manage_hospital_requests(request):
    if request.user.user_type != "1":
        return redirect('home')

    pending_requests = HospitalBloodRequest.objects.filter(status='pending')
    processing_requests = HospitalBloodRequest.objects.filter(status='processing')

    context = {
        'pending_requests': pending_requests,
        'processing_requests': processing_requests,
    }
    return render(request, 'admin/hospital_requests.html', context)


@login_required
def admin_accept_request(request, request_id):
    if request.user.user_type != "1":
        return redirect('home')

    if request.method == 'POST':
        blood_request = get_object_or_404(HospitalBloodRequest, id=request_id)

        try:
            approved_units = float(request.POST.get('approved_units', 0))
            if approved_units <= 0:
                messages.error(request, "Approved units must be greater than 0.")
                return redirect('admin_manage_hospital_requests')

            # Check inventory before accepting the request
            inventory = BloodInventory.objects.filter(
                admin=request.user,
                blood_group=blood_request.blood_group
            ).first()

            if not inventory or inventory.available_units < approved_units:
                messages.error(request, "Not enough inventory to fulfill this request.")
                return redirect('admin_manage_hospital_requests')

            # Deduct units immediately
            inventory.available_units -= approved_units
            inventory.save()

            # Update request status and approved units
            blood_request.admin = request.user
            blood_request.units_approved = approved_units
            blood_request.status = 'processing'
            blood_request.save()

            messages.success(request, "Request accepted and moved to processing. Inventory updated.")
        except ValueError:
            messages.error(request, "Invalid unit value.")

    return redirect('admin_manage_hospital_requests')


@login_required
def admin_reject_request(request, request_id):
    if request.user.user_type != "1":
        return redirect('home')

    blood_request = get_object_or_404(HospitalBloodRequest, id=request_id)
    blood_request.status = 'rejected'
    blood_request.save()

    messages.info(request, "Request rejected.")
    return redirect('admin_manage_hospital_requests')


@login_required
def admin_mark_delivered(request, request_id):
    if request.user.user_type != "1":
        return redirect('home')

    blood_request = get_object_or_404(HospitalBloodRequest, id=request_id)

    # Inventory deduction is already handled during acceptance, so no need to deduct again.

    if blood_request.status == 'processing':
        blood_request.status = 'delivered'
        blood_request.save()

        messages.success(request, "Request marked as delivered.")
    else:
        messages.error(request, "Request is not in a processable state.")

    return redirect('admin_manage_hospital_requests')


@login_required
def admin_mark_failed(request, request_id):
    if request.user.user_type != "1":
        return redirect('home')

    blood_request = get_object_or_404(HospitalBloodRequest, id=request_id)

    # If the request was accepted, and the status is processing, return the blood units back to inventory.
    if blood_request.status == 'processing':
        # Add the deducted units back to the inventory
        inventory = BloodInventory.objects.filter(
            admin=request.user,
            blood_group=blood_request.blood_group
        ).first()

        if inventory:
            inventory.available_units += blood_request.units_approved
            inventory.save()

        # Mark the request as failed
        blood_request.status = 'failed'
        blood_request.save()

        messages.warning(request, "Request marked as failed. Blood units have been returned to inventory.")
    else:
        messages.error(request, "Request cannot be marked as failed because it is not in processing.")

    return redirect('admin_manage_hospital_requests')



@login_required
def hospital_request_blood(request):
    if request.user.user_type != "2":  # Only hospitals
        messages.error(request, "You are not authorized to request blood.")
        return redirect('home')

    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units_requested = request.POST.get('units_requested')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')

        if not all([blood_group, units_requested, address, contact_number]):
            messages.error(request, "All fields are required.")
            return redirect('hospital_request_blood')

        try:
            units_requested = float(units_requested)
        except ValueError:
            messages.error(request, "Units must be a number.")
            return redirect('hospital_request_blood')

        HospitalBloodRequest.objects.create(
            hospital=request.user,
            hospital_name_snapshot=request.user.organization_name,
            hospital_email_snapshot=request.user.email,
            hospital_contact_snapshot=request.user.contact_number,
            hospital_address_snapshot=request.user.address,
            blood_group=blood_group,
            units_requested=units_requested,
            address=address,
            contact_number=contact_number
        )

        messages.success(request, "Blood request submitted successfully.")
        return redirect('hospital_dashboard')

    # Pass the BLOOD_GROUP choices from CustomUser model to the template
    blood_groups = CustomUser.BLOOD_GROUPS
    return render(request, 'hospital/request_blood.html', {'blood_groups': blood_groups})



@login_required
def hospital_view_requests(request):
    if request.user.user_type != "2":  # Only hospitals
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    pending_requests = HospitalBloodRequest.objects.filter(hospital=request.user, status='pending')
    processing_requests = HospitalBloodRequest.objects.filter(hospital=request.user, status='processing')
    delivered_requests = HospitalBloodRequest.objects.filter(hospital=request.user, status='delivered')
    rejected_requests = HospitalBloodRequest.objects.filter(hospital=request.user, status='rejected')
    failed_requests = HospitalBloodRequest.objects.filter(hospital=request.user, status='failed')

    context = {
        'pending_requests': pending_requests,
        'processing_requests': processing_requests,
        'delivered_requests': delivered_requests,
        'rejected_requests': rejected_requests,
        'failed_requests': failed_requests,
    }

    return render(request, 'hospital/view_requests.html', context)

@login_required
def hospital_delete_request(request, request_id):
    if request.user.user_type != "2":
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    blood_request = get_object_or_404(HospitalBloodRequest, id=request_id, hospital=request.user, status='pending')
    blood_request.delete()

    messages.success(request, "Request deleted successfully.")
    return redirect('hospital_view_requests')





