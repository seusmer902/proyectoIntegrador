# datos.py
import json
import os
import hashlib
import random
import string
from datetime import datetime

# Importamos las nuevas rutas
from .config import (
    ARCHIVO_DATOS,
    INVENTARIO_INICIAL,
    ARCHIVO_CLIENTES,
    ARCHIVO_USUARIOS,
    ARCHIVO_PENDIENTES,
    DIR_VENTAS_DIARIAS,  # <--- Importante
)

# Bases de datos en memoria
inventario_db = {}
ventas_db = []
clientes_db = {}
usuarios_db = {}
pendientes_db = {}
nombre_archivo_ventas_hoy = ""  # Variable para saber cuál es el json de hoy

# Roles y Permisos (Igual que antes)
PERMISOS_DISPONIBLES = {
    "VENTAS": "Acceso a Caja y Facturación",
    "STOCK": "Movimientos de Entrada/Salida",
    "PROD": "Crear, Editar y Borrar Productos",
    "CLIENTES": "Registrar y Ver Clientes",
    "REPORTES": "Ver Historial de Ventas y Dinero",
    "ADMIN": "Gestión Total (Usuarios y Config)",
    "COMPRA_SELF": "Permiso para comprar como cliente",
}

ROLES_PLANTILLA = {
    "Administrador": ["VENTAS", "STOCK", "PROD", "CLIENTES", "REPORTES", "ADMIN"],
    "Cajero": ["VENTAS", "CLIENTES"],
    "Bodeguero": ["STOCK", "PROD"],
    "Supervisor": ["VENTAS", "STOCK", "CLIENTES", "REPORTES"],
    "Cliente": ["COMPRA_SELF"],
}


def generar_codigo_recuperacion():
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(6))


def cargar_datos_sistema():
    global inventario_db, ventas_db, clientes_db, usuarios_db, pendientes_db, nombre_archivo_ventas_hoy

    # 1. Cargar Inventario
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                data = json.load(f)
                inventario_db.clear()
                inventario_db.update(data)
        except:
            inventario_db.clear()
    else:
        inventario_db.clear()
        inventario_db.update(INVENTARIO_INICIAL)
        guardar_inventario()

    # ==========================================================
    # 2. CARGAR VENTAS DEL DÍA (NUEVA LÓGICA)
    # ==========================================================
    # Crear carpeta de ventas diarias si no existe
    if not os.path.exists(DIR_VENTAS_DIARIAS):
        os.makedirs(DIR_VENTAS_DIARIAS)

    # Definimos el nombre del archivo según la fecha de HOY
    hoy_str = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo_ventas_hoy = os.path.join(
        DIR_VENTAS_DIARIAS, f"ventas_{hoy_str}.json"
    )

    if os.path.exists(nombre_archivo_ventas_hoy):
        try:
            with open(nombre_archivo_ventas_hoy, "r", encoding="utf-8") as f:
                data = json.load(f)
                ventas_db[:] = data
        except:
            ventas_db[:] = []
    else:
        # Si es un día nuevo, empezamos con lista vacía
        ventas_db[:] = []

    # 3. Cargar Clientes
    if os.path.exists(ARCHIVO_CLIENTES):
        try:
            with open(ARCHIVO_CLIENTES, "r", encoding="utf-8") as f:
                data = json.load(f)
                clientes_db.clear()
                clientes_db.update(data)
        except:
            clientes_db.clear()
    else:
        clientes_db.clear()

    # 4. Cargar Usuarios
    if os.path.exists(ARCHIVO_USUARIOS):
        try:
            with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
                data = json.load(f)
                usuarios_db.clear()
                usuarios_db.update(data)
                # Migración rápida
                cambios = False
                for u, val in usuarios_db.items():
                    if "bloqueado" not in val:
                        val["bloqueado"] = False
                        cambios = True
                    if "codigo_recuperacion" not in val:
                        val["codigo_recuperacion"] = "ADMIN1"
                        cambios = True
                if cambios:
                    guardar_usuarios()
        except:
            usuarios_db.clear()
    else:
        # Admin por defecto (123)
        pass_hash = hashlib.sha256("123".encode()).hexdigest()
        usuarios_db.clear()
        usuarios_db.update(
            {
                "admin": {
                    "pass_hash": pass_hash,
                    "rol": "Administrador",
                    "permisos": ROLES_PLANTILLA["Administrador"],
                    "bloqueado": False,
                    "codigo_recuperacion": "ADMIN1",
                }
            }
        )
        guardar_usuarios()

    # 5. Cargar Pendientes
    if os.path.exists(ARCHIVO_PENDIENTES):
        try:
            with open(ARCHIVO_PENDIENTES, "r", encoding="utf-8") as f:
                data = json.load(f)
                pendientes_db.clear()
                pendientes_db.update(data)
        except:
            pendientes_db.clear()
    else:
        pendientes_db.clear()


# --- FUNCIONES DE GUARDADO ---
def guardar_inventario():
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(inventario_db, f, indent=4)


def guardar_historial_ventas():
    # Guarda en el archivo específico del día de hoy
    global nombre_archivo_ventas_hoy
    if not nombre_archivo_ventas_hoy:  # Seguridad por si acaso
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo_ventas_hoy = os.path.join(
            DIR_VENTAS_DIARIAS, f"ventas_{hoy_str}.json"
        )

    with open(nombre_archivo_ventas_hoy, "w", encoding="utf-8") as f:
        json.dump(ventas_db, f, indent=4)


def guardar_clientes():
    with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(clientes_db, f, indent=4)


def guardar_usuarios():
    with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios_db, f, indent=4)


def guardar_pendientes():
    with open(ARCHIVO_PENDIENTES, "w", encoding="utf-8") as f:
        json.dump(pendientes_db, f, indent=4)


# --- ACCIONES ---
def resetear_password(usuario, nueva_pass):
    if usuario in usuarios_db:
        usuarios_db[usuario]["pass_hash"] = hashlib.sha256(
            nueva_pass.encode()
        ).hexdigest()
        guardar_usuarios()
        return True
    return False


def bloquear_usuario(usuario):
    if usuario in usuarios_db:
        usuarios_db[usuario]["bloqueado"] = True
        guardar_usuarios()
