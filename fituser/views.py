from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.db import models
from fituser.models import CustomUser
from fituser.models import UserWorkoutTracking
import pandas as pd
from fituser.models import (
    WeightLossWorkout,
    WeightGainWorkout,
    StrengthTrainingWorkout,
    RehabilitationWorkout,
    
)

import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend
from collections import defaultdict
import datetime


from collections import Counter
from django.http import JsonResponse
from django.conf import settings
import requests




from django.contrib.auth.decorators import login_required


def home(request):
    return render(request,'home.html')

# Create your views here.
def userPage(request):
    return render(request,'login.html')

def registerPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        fullname = request.POST.get('fullname', '')
        height = request.POST.get('height', None)
        weight = request.POST.get('weight', None)
        profile_picture = request.FILES.get('profile_picture', None)


        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('signup')
        height = float(height) if height and height.strip() else None
        weight = float(weight) if weight and weight.strip() else None

        bmi = None
        if height and weight:
            bmi = round(float(weight) / (float(height / 100) ** 2), 2)  # ✅ BMI formula


        # Create and save user
        user = CustomUser.objects.create_user(
            username=username, 
            password=password,
            fullname=fullname, 
            height=height, 
            weight=weight,
            bmi= bmi,

            profile_picture=profile_picture,
        )
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect('home')

    return render(request, 'signup.html')

    

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:  # Ensure a valid user object is returned
            login(request, user)  # Log in the user

            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['fullname'] = user.fullname
            request.session['height'] = str(user.height)  # Convert to string
            request.session['weight'] = str(user.weight)  # Convert to string
            request.session['bmi'] = str(user.bmi)  # Convert to string

            # ✅ Store profile picture URL instead of the object
            request.session['profile_picture'] = (
                user.profile_picture.url if user.profile_picture else None
            )

            # Redirect to the profile page
            return redirect('profile')  
        else:
            messages.error(request, "Invalid username or password")
            return redirect(reverse('login'))  # Stay on login page

    return render(request, 'login.html')


@login_required
def profile_view(request):
    user = request.user  # ✅ Get logged-in user

    # ✅ Ensure BMI is updated before getting the goal
    if user.bmi is None:
        user.bmi = user.calculate_bmi()
        user.save(update_fields=['bmi'])  # ✅ Save BMI if not already calculated

    recommended_goal = user.recommended_goal  # ✅ Get recommended goal

    # ✅ Fetch workouts based on the recommended goal
    workouts = []
    if recommended_goal == "weight_gain ":
        workouts = WeightGainWorkout.objects.all()
    elif recommended_goal == "strength_training":
        workouts = StrengthTrainingWorkout.objects.all()
    elif recommended_goal == "weight_loss":
        workouts = WeightLossWorkout.objects.all()
    elif recommended_goal == "rehabilitation":
        workouts = RehabilitationWorkout.objects.all()

    # ✅ Store user data including recommended workouts
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'fullname': user.fullname,
        'height': user.height,
        'weight': user.weight,
        'profile_picture': user.profile_picture if user.profile_picture else None,
        'bmi': user.bmi if user.bmi else "Not Available",
        'recommended_goal': user.recommended_goal,  # ✅ Ensure goal is calculated
        'workouts': workouts,  # ✅ Pass recommended workouts
    }

    return render(request, 'profile.html', {'user_data': user_data})

    """Update user profile with height, weight & recommend workouts."""
    if request.method == 'POST':
        user = request.user
        user.fullname = request.POST.get('fullname', user.fullname)
        user.height = float(request.POST.get('height', user.height or 0))
        user.weight = float(request.POST.get('weight', user.weight or 0))

        user.calculate_bmi()
        recommended_goal = user.get_recommended_goal()
        request.session['recommended_goal'] = recommended_goal

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'profile.html', {"recommended_goal": request.session.get('recommended_goal', None)})

@login_required
def assign_workouts(request):
    user=request.user
    workouts = None
    if user.recommended_goal == "weight_loss":
            workouts = WeightLossWorkout.objects.all()
    elif user.recommended_goal == "weight_gain":
            workouts = WeightGainWorkout.objects.all()
    elif user.recommended_goal == "strength_training":
            workouts = StrengthTrainingWorkout.objects.all()
    elif user.recommended_goal == "rehabilitation":
            workouts = RehabilitationWorkout.objects.all()
    else:
        messages.error(request, "No recommended goal found. Please update your profile.")
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'fullname': user.fullname,
        'height': user.height,
        'weight': user.weight,
        'profile_picture': user.profile_picture if user.profile_picture else None,
        'bmi': user.bmi if user.bmi else "Not Available",
        'recommended_goal': user.recommended_goal,  # ✅ Ensure goal is calculated
        'workouts': workouts,  # ✅ Pass recommended workouts
    }
    return render(request,"workout_plan.html",{'user_data':user_data,'workouts':workouts})
