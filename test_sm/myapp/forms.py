from django import forms
from .models import CustomUser  # Import CustomUser model


class Login_form(forms.Form):
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput(), required=True)

class RegisterForm(forms.ModelForm):
    contact_number = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "contact number"}) ,required=True)  # Enforce required field
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "password"}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "confirm-password",}), required=True)
    organization_identity = forms.ImageField(required=False)
    dob = forms.DateField(widget=forms.DateInput(attrs={"type": "date", 'class': 'form-control'}), required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Enter your address"}), required=True)
    organization_name = forms.CharField(required=False, widget=forms.PasswordInput(attrs={"placeholder": "organization name",}))
    first_name = forms.CharField(required=False , widget=forms.PasswordInput(attrs={"placeholder": "First name"}))
    last_name = forms.CharField(required=False, widget=forms.PasswordInput(attrs={"placeholder": "Last name"}))

    class Meta:
        model = CustomUser
        fields = ["email", "user_type", "gender", "profile_pic", "address", "identity",
                  "contact_number", "dob", "blood_group", "organization_name", "address", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # Filter user_type to exclude "Admin" (1)
        self.fields["user_type"].choices = [choice for choice in self.fields["user_type"].choices if choice[0] in ["2", "3"]]
        
        # Conditional field requirement based on user_type
        user_type = self.initial.get('user_type', '3')  # Default to "User" if not specified
        if user_type == "2":  # Hospital type
            self.fields["dob"].required = False
            self.fields["gender"].required = False
            self.fields["blood_group"].required = False
            self.fields["first_name"].required = False
            self.fields["last_name"].required = False

    def clean_user_type(self):
        user_type = self.cleaned_data.get("user_type")
        return str(user_type)  # Convert user_type to a string

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        user_type = cleaned_data.get("user_type")
        organization_identity = cleaned_data.get("organization_identity")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        if user_type == "2" and not cleaned_data.get("organization_name"):
            raise forms.ValidationError("Organization name is required.")

        if user_type == "2" and not organization_identity:
            raise forms.ValidationError("Organization must upload an identity document.")

        if user_type == "3":  # Regular user must provide first and last name
            if not cleaned_data.get("first_name") or not cleaned_data.get("last_name"):
                raise forms.ValidationError("First name and Last name are required for users.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["user_type"] == "2":  # If hospital
            user.is_staff = True
            user.identity = self.cleaned_data["organization_identity"]

        if commit:
            user.save()
        return user


