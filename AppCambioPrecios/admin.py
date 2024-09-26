from django.contrib import admin
from .models import *

@admin.register(Precio)
class PrecioAdmin(admin.ModelAdmin):
    search_fields=('idListaPrecio','idProducto','precio')
    list_filter=('idListaPrecio',)
    list_per_page=20
    list_display=('idListaPrecio','idProducto','precio')