@login_required
def tracking(request):
    if request.method == "POST":
        user = request.user
        goal = user.recommended_goal

        workout_day = request.POST.get('workout_day')
        workout_activity = request.POST.get('workout_activity')

        # Save tracking details using workout_day
        tracking_entry = UserWorkoutTracking.objects.create(
            user=user,
            goal=goal,
            workout_day=workout_day,
            workout=workout_activity,  # Now using workout_day instead of workout_id
            status='completed',
        )

        print(f"Saved: {tracking_entry}")

        return redirect('assign_recommended_workouts')

    return redirect('profile')

@login_required
def undo_tracking(request):
    if request.method == "POST":
        user = request.user
        workout_day = request.POST.get('workout_day')
        workout_activity = request.POST.get('workout_activity')

        # Find and delete the latest matching workout entry
        tracking_entry = UserWorkoutTracking.objects.filter(
            user=user, workout_day=workout_day, workout=workout_activity
        ).last()  # Get the latest entry

        if tracking_entry:
            tracking_entry.delete()  # Delete the entry
            print(f"Deleted tracking entry for: {user.username} - {workout_day} - {workout_activity}")

        return redirect('assign_recommended_workouts')

    return redirect('profile')

@login_required
def workout_tracking_view(request):
    user = request.user
    user_data = {
            'user_id': user.id,
            'username': user.username,
            'fullname': user.fullname,
            'height': user.height,
            'weight': user.weight,
            'profile_picture': user.profile_picture if user.profile_picture else None,
            'bmi': user.bmi if user.bmi else "Not Available",
            'recommended_goal': user.recommended_goal,  # ✅ Ensure goal is calculated
  # ✅ Pass recommended workouts
        }
    tracking_data = UserWorkoutTracking.objects.filter(user=user)

    # Organize workouts into weeks (Monday to Sunday)
    weekly_progress = defaultdict(lambda: {"completed": 0, "total": 7})  # Each week is 7 days

    for entry in tracking_data:
        try:
            # Convert workout_day (e.g., "Monday") to a date
            today = datetime.date.today()
            days_map = {
                "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
                "Friday": 4, "Saturday": 5, "Sunday": 6
            }
            workout_day_index = days_map.get(entry.workout_day, -1)

            if workout_day_index == -1:
                continue  # Skip invalid days

            # Get the start of the week (Monday)
            week_start = today - datetime.timedelta(days=today.weekday())
            workout_date = week_start + datetime.timedelta(days=workout_day_index)
            week_label = workout_date.strftime("%Y-%m-%d")  # Store weeks as "YYYY-MM-DD"

            if entry.status == "completed":
                weekly_progress[week_label]["completed"] += 1  # Count completed days

        except ValueError:
            continue  # Skip invalid date conversions

    # Ensure correct total for weeks
    completed_counts = sum(week["completed"] for week in weekly_progress.values())
    total_counts = sum(week["total"] for week in weekly_progress.values())

    # Avoid division by zero
    completion_percentage = (completed_counts / total_counts) * 100 if total_counts else 0

    # Generate the doughnut chart
    plt.figure(figsize=(8, 8))
    plt.pie(
        [completion_percentage, 100 - completion_percentage],
        labels=["Completed Workouts", "Pending Workouts"],
        autopct="%1.1f%%",
        colors=["#34D399", "#FACC15"],
        wedgeprops={"linewidth": 2, "edgecolor": "white"}
    )
    plt.title("Overall Workout Completion")

    # Draw a white circle at the center to make it a doughnut chart
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    # Save the chart to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return render(request, "tracking.html", {"tracking_data": tracking_data, "chart_image": chart_image, "user_data":user_data})
def gym_locator(request):
    return render(request,'gym_locator.html')
def logout(request):
     auth.logout(request)
     return redirect('home')

GOOGLE_PLACES_API_KEY = "AIzaSyARGnV45YeOAdOZ_yH61flYVyL8jw1FwiI"

def find_nearby_gyms(request):
   return render(request,'gym_locator.html')