from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UAPDepartment(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='departments/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Tour(models.Model):
    TOUR_STATUS = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    TOUR_CATEGORIES = (
        ('campus', 'Campus Tour'),
        ('department', 'Department Visit'),
        ('cultural', 'Cultural Event'),
        ('educational', 'Educational Trip'),
        ('adventure', 'Adventure Tour'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=TOUR_CATEGORIES, default='campus')
    department = models.ForeignKey(UAPDepartment, on_delete=models.CASCADE, null=True, blank=True)  # Add null=True temporarily
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'organizer'})
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_hours = models.IntegerField()
    max_participants = models.IntegerField()
    meeting_point = models.CharField(max_length=300)
    tour_date = models.DateTimeField()
    includes = models.TextField(help_text="What's included in the tour", blank=True)
    requirements = models.TextField(help_text="What participants should bring", blank=True)
    itinerary = models.TextField(help_text="Detailed schedule", blank=True)
    image = models.ImageField(upload_to='tours/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=TOUR_STATUS, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def available_spots(self):
        booked = self.booking_set.filter(status='confirmed').count()
        return self.max_participants - booked
    
    def is_upcoming(self):
        from django.utils import timezone
        return self.tour_date > timezone.now()
    
    def save(self, *args, **kwargs):
        # Auto-assign organizer's department if not set
        if not self.department and self.organizer.user_type == 'organizer':
            from accounts.models import OrganizerProfile
            try:
                organizer_profile = OrganizerProfile.objects.get(user=self.organizer)
                # Find or create department based on organizer's department
                department, created = UAPDepartment.objects.get_or_create(
                    name=organizer_profile.department,
                    defaults={
                        'code': organizer_profile.department.split()[0],
                        'description': f'{organizer_profile.department} at UAP'
                    }
                )
                self.department = department
            except OrganizerProfile.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class Booking(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    tourist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'tourist'})
    booking_date = models.DateTimeField(auto_now_add=True)
    participants = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requirements = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.tourist.username}"

class Review(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    tourist = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.tourist.username}"

class Wishlist(models.Model):
    tourist = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tourist', 'tour']
    
    def __str__(self):
        return f"{self.tourist.username} - {self.tour.title}"

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=Booking.PAYMENT_STATUS, default='pending')
    
    def __str__(self):
        return f"Payment #{self.transaction_id}"