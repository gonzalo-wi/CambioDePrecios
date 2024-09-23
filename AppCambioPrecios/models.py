from django.db import models

# Create your models here.
class precio(models.Model):
   idListaPrecio = models.CharField(max_length=30)
   idProducto= models.CharField(max_length=30)
   precio = models.ImageField()

   def __str__(self):
      
      return f"Lista de Precio: {self.idListaPrecio} - codigo de Producto: {self.idProducto} - Precio: {precio}" 
