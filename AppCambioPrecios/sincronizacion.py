import time
import pyodbc
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db import transaction
from django.db import IntegrityError
from django.db import connection

def obtener_conexion():
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=192.168.0.234;"
        "DATABASE=H2O_JUMI;"
        "UID=h2o;"
        "PWD=Jumi1234;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def guardar_precio_anterior(precio):
    try:
        
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        
        cursor.execute("""
            SELECT idListaPrecio, idProducto, precio
            FROM Precios
            WHERE idListaPrecio = ?
        """, precio.idListaPrecio)
        
        
        for row in cursor.fetchall():
            try:
                PrecioAntiguo.objects.get(
                    idListaPrecio=row.idListaPrecio,
                    idProducto=row.idProducto
                )
            except PrecioAntiguo.DoesNotExist:
                PrecioAntiguo.objects.create(
                    idListaPrecio=row.idListaPrecio,
                    idProducto=row.idProducto,
                    precio_anterior=row.precio
                )
            except IntegrityError:
                print("Error al guardar el precio anterior.")
        
        
        cursor.close()
        conn.close()
        
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {e}")

def ejecutar_primer_script():
    script_sql = """
    DROP TABLE IF EXISTS tmp_descuentosXporcentaje;

    SELECT c.nrocta, p.idproducto, precio, preciolista = (SELECT dbo.Get_PrecioPorClienteProducto_sinprecioespecial(c.nrocta, p.idproducto, 0, 0)), 
           descuento = CONVERT(NUMERIC(18, 2), 0), atrib2, atrib3, atrib4, atrib5
    INTO tmp_descuentosXporcentaje
    FROM clientes c 
    INNER JOIN precios_clientes p ON p.nrocta = c.nrocta
    ORDER BY c.nrocta, p.idproducto;

    UPDATE tmp_descuentosXporcentaje 
    SET descuento = CONVERT(NUMERIC(18, 2), 100 - (precio * 100) / CASE preciolista WHEN 0 THEN 1 ELSE preciolista END);
    """

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Ejecutar cada comando individualmente
        for command in script_sql.split(';'):
            if command.strip():
                cursor.execute(command)
        
        conn.commit()
        print("Script SQL ejecutado correctamente.")
        
    except pyodbc.Error as e:
        print(f"Error al ejecutar el script SQL: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()     
def agregar_columna():
    script = """
    ALTER TABLE tmp_descuentosXporcentaje
    ADD precio_mod NUMERIC(18,2);
    """
    with connection.cursor() as cursor:
        cursor.execute(script)
def actualizar_precios():
    script = """
    UPDATE tmp_descuentosXporcentaje
    SET precio_mod = (
        SELECT dbo.Get_PrecioPorClienteProducto_sinprecioespecial(
            tmp_descuentosXporcentaje.nrocta,
            tmp_descuentosXporcentaje.idproducto,
            0, 0
        )
    );
    """
    with connection.cursor() as cursor:
        cursor.execute(script)      
def eliminar_precios_antiguos():
    script = """
    DELETE FROM Precios_Clientes
    WHERE nrocta IN (
        SELECT nrocta FROM tmp_descuentosXporcentaje
    );
    """
    with connection.cursor() as cursor:
        cursor.execute(script)
def insertar_nuevos_precios():
    script = """
    INSERT INTO Precios_Clientes (nrocta, idproducto, precio_descuento_esp)
    SELECT
        nrocta,
        idproducto,
        DBO.GET_ROUND_ESP(
            DBO.GET_ROUND_UP_5(
                ROUND(precio_mod - DBO.GET_ROUND_UP_5(
                    ROUND(precio_mod * (descuento / 100), 0)
                ), 0)
            )
        )
    FROM tmp_descuentosXporcentaje
    WHERE descuento > 0;
    """
    with connection.cursor() as cursor:
        cursor.execute(script)
        
def ejecutar_script_completo():
    try:
        agregar_columna()
        actualizar_precios()
        eliminar_precios_antiguos()
        insertar_nuevos_precios()
        print("Script ejecutado exitosamente.")
    except Exception as e:
        print(f"Error al ejecutar el script: {e}")     

def ejecutar_segundo_script():
    try:
        ejecutar_script_completo()
        mensaje = "Script SQL ejecutado correctamente."
        print(mensaje)
    except Exception as e:
        mensaje = f"Error al ejecutar el script SQL: {e}"
        print(mensaje)
    return mensaje           
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
def actualizar_precio(cursor, precio):
    query_update = """
        UPDATE dbo.Precios 
        SET Precio = ? 
        WHERE IdListaPrecio = ? AND IdProducto = ?
    """
    cursor.execute(query_update, precio.precio, precio.idListaPrecio, precio.idProducto)

def guardar_precios_clientes(cursor):
    try:
        
        cursor.execute("""
            IF OBJECT_ID('dbo.Backup_Precios_Clientes', 'U') IS NOT NULL
            DROP TABLE dbo.Backup_Precios_Clientes
        """)

        
        cursor.execute("""
            IF OBJECT_ID('dbo.Backup_Precios_Clientes', 'U') IS NULL
            CREATE TABLE dbo.Backup_Precios_Clientes (
                NroCta INT,
                IdProducto VARCHAR(50),
                Precio DECIMAL(18, 3)
            )
        """)

        
        cursor.execute("""
            INSERT INTO dbo.Backup_Precios_Clientes (NroCta, IdProducto, Precio)
            SELECT NroCta, IdProducto, Precio FROM dbo.Precios_Clientes
        """)

        
        cursor.execute("SELECT * FROM dbo.Backup_Precios_Clientes")
        for row in cursor.fetchall():
            print(row)

    except pyodbc.Error as e:
        print(f"Error al crear o insertar en la tabla Backup_Precios_Clientes: {e}")
        raise
    
def restaurar_precios_clientes(cursor):
    try:
       
        cursor.execute("""
            UPDATE dbo.Precios_Clientes
            SET Precio = b.Precio
            FROM dbo.Backup_Precios_Clientes b
            WHERE dbo.Precios_Clientes.NroCta = b.NroCta
            AND dbo.Precios_Clientes.IdProducto = b.IdProducto
        """)
    except pyodbc.Error as e:
        print(f"Error al restablecer los valores de la tabla Backup_Precios_Clientes: {e}")
        raise

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
    cursor_remoto = None
    conn_remota = None

    try:
        precios_antiguos = PrecioAntiguo.objects.all()
        print(f"Precios antiguos: {precios_antiguos}")

        conn_remota = obtener_conexion()
        cursor_remoto = conn_remota.cursor()

        for precio_antiguo in precios_antiguos:
            precio_antiguo.precio_anterior
            query_update = """
                UPDATE dbo.Precios 
                SET Precio = ? 
                WHERE IdListaPrecio = ? AND IdProducto = ?
            """
            cursor_remoto.execute(query_update, precio_antiguo.precio_anterior, precio_antiguo.idListaPrecio, precio_antiguo.idProducto)

        restaurar_precios_clientes(cursor_remoto)

        conn_remota.commit()
        mensaje = "Precios restaurados y sincronizados con la base de datos Aguas."

    except Exception as e:
        mensaje = f"Error al restaurar precios: {e}"
        print(mensaje)

    finally:
        if cursor_remoto is not None:
            cursor_remoto.close()
        if conn_remota is not None:
            conn_remota.close()

    return mensaje