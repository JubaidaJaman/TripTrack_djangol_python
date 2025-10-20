from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    TOURIST = 'TOURIST'
    ORGANIZER = 'ORGANIZER'
    DEVELOPER = 'DEVELOPER'
    ROLE_CHOICES = [
        (TOURIST, 'Tourist'),
        (ORGANIZER, 'Tour Organizer'),
        (DEVELOPER, 'Developer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=TOURIST)
    # extra profile fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def is_tourist(self):
        return self.role == self.TOURIST

    def is_organizer(self):
        return self.role == self.ORGANIZER

    def is_developer(self):
        return self.role == self.DEVELOPER
