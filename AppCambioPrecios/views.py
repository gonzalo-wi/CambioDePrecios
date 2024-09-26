from django.shortcuts import render


import pandas as pd
from .forms import UploadFileForm
from .models import Precio
from django.http import HttpResponse
from AppCambioPrecios.models import *
from AppCambioPrecios.forms import *
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Leer el archivo Excel
            file = request.FILES['file']
            df = pd.read_excel(file)

            # Iterar sobre las filas del DataFrame y guardar en la base de datos
            for index, row in df.iterrows():
                lista = Precio(
                    idListaPrecios=row['idListaPrecio'],  # Asegúrate que los nombres de las columnas coincidan
                    idProducto=row['idProducto'],
                    precio=row['precio']
                )
                lista.save()

            return render(request, 'form-list-success.html')  # Redirige a una página de éxito

    else:
        form = UploadFileForm()
    return render(request, 'form-list.html', {'form': form})

def base(request):
    return render(request, "AppCambioPrecios/base.html")