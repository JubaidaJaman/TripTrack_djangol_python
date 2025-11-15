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

# tours/forms.py - ADD THESE FORMS
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('title', 'message', 'notification_type', 'tour', 'send_to_all_tourists', 'target_users', 'scheduled_send')
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your notification message...'}),
            'scheduled_send': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'target_users': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        organizer = kwargs.pop('organizer', None)
        super().__init__(*args, **kwargs)
        
        # Only show organizer's tours
        if organizer:
            self.fields['tour'].queryset = Tour.objects.filter(organizer=organizer)
        
        # Only show tourists for target users
        self.fields['target_users'].queryset = User.objects.filter(user_type='tourist')
        
        # Make target_users not required if sending to all
        self.fields['target_users'].required = False

class QuickReminderForm(forms.Form):
    tour = forms.ModelChoiceField(queryset=Tour.objects.none(), required=True)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Quick reminder message...'}),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        organizer = kwargs.pop('organizer', None)
        super().__init__(*args, **kwargs)
        
        if organizer:
            self.fields['tour'].queryset = Tour.objects.filter(organizer=organizer, status='published')



class BookingForm(forms.ModelForm):
    payment_number = forms.CharField(
        required=False,
        max_length=20,
        help_text="Enter your bKash/Nagad/Rocket number"
    )
    
    class Meta:
        model = Booking
        fields = ('participants', 'special_requirements', 'payment_method', 'payment_number')
        widgets = {
            'special_requirements': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        payment_number = cleaned_data.get('payment_number')
        
        # Require payment number for mobile payment methods
        if payment_method in ['bkash', 'nagad', 'rocket'] and not payment_number:
            raise forms.ValidationError("Payment number is required for mobile payments.")
        
        return cleaned_data

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