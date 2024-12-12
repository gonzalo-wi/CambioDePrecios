import pyodbc

"""conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=192.168.0.234;"
    "Database=H2O_JUMI;"
    "UID=h2o;"
    "PWD=Jumi1234;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("Conexión exitosa!")
except Exception as e:
    print(f"Error de conexión: {e}")
"""

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=192.168.0.234;"
    "Database=H2O_JUMI;"
    "UID=h2o;"
    "PWD=Jumi1234;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("Conexión exitosa!")
except Exception as e:
    print(f"Error de conexión: {e}")