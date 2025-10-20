from django import forms
from .models import Tour

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = [
            'title',
            'location',
            'tour_date',
            'payment_deadline',
            'fee',
            'description'
        ]
        widgets = {
            'tour_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_deadline': forms.DateInput(attrs={'type': 'date'}),
        }
