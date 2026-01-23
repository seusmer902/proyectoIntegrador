import json
import os
import hashlib

# Importamos desde config dentro de core
from .config import (
    ARCHIVO_DATOS,
    ARCHIVO_VENTAS,
    INVENTARIO_INICIAL,
    ARCHIVO_CLIENTES,
    ARCHIVO_USUARIOS,
)

# --- BASES DE DATOS EN MEMORIA ---
# Es vital que sean MUTABLES y no se reasignen con =
inventario_db = {}
ventas_db = []
clientes_db = {}
usuarios_db = {}

# --- ROLES Y PERMISOS ---
PERMISOS_DISPONIBLES = {
    "VENTAS": "Acceso a Caja y Facturación",
    "STOCK": "Movimientos de Entrada/Salida",
    "PROD": "Crear, Editar y Borrar Productos",
    "CLIENTES": "Registrar y Ver Clientes",
    "REPORTES": "Ver Historial de Ventas y Dinero",
    "ADMIN": "Gestión Total (Usuarios y Config)",
}

ROLES_PLANTILLA = {
    "Administrador": ["VENTAS", "STOCK", "PROD", "CLIENTES", "REPORTES", "ADMIN"],
    "Cajero": ["VENTAS", "CLIENTES"],
    "Bodeguero": ["STOCK", "PROD"],
    "Supervisor": ["VENTAS", "STOCK", "CLIENTES", "REPORTES"],
}


def cargar_datos_sistema():
    # Usamos global para asegurarnos de ver las variables,
    # pero las modificaremos IN-PLACE (sin usar el signo =)
    global inventario_db, ventas_db, clientes_db, usuarios_db

    # 1. Cargar Inventario
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                data = json.load(f)
                inventario_db.clear()  # Borramos lo viejo
                inventario_db.update(data)  # Ponemos lo nuevo
        except:
            inventario_db.clear()
    else:
        inventario_db.clear()
        inventario_db.update(INVENTARIO_INICIAL)
        guardar_inventario()

    # 2. Cargar Ventas (Lista)
    if os.path.exists(ARCHIVO_VENTAS):
        try:
            with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as f:
                data = json.load(f)
                ventas_db[:] = (
                    data  # [:] Truco para actualizar listas sin romper referencias
                )
        except:
            ventas_db[:] = []
    else:
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
        except:
            usuarios_db.clear()
    else:
        # Admin por defecto si falla todo
        pass_admin = hashlib.sha256("admin123".encode()).hexdigest()
        usuarios_db.clear()
        usuarios_db.update(
            {
                "admin": {
                    "pass_hash": pass_admin,
                    "rol": "Administrador",
                    "permisos": ROLES_PLANTILLA["Administrador"],
                }
            }
        )
        guardar_usuarios()

    print("✅ Datos cargados correctamente en memoria compartida.")


# --- FUNCIONES DE GUARDADO ---
def guardar_inventario():
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(inventario_db, f, indent=4)


def guardar_historial_ventas():
    with open(ARCHIVO_VENTAS, "w", encoding="utf-8") as f:
        json.dump(ventas_db, f, indent=4)


def guardar_clientes():
    with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(clientes_db, f, indent=4)


def guardar_usuarios():
    with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios_db, f, indent=4)


def resetear_password(usuario, nueva_pass):
    if usuario in usuarios_db:
        usuarios_db[usuario]["pass_hash"] = hashlib.sha256(
            nueva_pass.encode()
        ).hexdigest()
        guardar_usuarios()
        return True
    return False
