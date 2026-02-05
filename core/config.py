import os
from datetime import datetime

# --- RUTAS BASE ---
ruta_actual = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(ruta_actual)

# --- CARPETAS PRINCIPALES ---
DB_DIR = os.path.join(BASE_DIR, "db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# --- SUB-CARPETAS DE ORGANIZACIÓN ---
# 1. Donde se guardan los JSON de ventas de cada día
DIR_VENTAS_DIARIAS = os.path.join(DB_DIR, "ventas_diarias")

# 2. Donde se guardan los archivos generados (Salidas)
CARPETA_QR = os.path.join(ASSETS_DIR, "codigos_qr")
CARPETA_FACTURAS = os.path.join(ASSETS_DIR, "facturas")
CARPETA_REPORTES = os.path.join(ASSETS_DIR, "reportes")  # <--- NUEVA PARA CIERRES

# --- ARCHIVOS JSON FIJOS ---
ARCHIVO_DATOS = os.path.join(DB_DIR, "inventario.json")
ARCHIVO_CLIENTES = os.path.join(DB_DIR, "clientes.json")
ARCHIVO_USUARIOS = os.path.join(DB_DIR, "usuarios.json")
ARCHIVO_PENDIENTES = os.path.join(DB_DIR, "usuarios_pendientes.json")

# NOTA: ARCHIVO_VENTAS ya no es fijo, se calcula en datos.py según el día.

# --- DATOS SEMILLA ---
INVENTARIO_INICIAL = {
    "PAP-001": {
        "nombre": "Cuaderno 100h",
        "categoria": "Cuadernos",
        "precio": 1.50,
        "stock": 50,
    },
    "PAP-002": {
        "nombre": "Esfero Azul",
        "categoria": "Escritura",
        "precio": 0.60,
        "stock": 200,
    },
}
