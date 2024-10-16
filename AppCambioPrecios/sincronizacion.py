import pyodbc
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db import transaction

def obtener_conexion():
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=192.168.0.5;"
        "DATABASE=H2O_JUMI_29_12_23;"
        "UID=Cafe;"
        "PWD=JumiCAFE3241;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def guardar_precio_anterior(precio):
    PrecioAntiguo.objects.create(
        idListaPrecio=precio.idListaPrecio,
        idProducto=precio.idProducto,
        precio_anterior=precio.precio
    )

def actualizar_precio(cursor, precio):
    query_update = """
        UPDATE dbo.Precios 
        SET Precio = ? 
        WHERE IdListaPrecio = ? AND IdProducto = ?
    """
    cursor.execute(query_update, precio.precio, precio.idListaPrecio, precio.idProducto)

def guardar_precios_clientes(cursor):
    query_select = "SELECT NroCta, IdProducto, Precio FROM dbo.Precios_Clientes"
    cursor.execute(query_select)
    
    for row in cursor.fetchall():
        NroCta, IdProducto, Precio = row
        
        PrecioCliente.objects.create(
            nroCta=NroCta,
            idProducto=IdProducto,
            precio=Precio
        )

def sincronizar_precios():
    mensaje = ""
    cursor = None  
    conn = None 
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        precios_locales = Precio.objects.all()
        
        for precio in precios_locales:
            guardar_precio_anterior(precio)
            actualizar_precio(cursor, precio)

        
        guardar_precios_clientes(cursor)

        conn.commit()
        mensaje = "Sincronización exitosa."
    
    except pyodbc.Error as e:
        mensaje = f"No se puede sincronizar: {e}"
    
    except ObjectDoesNotExist:
        mensaje = "Error: No se encontraron precios locales."
    
    except Exception as e:
        mensaje = f"Tiempo agotado o error inesperado: {e}"
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    
    return mensaje

def restaurar_precios(request):
    mensaje = ""

    try:
        precios_antiguos = PrecioAntiguo.objects.all()

        if not precios_antiguos.exists():
            return JsonResponse({'mensaje': "No hay precios antiguos para restaurar."})

        with obtener_conexion() as conn_remota:
            cursor_remoto = conn_remota.cursor()
            with transaction.atomic():
                # Actualizar precios locales
                for precio_antiguo in precios_antiguos:
                    Precio.objects.filter(
                        idListaPrecio=precio_antiguo.idListaPrecio,
                        idProducto=precio_antiguo.idProducto
                    ).update(precio=precio_antiguo.precio_anterior)

                    # Actualizar precios en la base de datos remota
                    query_update = """
                        UPDATE dbo.Precios 
                        SET Precio = ? 
                        WHERE IdListaPrecio = ? AND IdProducto = ?
                    """
                    cursor_remoto.execute(query_update, (precio_antiguo.precio_anterior, precio_antiguo.idListaPrecio, precio_antiguo.idProducto))

                # Actualizar precios de clientes
                precios_clientes_antiguos = PrecioCliente.objects.all()
                for precio_cliente_antiguo in precios_clientes_antiguos:
                    query_update_cliente = """
                        UPDATE dbo.Precios_Clientes 
                        SET Precio = ? 
                        WHERE NroCta = ? AND IdProducto = ?
                    """
                    cursor_remoto.execute(query_update_cliente, (precio_cliente_antiguo.precio, precio_cliente_antiguo.nroCta, precio_cliente_antiguo.idProducto))

            conn_remota.commit()
            mensaje = "Precios restaurados y sincronizados con la base de datos remota."

    except Exception as e:
        mensaje = f"Error al restaurar precios: {e}"

    return JsonResponse({'mensaje': mensaje})