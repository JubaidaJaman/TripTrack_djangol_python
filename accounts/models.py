# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('tourist', 'Tourist'),
        ('organizer', 'Tour Organizer'),
        ('developer', 'Developer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='tourist')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"

    def save(self, *args, **kwargs):
        if self.is_superuser and self.user_type != 'developer':
            self.user_type = 'developer'
        super().save(*args, **kwargs)


class TouristProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    semester = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Tourist: {self.user.username}"


class OrganizerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=200, default="CSE Department")
    organizer_id = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Organizer: {self.department}"


class EmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = (
        ('parent', 'Parent'),
        ('guardian', 'Guardian'),
        ('sibling', 'Sibling'),
        ('spouse', 'Spouse'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'tourist'})
    full_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'phone']

    def __str__(self):
        return f"{self.full_name} ({self.relationship}) - {self.user.username}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary contacts for this user
        if self.is_primary:
            EmergencyContact.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'tourist':
            TouristProfile.objects.create(user=instance)
        elif instance.user_type == 'organizer':
            OrganizerProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    try:
        if instance.user_type == 'tourist' and hasattr(instance, 'touristprofile'):
            instance.touristprofile.save()
        elif instance.user_type == 'organizer' and hasattr(instance, 'organizerprofile'):
            instance.organizerprofile.save()
    except Exception:
        pass