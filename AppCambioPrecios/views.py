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
from .sincronizacion import sincronizar_precios

@login_required
def inicio(request):
    return render(request, "AppCambioPrecios/inicio.html")
@login_required
def listas(request):
    precios = Precio.objects.all()
    return render(request, "AppCambioPrecios/listas.html",{"precios":precios})

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
                        
                        Precio.objects.create(
                            nombreDeLista=hoja ,
                            idListaPrecio=idListaPrecio,  
                            idProducto=idProducto,
                            precio=precio,
                             
                        )
            

            messages.success(request, "Archivo procesado correctamente y listas de precios actualizadas.")
            return redirect('subir_archivo')

        except Exception as e:
            messages.error(request, f"Error procesando el archivo: {e}")
            return redirect('subir_archivo')

    return render(request, 'AppCambioPrecios/subir_archivo.html')


@login_required
def sincronizar_precios_view(request):
    if request.method == 'POST':
        resultado = sincronizar_precios()
        messages.success(request, resultado)  
        print(f"Mensaje: {resultado}") 
       
    return render(request, 'AppCambioPrecios/sincronizar_precios.html')
