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


def inicio(request):
    return render(request, "AppCambioPrecios/inicio.html")

def listas(request):
    precios = Precio.objects.all()
    return render(request, "AppCambioPrecios/listas.html",{"precios":precios})


def subir_archivo(request):
    if request.method == 'POST':
        archivo_excel = request.FILES['archivo_excel']
        try:
            # Cargar el archivo Excel
            wb = openpyxl.load_workbook(archivo_excel)
            hoja = wb.active  # Asume que los datos están en la primera hoja del archivo
            
            # Iterar sobre las filas del archivo Excel (asumiendo que la primera fila tiene encabezados)
            for fila in hoja.iter_rows(min_row=2, values_only=True):
                idListaPrecio, idProducto, precio = fila

                # Crear un nuevo objeto de ListaPrecio
                Precio.objects.create(
                    idListaPrecio=idListaPrecio,
                    idProducto=idProducto,
                    precio=precio
                )

            messages.success(request, "Archivo procesado correctamente y listas de precios actualizadas.")
            return redirect('AppCambioPrecios/subir_archivo.html')

        except Exception as e:
            messages.error(request, f"Error procesando el archivo: {e}")
            return redirect('AppCambioPrecios/subir_archivo.html')

    return render(request, 'AppCambioPrecios/subir_archivo.html')


