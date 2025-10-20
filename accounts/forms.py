from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import re
from django.core.exceptions import ValidationError

# Password complexity validator
def validate_password_complexity(value):
    if len(value) < 8 or len(value) > 12:
        raise ValidationError("Password must be between 8 and 12 characters.")
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', value):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', value):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r'[^A-Za-z0-9]', value):
        raise ValidationError("Password must contain at least one special character.")

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            (CustomUser.TOURIST, 'Tourist'),
            (CustomUser.ORGANIZER, 'Tour Organizer'),
            (CustomUser.DEVELOPER, 'Developer')
        ],
        widget=forms.Select
    )
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, validators=[validate_password_complexity])
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'phone', 'avatar', 'password1', 'password2', 'first_name', 'last_name')

    # Ensure unique email
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return email
