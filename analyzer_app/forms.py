from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Validate proper email format
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")

        # Prevent duplicate emails
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
        
def clean_username(self):
    username = self.cleaned_data.get("username")

    if not username.isalnum():
        raise forms.ValidationError("Username should contain only letters and numbers.")

    return username