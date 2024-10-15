import pyodbc
from .models import Precio
from django.core.exceptions import ObjectDoesNotExist

def sincronizar_precios():
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=192.168.0.5;"
        "DATABASE=H2O_JUMI_29_12_23;"
        "UID=Cafe;"
        "PWD=JumiCAFE3241;"
        "TrustServerCertificate=yes;"
    )
    
    cursor = None
    conn = None
    mensaje = ""

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        precios_locales = Precio.objects.all()
        
        for precio in precios_locales:
            query = """
                UPDATE dbo.Precios 
                SET Precio = ? 
                WHERE IdListaPrecio = ? AND IdProducto = ?
            """
            cursor.execute(query, precio.precio, precio.idListaPrecio, precio.idProducto)
        
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