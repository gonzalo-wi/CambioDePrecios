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
            for hoja in wb.sheetnames:
                sheet = wb[hoja]  # Obtiene la hoja por nombre

                # Iterar sobre las filas de la hoja, asumiendo que la primera fila tiene los encabezados
                for fila in sheet.iter_rows(min_row=2, values_only=True):  # Empezamos desde la segunda fila
                    idListaPrecio, idProducto, precio = fila

                    # Verificar que los datos sean válidos antes de crear el objeto
                    if idListaPrecio and idProducto and precio is not None:
                        # Crear un nuevo objeto Precio
                        Precio.objects.create(
                            nombreDeLista=hoja ,
                            idListaPrecio=idListaPrecio,  # Puede ser el ID de la lista (por ejemplo, del archivo Excel o un valor en tu DB)
                            idProducto=idProducto,
                            precio=precio,
                             # Aquí asignamos el nombre de la hoja como el atributo 'nombreDeLista'
                        )
            

            messages.success(request, "Archivo procesado correctamente y listas de precios actualizadas.")
            return redirect('subir_archivo')

        except Exception as e:
            messages.error(request, f"Error procesando el archivo: {e}")
            return redirect('subir_archivo')

    return render(request, 'AppCambioPrecios/subir_archivo.html')


