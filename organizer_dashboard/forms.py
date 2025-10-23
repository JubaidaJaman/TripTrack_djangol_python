# organizer_dashboard/forms.py
from django import forms
from tours.models import Tour  # we'll use the Tour model from tours app

class OrganizerTourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = [
            'title', 'description', 'location', 'emergency_contact',
            'start_date', 'end_date', 'total_seats', 'price_per_person',
            'cover_image', 'published'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
