from django.db import models
from django.contrib.auth.models import User  # Import Django's built-in User model

class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-One relationship
    fullname = models.CharField(max_length=100, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # In cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # In kg
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username  # Return the username associated with this profile
