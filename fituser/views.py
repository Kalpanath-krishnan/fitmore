from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required


def home(request):
    return render(request,'home.html')

# Create your views here.
def userPage(request):
    return render(request,'login.html')

def registerPage(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        password = request.POST.get('password1')

        # Create a new user
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # Success message (optional)
            messages.success(request, "Account created successfully!")

            # Correctly redirect to the 'user' route
            return redirect('/')  # 'user' must match the URL name in urls.py
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'signup.html')

    # Render the registration form for GET requests
    return render(request, 'signup.html')

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user is not None:
         auth.login(request,user)
         
         return redirect('profile')
         
        else:
            error_message='invalid'
    return render(request,'user/',{'error_message':error_message})
def profile_view(request):
    return render(request,'profile.html')
def logout(request):
    auth.logout(request)
    return redirect('home')