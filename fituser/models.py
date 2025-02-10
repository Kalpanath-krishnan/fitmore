from django.db import models
from django.contrib.auth.models import User  # Import Django's built-in User model
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Use CustomUser model

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=255, default="unknown")
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    RECOMMENDED_GOALS = [
        ("weight_gain", "Weight Gain (Strength Training)"),
        ("strength_training", "Strength Training"),
        ("weight_loss", "Weight Loss"),
        ("rehabilitation", "Rehabilitation / Special Training"),
        ("no_data", "No BMI Data Available"),
    ]
    recommended_goal = models.CharField(
        max_length=50, choices=RECOMMENDED_GOALS, default="no_data"
    )

    def calculate_bmi(self):
        """Calculate and store BMI based on height and weight."""
        if self.height and self.weight:
            try:
                height_m = float(self.height) / 100  # Convert cm to meters
                weight_kg = float(self.weight)  # Ensure weight is float
                bmi_value = round(weight_kg / (height_m ** 2), 2)  # Calculate BMI
                
                return bmi_value  # ✅ Return float value
            except ValueError:
                return None  # ✅ Return None if conversion fails
        return None

    def update_recommended_goal(self):
        """Determine recommended fitness goal based on BMI."""
        if self.bmi is not None:
            if self.bmi < 18.5:
                return "weight_gain"
            elif 18.5 <= self.bmi < 24.9:
                return "strength_training"
            elif 25 <= self.bmi < 29.9:
                return "weight_loss"
            else:
                return "rehabilitation"
        return "no_data"

    def save(self, *args, **kwargs):
        """Override save method to update BMI & Recommended Goal before saving."""
        self.bmi = self.calculate_bmi()  # ✅ Update BMI
        self.recommended_goal = self.update_recommended_goal()  # ✅ Update Goal
        super().save(*args, **kwargs)  # ✅ Save instance

    def __str__(self):
        return f"{self.username} - {self.recommended_goal}" # Save user instance

class WeightLossWorkout(models.Model):
    day = models.CharField(max_length=20)  # e.g., Monday
    activity = models.TextField()  # Exercise details

    def __str__(self):
        return f"{self.day} - {self.activity[:30]}"


class WeightGainWorkout(models.Model):
    day = models.CharField(max_length=20)
    activity = models.TextField()

    def __str__(self):
        return f"{self.day} - {self.activity[:30]}"

class StrengthTrainingWorkout(models.Model):
    day = models.CharField(max_length=20)
    activity = models.TextField()

    def __str__(self):
        return f"{self.day} - {self.activity[:30]}"


class RehabilitationWorkout(models.Model):
    day = models.CharField(max_length=20)
    activity = models.TextField()

    def __str__(self):
        return f"{self.day} - {self.activity[:30]}"


class UserWorkoutTracking(models.Model):
    STATUS_CHOICES = [('not_completed', 'Not Completed'), ('completed', 'Completed')]
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('strength_building', 'Strength Building'),
        ('rehabilitation', 'Rehabilitation'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES)
    workout_day = models.CharField(max_length=20)  # Changed from workout_id to workout_day
    workout = models.CharField(max_length=255,default="")  # Added column to store workout name/activity
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_completed')

    def __str__(self):
        return f"{self.user.username} - {self.goal} - Day {self.workout_day} - {self.workout} - {self.status}"
