from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('developer', 'Developer'),
        ('organizer', 'Organizer'),
        ('tourist', 'Tourist'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tourist')
    phone = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    organization_name = models.CharField(max_length=200, blank=True, null=True)
    organization_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
