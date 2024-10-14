import pyodbc

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=192.168.0.5;"
    "Database=H2O_JUMI_29_12_23;"
    "UID=Cafe;"
    "PWD=JumiCAFE3241;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("Conexión exitosa!")
except Exception as e:
    print(f"Error de conexión: {e}")
