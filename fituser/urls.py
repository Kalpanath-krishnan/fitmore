from django.urls import path
from .views import home ,userPage,registerPage,login_view,profile_view,logout,assign_workouts,tracking,workout_tracking_view,undo_tracking,find_nearby_gyms# Import the home view from your views module


urlpatterns = [
    path('', home, name='home'),  # Set the root URL to render the home page
    path('user/',userPage,name='user'),
    path('user/registerPage/',registerPage,name='signup'),
    path('user/login/',login_view,name='login'),
    path('profile/',profile_view,name='profile'),
    path('user/logout/',logout,name='logout'),
    path('assign-recommended-workouts/', assign_workouts, name='assign_recommended_workouts'),
    path('tracking/',tracking,name='tracking'),
    path('undotracking/',undo_tracking,name='undo'),
    path("workout-tracking/",workout_tracking_view, name="workout_tracking"),
    path('api/gyms/', find_nearby_gyms, name='find_nearby_gyms'),

    
]
