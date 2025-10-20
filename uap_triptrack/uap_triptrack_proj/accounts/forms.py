from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import User
import re
from django.core.exceptions import ValidationError

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
    role = forms.ChoiceField(choices=[(User.TOURIST,'Tourist'),(User.ORGANIZER,'Tour Organizer')], widget=forms.Select)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, validators=[validate_password_complexity])
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username','email','role','phone','password1','password2','first_name','last_name')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return email
