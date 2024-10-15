from django.db import models

# Create your models here.
class Precio(models.Model):
   nombreDeLista = models.CharField(max_length=255)
   idListaPrecio = models.CharField(max_length=30)
   idProducto= models.CharField(max_length=30)
   precio = models.IntegerField()

   def __str__(self):
      
      return f"Nombre de Lista: {self.nombreDeLista}  Codigo: {self.idListaPrecio} - codigo de Producto: {self.idProducto} - Precio: {self.precio}" 


