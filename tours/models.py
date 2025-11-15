# tours/models.py - COMPLETE VERSION
from django.db import models
from django.contrib.auth import get_user_model
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
import uuid

User = get_user_model()

class UAPDepartment(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='departments/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Tour(models.Model):
    CATEGORY_CHOICES = (
        ('campus', 'Campus Tour'),
        ('department', 'Department Visit'),
        ('cultural', 'Cultural Event'),
        ('educational', 'Educational Trip'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='campus')
    department = models.ForeignKey(UAPDepartment, on_delete=models.CASCADE, null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'organizer'})
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_hours = models.IntegerField()
    max_participants = models.IntegerField()
    meeting_point = models.CharField(max_length=300)
    tour_date = models.DateTimeField()
    includes = models.TextField(blank=True, help_text="What's included in the tour")
    requirements = models.TextField(blank=True, help_text="What participants should bring")
    itinerary = models.TextField(blank=True, help_text="Detailed schedule")
    image = models.ImageField(upload_to='tours/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def available_spots(self):
        confirmed_bookings = self.booking_set.filter(status='confirmed').aggregate(
            total_participants=models.Sum('participants')
        )['total_participants'] or 0
        return self.max_participants - confirmed_bookings
    
    @property
    def is_upcoming(self):
        return self.tour_date > timezone.now()
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Generate URL for this tour
        tour_url = f"http://localhost:8000/tours/{self.id}/"  # Update with your domain
        qr.add_data(tour_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        filename = f'qr_code_{self.id}_{uuid.uuid4().hex[:8]}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        return filename

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
    )
    
    tourist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'tourist'})
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    participants = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requirements = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_number = models.CharField(max_length=20, blank=True, help_text="bKash/Nagad/Rocket number")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.tourist.username} - {self.tour.title}"

class Review(models.Model):
    RATING_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )
    
    tourist = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tour', 'tourist']
    
    def __str__(self):
        return f"{self.tourist.username} - {self.tour.title} - {self.rating} stars"

class Wishlist(models.Model):
    tourist = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tourist', 'tour']
    
    def __str__(self):
        return f"{self.tourist.username} - {self.tour.title}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Payment for {self.booking}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('reminder', 'Tour Reminder'),
        ('announcement', 'Announcement'),
        ('update', 'Tour Update'),
        ('cancellation', 'Cancellation'),
        ('promotion', 'Promotion'),
    )
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'organizer'})
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='announcement')
    send_to_all_tourists = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type}: {self.title}"
    
    def get_target_users(self):
        """Get all users who should receive this notification"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if self.send_to_all_tourists:
            return User.objects.filter(user_type='tourist')
        elif self.tour:
            # Send to tourists who booked this specific tour
            return User.objects.filter(
                booking__tour=self.tour,
                booking__status='confirmed',
                user_type='tourist'
            ).distinct()
        else:
            return User.objects.filter(user_type='tourist')

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'notification']
    
    def __str__(self):
        return f"{self.user.username} - {self.notification.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()