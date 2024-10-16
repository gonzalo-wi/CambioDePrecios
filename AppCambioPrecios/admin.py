from django.contrib import admin
from .models import *

@admin.register(Precio)
class PrecioAdmin(admin.ModelAdmin):
    search_fields=('idListaPrecio','idProducto','precio')
    list_filter=('idListaPrecio',)
    list_per_page=20
    list_display=('idListaPrecio','idProducto','precio')

@admin.register(PrecioAntiguo)
class PrecioAntiguoAdmin(admin.ModelAdmin):
    search_fields=('idListaPrecio','idProducto','precio_anterior')
    list_filter=('idListaPrecio',)
    list_per_page=20
    list_display=('idListaPrecio','idProducto','precio_anterior')

@admin.register(PrecioCliente)
class PrecioClienteAdmin(admin.ModelAdmin):
    search_fields=('nroCta','idProducto','precio')
    list_filter=('precio',)
    list_per_page=20
    list_display=('nroCta','idProducto','precio')