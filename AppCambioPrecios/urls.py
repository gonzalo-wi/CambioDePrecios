from django.urls import path
from . import views
from AppCambioPrecios.views import *
 

urlpatterns = [
    path('', inicio, name = "inicio"),
    path('listas/', listas, name = "listas"),
    path('subir-archivo/', views.subir_archivo, name='subir_archivo'),
    path('sincronizar-precios/', sincronizar_precios_view, name='sincronizar_precios'),
    path('restaurar_precios/', restaurar_precios_view, name='restaurar_precios'),
    path('ejecutar-primer-script/', ejecutar_primer_script_view, name='ejecutar_primer_script'),
    path('ejecutar-segundo-script/', ejecutar_segundo_script_view, name='ejecutar_segundo_script'),
    path('buscar_listas_precios/', buscar_listas_precios, name='buscar_listas_precios'),
   
]