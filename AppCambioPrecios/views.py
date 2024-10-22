from django.shortcuts import render


import pandas as pd
import openpyxl
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from AppCambioPrecios.models import *
from AppCambioPrecios.forms import *
from AppCambioPrecios.urls import *
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .sincronizacion import *

@login_required
def inicio(request):
    return render(request, "AppCambioPrecios/inicio.html")
@login_required
def listas(request):
    precios = Precio.objects.all()
    mensaje = ""

    if request.method == 'POST':
       
        for key in request.POST.keys():
            if key.startswith('precio_'): 
                id_producto = key.split('_')[1]  
                nuevo_precio = request.POST[key].strip()  
                
                if nuevo_precio:
                    try:
                        nuevo_precio_float = float(nuevo_precio)  
                        if nuevo_precio_float < 0:
                            messages.error(request, f"El precio ingresado para el producto {id_producto} no puede ser negativo.")
                            continue  

                        precios = Precio.objects.filter(idProducto=id_producto)

                        for precio in precios:
                            
                            precio.precio = nuevo_precio_float
                            precio.save()
                 
                    except Precio.DoesNotExist:
                        messages.error(request, f"Producto {id_producto} no encontrado.")
                    except ValueError:
                        messages.error(request, f"El precio ingresado para el producto {id_producto} no es válido.")

        return redirect('listas')  

    
    precios_anteriores = {precio.idProducto: PrecioAntiguo.objects.filter(idProducto=precio.idProducto).order_by('-id').first() for precio in precios}

    return render(request, 'AppCambioPrecios/listas.html', {'precios': precios, 'precios_anteriores': precios_anteriores, 'mensaje': mensaje})

@login_required
def subir_archivo(request):
    if request.method == 'POST':
        archivo_excel = request.FILES['archivo_excel']
        try:
            wb = openpyxl.load_workbook(archivo_excel)
            for hoja in wb.sheetnames:
                sheet = wb[hoja]  

                for fila in sheet.iter_rows(min_row=2, values_only=True):  
                    idListaPrecio, idProducto, precio = fila

                    if idListaPrecio and idProducto and precio is not None:
                        
                        precio_obj, created = Precio.objects.get_or_create(
                            nombreDeLista=hoja,
                            idListaPrecio=idListaPrecio,
                            idProducto=idProducto,
                            defaults={'precio': precio}
                        )

                        if not created:
                            
                            precio_obj.precio = precio
                            precio_obj.save()
                        else:
                            
                            guardar_precio_anterior(precio_obj)

            
            conn = obtener_conexion()
            cursor = conn.cursor()
            guardar_precios_clientes(cursor)
            conn.commit()
            

            messages.success(request, "Archivo procesado correctamente y listas de precios actualizadas.")
            return redirect('subir_archivo')

        except Exception as e:
            messages.error(request, f"Error procesando el archivo: {e}")
            return redirect('subir_archivo')

    return render(request, 'AppCambioPrecios/subir_archivo.html')

@login_required
def sincronizar_precios_view(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'restaurar':
            resultado = restaurar_precios(request)  
        else:
            resultado = sincronizar_precios()  
        
        messages.success(request, resultado)  
        print(f"Mensaje: {resultado}") 
       
    return render(request, 'AppCambioPrecios/sincronizar_precios.html')
