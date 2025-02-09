from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.db import models
from fituser.models import CustomUser
import pandas as pd
from fituser.models import (
    WeightLossWorkout,
    WeightGainWorkout,
    StrengthTrainingWorkout,
    RehabilitationWorkout,
    
)




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
     user=request.user
     goal=user.recommended_goal


     name=user.username   
     workout_day=request.POST['workout_day']
     workout_activity=request.POST['workout_activity']
     print(user,goal,workout_day,workout_activity)

     



       

def logout(request):
     auth.logout(request)
     return redirect('home')

     
     










        
    