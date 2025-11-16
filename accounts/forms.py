#accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, TouristProfile, OrganizerProfile, EmergencyContact


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'phone', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class TouristProfileForm(forms.ModelForm):
    class Meta:
        model = TouristProfile
        fields = ('student_id', 'department', 'semester', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class OrganizerProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizerProfile
        fields = ('department', 'organizer_id', 'bio')


# NEW: Emergency Contact Form
class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ('full_name', 'relationship', 'phone', 'email', 'address', 'is_primary')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace('+', '').replace(' ', '').isdigit():
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone