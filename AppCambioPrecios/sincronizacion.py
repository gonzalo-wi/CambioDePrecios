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
        "SERVER=192.168.0.5;"
        "DATABASE=H2O_JUMI;"
        "UID=cafe;"
        "PWD=JumiCAFE3241;"
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
        
        
        for command in script_sql.split(';'):
            if command.strip():
                cursor.execute(command)
        
        conn.commit()
        print("Script SQL ejecutado correctamente.")
        
    except pyodbc.Error as e:
        print(f"Error al ejecutar el script SQL: {e}")
        
      


def ejecutar_segundo_script():
    script_sql = """
    alter table tmp_descuentosXporcentaje
    add precio_mod numeric(18,2);

    update tmp_descuentosXporcentaje 
    set precio_mod = (select dbo.Get_PrecioPorClienteProducto_sinprecioespecial(tmp_descuentosXporcentaje.nrocta, tmp_descuentosXporcentaje.idproducto, 0, 0));

    delete from Precios_Clientes 
    where nrocta in (select nrocta from tmp_descuentosXporcentaje);

    insert into Precios_Clientes
    select nrocta, idproducto,
        precio_descuento_esp = DBO.GET_ROUND_ESP(
            DBO.GET_ROUND_UP_5(
                round(precio_mod - DBO.GET_ROUND_UP_5(round(precio_mod * (descuento / 100), 0)), 0)
            )
        )
    from tmp_descuentosXporcentaje
    where descuento > 0;
    """
    
    try:
        conn = obtener_conexion()
        if conn:
            cursor = conn.cursor()
            
            # Dividir el script en sentencias individuales
            commands = [cmd.strip() for cmd in script_sql.split(';') if cmd.strip()]
            
            for command in commands:
                cursor.execute(command)  # Ejecutar cada sentencia SQL
                conn.commit()  # Confirmar cambios después de cada sentencia
                print(f"Ejecutado: {command[:50]}...")  # Imprime un resumen de la sentencia ejecutada
                time.sleep(3)  # Pausa de 3 segundos (puedes ajustar este tiempo)

            cursor.close()
            conn.close()
            print("Segundo script ejecutado exitosamente.")
        else:
            print("No se pudo establecer la conexión a la base de datos.")
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
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