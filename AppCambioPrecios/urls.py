from django.urls import path
from AppCambioPrecios.views import *

urlpatterns = [
    
    path('base/', base, name="base"),
]