from django.conf import settings
from django.db import models

class Tour(models.Model):
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # links to the User model
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    tour_date = models.DateField()
    payment_deadline = models.DateField()
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
