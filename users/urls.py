from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from users.views import *




urlpatterns = [
   path('login/',login_request, name='Login'),
   path('logout/', auth_views.LogoutView.as_view(next_page='Login'), name='logout'),
]