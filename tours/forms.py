# tours/forms.py
from django import forms
from .models import Tour

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = [
            'title',
            'description',
            'location',
            'start_date',
            'end_date',
            'total_seats',
            'price_per_person',
            'cover_image',
            'emergency_contact'
        ]
