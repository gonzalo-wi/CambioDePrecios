
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .view import saludo
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("AppCambioPrecios.urls")),
    path("users/", include("users.urls")),
   
   
    
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)