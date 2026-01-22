import json
import os
from config import (
    ARCHIVO_DATOS,
    ARCHIVO_VENTAS,
    INVENTARIO_INICIAL,
    ARCHIVO_CLIENTES,
    ARCHIVO_USUARIOS,
)

# Variables Globales
inventario_db = {}
ventas_db = []
clientes_db = {}
usuarios_db = {}  # <--- NUEVA VARIABLE GLOBAL


def cargar_datos_sistema():
    global inventario_db, ventas_db, clientes_db, usuarios_db

    # 1. Cargar Inventario
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                inventario_db = json.load(f)
        except:
            inventario_db = {}
    else:
        inventario_db = INVENTARIO_INICIAL.copy()
        guardar_inventario()

    # 2. Cargar Ventas
    if os.path.exists(ARCHIVO_VENTAS):
        try:
            with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as f:
                ventas_db = json.load(f)
        except:
            ventas_db = []
    else:
        ventas_db = []

    # 3. Cargar Clientes
    if os.path.exists(ARCHIVO_CLIENTES):
        try:
            with open(ARCHIVO_CLIENTES, "r", encoding="utf-8") as f:
                clientes_db = json.load(f)
        except:
            clientes_db = {}
    else:
        clientes_db = {}

    # 4. Cargar USUARIOS (¡NUEVO!)
    if os.path.exists(ARCHIVO_USUARIOS):
        try:
            with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
                usuarios_db = json.load(f)
        except:
            usuarios_db = {}
    else:
        # Si no existe, creamos el Admin por defecto para no bloquearnos
        # Hash de "123": a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
        print(">> Creando sistema de usuarios por primera vez...")
        usuarios_db = {
            "admin": {
                "pass_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
                "rol": "Administrador",
            }
        }
        guardar_usuarios()


def guardar_inventario():
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(inventario_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error inv: {e}")


def guardar_historial_ventas():
    try:
        with open(ARCHIVO_VENTAS, "w", encoding="utf-8") as f:
            json.dump(ventas_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error ventas: {e}")


def guardar_clientes():
    try:
        with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
            json.dump(clientes_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error clientes: {e}")


def guardar_usuarios():  # <--- NUEVA FUNCIÓN
    try:
        with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error usuarios: {e}")
