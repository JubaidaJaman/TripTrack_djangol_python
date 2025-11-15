from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, TouristProfile, OrganizerProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    
    # FIXED: Remove department field from user creation form
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'phone', 'password1', 'password2')
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        # FIXED: Remove department validation since it's not in the form anymore
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