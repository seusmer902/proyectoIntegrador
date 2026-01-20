import json
import os
from config import ARCHIVO_DATOS, ARCHIVO_VENTAS, INVENTARIO_INICIAL, ARCHIVO_CLIENTES

# Variables Globales de Datos
clientes_db = {}
inventario_db = {}
ventas_db = []


def cargar_datos_sistema():
    """Carga tanto el inventario como el historial de ventas al iniciar."""
    global inventario_db, ventas_db

    # 1. Cargar Inventario
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                inventario_db = json.load(f)
        except Exception:
            inventario_db = {}
    else:
        print(">> Primera ejecución. Cargando datos semilla...")
        inventario_db = INVENTARIO_INICIAL.copy()
        guardar_inventario()

    # 2. Cargar Ventas
    if os.path.exists(ARCHIVO_VENTAS):
        try:
            with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as f:
                ventas_db = json.load(f)
        except Exception:
            ventas_db = []
    else:
        ventas_db = []

    if os.path.exists(ARCHIVO_CLIENTES):
        try:
            with open(ARCHIVO_CLIENTES, "r", encoding="utf-8") as f:
                clientes_db = json.load(f)
        except Exception:
            clientes_db = {}
    else:
        clientes_db = {}


def guardar_inventario():
    """Guarda los cambios del inventario en el JSON."""
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(inventario_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar inventario: {e}")


def guardar_historial_ventas():
    """Guarda el historial de ventas en el JSON."""
    try:
        with open(ARCHIVO_VENTAS, "w", encoding="utf-8") as f:
            json.dump(ventas_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar ventas: {e}")


def guardar_clientes():
    try:
        with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
            json.dump(clientes_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar clientes: {e}")
