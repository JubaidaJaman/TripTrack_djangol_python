import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

User = settings.AUTH_USER_MODEL

class Tour(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_tours')
    title = models.CharField(max_length=250)
    description = models.TextField()
    location = models.CharField(max_length=250)
    date = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=20)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='tour_images/', blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)

    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # generate QR code with URL to tour detail
        super().save(*args, **kwargs)
        if not self.qr_image:
            tour_url = f"/tours/{self.id}/qr-detail/"  # local url; adjust to full domain if needed
            qr = qrcode.make(tour_url)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            filename = f"{self.id}.png"
            self.qr_image.save(filename, ContentFile(buffer.getvalue()), save=False)
            buffer.close()
            super().save(*args, **kwargs)

    def spots_left(self):
        booked = Booking.objects.filter(tour=self, status='CONFIRMED').count()
        return max(0, self.capacity - booked)

    def is_past(self):
        return self.date < timezone.now()

class Booking(models.Model):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [(PENDING,'Pending'), (CONFIRMED,'Confirmed'), (CANCELLED,'Cancelled')]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_status = models.BooleanField(default=False)
    check_in = models.BooleanField(default=False)

class Wishlist(models.Model):
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
