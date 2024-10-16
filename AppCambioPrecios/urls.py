from django.urls import path
from . import views
from AppCambioPrecios.views import *
 

urlpatterns = [
    path('', inicio, name = "inicio"),
    path('listas/', listas, name = "listas"),
    path('subir-archivo/', views.subir_archivo, name='subir_archivo'),
    path('sincronizar-precios/', sincronizar_precios_view, name='sincronizar_precios'),
    

]