import pyodbc
from .models import Precio

def sincronizar_precios():
    
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=192.168.0.5;"
        "DATABASE=H2O_JUMI_29_12_23;"
        "UID=Cafe;"
        "PWD=JumiCAFE3241;"
        "TrustServerCertificate=yes;"
    )
    
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
    cursor.close()
    conn.close()