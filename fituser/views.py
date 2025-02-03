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
    UserWorkoutTracking,
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
            login(request, user)  # Use 'auth_login' instead of 'login'
            

            request.session['user_id']=user.id
            request.session['username'] = user.username
            request.session['fullname'] = user.fullname
            request.session['height'] = str(user.height)  # Convert DecimalField to string
            request.session['weight'] = str(user.weight)
            request.session['profile_picture'] = user.profile_picture.url if user.profile_picture else None
            request.session['bmi']=str(user.bmi)

            # Redirect using reverse() to ensure the correct URL
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
    if recommended_goal == "Weight Gain (Strength Training)":
        workouts = WeightGainWorkout.objects.all()
    elif recommended_goal == "Strength Training":
        workouts = StrengthTrainingWorkout.objects.all()
    elif recommended_goal == "Weight Loss":
        workouts = WeightLossWorkout.objects.all()
    elif recommended_goal == "Rehabilitation / Special Training":
        workouts = RehabilitationWorkout.objects.all()

    # ✅ Store user data including recommended workouts
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'fullname': user.fullname,
        'height': user.height,
        'weight': user.weight,
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
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
@login_required
def assign_recommended_workouts(request):
    """Assign workouts based on the user's recommended goal."""
    user = request.user  # ✅ Get the logged-in user

    if not user.recommended_goal:
        return redirect("profile")  # ✅ Redirect if no goal is assigned

    # Fetch workouts from the correct category
    workout_model_map = {
        "weight_loss": "WeightLossWorkout",
        "weight_gain": "WeightGainWorkout",
        "strength_training": "StrengthTraingingWorkout",
        "rehabilitation": "RehabilitationWorkout",
    }

    workout_model_name = workout_model_map.get(user.recommended_goal, None)

    if not workout_model_name:
        return redirect("profile")  # ✅ No valid goal, return to profile

    # Import the correct workout model dynamically
    from fituser.models import WeightLossWorkout, WeightGainWorkout, StrengthTrainingWorkout, RehabilitationWorkout

    WorkoutModel = eval(workout_model_name)  # ✅ Convert string to model class

    # Fetch first 7 workouts for the user
    workouts = WorkoutModel.objects.all()[:7]

    if not workouts.exists():
        return render(request, "workout_plan.html", {"user": user, "workouts": [], "message": "No workouts available for this goal."})

    # Assign workouts to the user in UserWorkoutTracking
    for workout in workouts:
        UserWorkoutTracking.objects.get_or_create(
            user=user,
            goal=user.recommended_goal,
            workout_id=workout.id
        )

    return render(request, "workout_plan.html", {"user": user, "workouts": workouts})


    
#@login_required
# def select_workout(request):
#     if request.method == "POST":
#         user_goal = request.POST.get("goal", "weight_loss")  # Default to weight loss
#         request.session['user_goal'] = user_goal  # Store goal in session

#         # Redirect to workout plan page
#         return redirect('workout_plan')  # URL name for workout plan page

#     return redirect('profile')  # If accessed without POST, go back to profile

# @login_required
# def workout_plan(request):
#     user_goal = request.session.get('user_goal', 'weight_loss')  # Default to weight loss

#     # Load workout data from spreadsheet
#     file_path = "media/workouts.xlsx"  # Change this to your actual spreadsheet path
#     df = pd.read_excel(file_path, sheet_name=user_goal)  # Load the selected goal sheet

#     # Convert DataFrame to a list of dictionaries
#     workouts = df.to_dict(orient="records")

#     return render(request, "workout_plan.html", {"workouts": workouts, "goal": user_goal})
# class Goal(models.Model):
#     GOAL_CHOICES = [
#         ('weight_loss', 'Weight Loss'),
#         ('weight_gain', 'Weight Gain'),
#         ('strength_building', 'Strength Building'),
#         ('rehabilitation', 'Rehabilitation'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE)  # Track goal per user
#     goal_type = models.CharField(max_length=50, choices=GOAL_CHOICES)
#     target_workouts = models.IntegerField(default=10)  # Number of workouts to complete
#     completed_workouts = models.IntegerField(default=0)  # Track progress
#     status = models.CharField(max_length=20, default='In Progress')

#     def update_status(self):
#         if self.completed_workouts >= self.target_workouts:
#             self.status = 'Completed'
#         else:
#             self.status = 'In Progress'
#         self.save()

#     def __str__(self):
#         return f"{self.user.username} - {self.goal_type} ({self.status})"

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .models import Goal, Workout
# from django.contrib import messages

# @login_required
# def select_goal(request):
#     if request.method == "POST":
#         user_goal = request.POST.get("goal", "weight_loss")

#         # Check if user already has an active goal
#         goal, created = Goal.objects.get_or_create(user=request.user, goal_type=user_goal)

#         if not created:
#             messages.info(request, "You already have an active goal.")
#         else:
#             messages.success(request, "Your goal has been set!")

#         return redirect('profile')

#     return redirect('profile')

# @login_required
# def complete_workout(request):
#     if request.method == "POST":
#         goal = Goal.objects.filter(user=request.user).first()

#         if goal:
#             goal.completed_workouts += 1  # Increment completed workouts
#             goal.update_status()  # Update status
#             messages.success(request, "Workout marked as completed!")

#         return redirect('profile')

#     return redirect('profile')
def logout(request):
    auth.logout(request)
    return redirect('home')

        
    