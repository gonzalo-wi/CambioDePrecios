from django.db import models

# Create your models here.
class Precio(models.Model):
   nombreDeLista = models.CharField(max_length=255)
   idListaPrecio = models.CharField(max_length=30)
   idProducto= models.CharField(max_length=30)
   precio = models.IntegerField()

   def __str__(self):
      
      return f"Nombre de Lista: {self.nombreDeLista}  Codigo: {self.idListaPrecio} - codigo de Producto: {self.idProducto} - Precio: {self.precio}" 


class PrecioAntiguo(models.Model):
    idListaPrecio = models.CharField(max_length=30)
    idProducto = models.CharField(max_length=30)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=3)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    

class PrecioCliente(models.Model):
   nroCta = models.IntegerField()
   idProducto = models.CharField(max_length=30)
   precio = models.DecimalField(max_digits=10, decimal_places=3)