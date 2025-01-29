from django.urls import path
from .views import home ,userPage,registerPage,login,profile_view,logout# Import the home view from your views module


urlpatterns = [
    path('', home, name='home'),  # Set the root URL to render the home page
    path('user/',userPage,name='user'),
    path('user/registerPage/',registerPage,name='signup'),
    path('user/login/',login,name='login'),
    path('profile/',profile_view,name='profile'),
    path('user/logout/',logout,name='logout'),
    
]
