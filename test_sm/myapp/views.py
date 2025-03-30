
from django.contrib.auth.models import User
from .models import *
from django.db.models import Q


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



from .models import CustomUser, BloodRequest, DonorResponse, AcceptedDonor


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

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    hospitals = CustomUser.objects.filter(user_type="2", is_approved=False)
    blood_requests = BloodRequest.objects.all()
    context = {"hospitals": hospitals, "blood_requests": blood_requests}
    return render(request, "admin/admin_dashboard.html", context)

@login_required
@user_passes_test(is_admin)
def approve_hospital(request, hospital_id):
    hospital = get_object_or_404(CustomUser, id=hospital_id, user_type="2")
    hospital.is_approved = True
    hospital.save()
    messages.success(request, "Hospital approved successfully.")
    return redirect("admin_dashboard")


# @login_required
# @user_passes_test(is_admin)
# def request_blood(request):
#     if request.method == "POST":
#         BloodRequest.objects.create(
#             admin=request.user,
#             blood_group=request.POST.get("blood_group"),
#             location=request.POST.get("location"),
#         )
#         messages.success(request, "Blood request created successfully.")
#         # return redirect("admin_dashboard")

#     return render(request, "admin/blood_requests.html", {"blood_groups": CustomUser.BLOOD_GROUPS})

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
def manage_blood_requests(request):
    blood_requests = BloodRequest.objects.all()
    context = {"blood_requests": blood_requests}
    return render(request, "admin/manage_requests.html", context)

@login_required
@user_passes_test(is_admin)
def update_blood_request_status(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    if blood_request.status == "pending":
        blood_request.status = "processing"
    elif blood_request.status == "processing":
        blood_request.status = "completed"
    blood_request.save()
    messages.success(request, "Blood request status updated successfully.")
    return redirect("manage_blood_requests")





@login_required
def home(request):
    if request.user.user_type == "1":
        return redirect("admin_dashboard")
    # elif request.user.user_type == "2":
    #     return redirect("hospital_dashboard")  
    # elif request.user.user_type == "3":
    #     return redirect("donor_dashboard")  
    else:
        messages.error(request, "Invalid user type.")
        return redirect("login")  # Redirect to login if user type is unknown

# Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    hospitals = CustomUser.objects.filter(user_type="2", is_approved=False)
    blood_requests = BloodRequest.objects.all()
    return render(request, "admin/admin_dashboard.html", {"hospitals": hospitals, "blood_requests": blood_requests})


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

# View for deleting a user
class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'admin/user_confirm_delete.html'
    context_object_name = 'user'
    success_url = reverse_lazy('user_list')

# Save view (admin can save user updates)
@staff_member_required
def save_user(request, pk):
    user = CustomUser.objects.get(id=pk)
    if request.method == "POST":
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        return redirect('user_list')
    return render(request, 'admin/save_user.html', {'user': user})