from django import forms
from .models import Tour

class TourForm(forms.ModelForm):
    date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    class Meta:
        model = Tour
        fields = ['title','description','location','date','capacity','price','image','emergency_contact']
