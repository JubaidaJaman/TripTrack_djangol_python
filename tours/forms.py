from django import forms
from .models import Tour, Booking, Review, UAPDepartment, Wishlist

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ('title', 'description', 'category', 'department', 'price', 
                 'duration_hours', 'max_participants', 'meeting_point', 
                 'tour_date', 'includes', 'requirements', 'itinerary', 'image')
        widgets = {
            'tour_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'includes': forms.Textarea(attrs={'rows': 3}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
            'itinerary': forms.Textarea(attrs={'rows': 5}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('participants', 'special_requirements', 'payment_method')
        widgets = {
            'special_requirements': forms.Textarea(attrs={'rows': 3}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class UAPDepartmentForm(forms.ModelForm):
    class Meta:
        model = UAPDepartment
        fields = ('name', 'code', 'description', 'image')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }