# core/datos.py (V-1.7.3 CORREGIDO)
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
    ARCHIVO_EMPLEADOS,
    ARCHIVO_CLIENTES_LOGIN,
    ARCHIVO_USUARIOS_LEGACY,
    ARCHIVO_PENDIENTES,
    DIR_VENTAS_DIARIAS,
)

# Bases de datos en memoria
inventario_db = {}
ventas_db = []
clientes_db = {}
pendientes_db = {}
nombre_archivo_ventas_hoy = ""

# --- DOBLE ALMACÉN ---
empleados_db = {}  # Solo Staff
clientes_login_db = {}  # Solo Clientes con cuenta
usuarios_db = {}  # Fusión en RAM (Staff + Clientes) para el Login

# Roles y Permisos
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
    global inventario_db, ventas_db, clientes_db, usuarios_db, pendientes_db
    global empleados_db, clientes_login_db, nombre_archivo_ventas_hoy

    # 1. INVENTARIO
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                inventario_db.clear()
                inventario_db.update(json.load(f))
        except:
            inventario_db.clear()
    else:
        inventario_db.clear()
        inventario_db.update(INVENTARIO_INICIAL)
        guardar_inventario()

    # 2. VENTAS DEL DÍA
    if not os.path.exists(DIR_VENTAS_DIARIAS):
        os.makedirs(DIR_VENTAS_DIARIAS)
    hoy_str = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo_ventas_hoy = os.path.join(
        DIR_VENTAS_DIARIAS, f"ventas_{hoy_str}.json"
    )

    if os.path.exists(nombre_archivo_ventas_hoy):
        try:
            with open(nombre_archivo_ventas_hoy, "r", encoding="utf-8") as f:
                ventas_db[:] = json.load(f)
        except:
            ventas_db[:] = []
    else:
        ventas_db[:] = []

    # 3. CLIENTES (Datos Facturación)
    if os.path.exists(ARCHIVO_CLIENTES):
        try:
            with open(ARCHIVO_CLIENTES, "r", encoding="utf-8") as f:
                clientes_db.clear()
                clientes_db.update(json.load(f))
        except:
            clientes_db.clear()
    else:
        clientes_db.clear()

    # ==========================================================
    # 4. SISTEMA DE USUARIOS (MIGRACIÓN Y CARGA DOBLE)
    # ==========================================================
    empleados_db.clear()
    clientes_login_db.clear()

    # A) MIGRACIÓN LEGACY
    if os.path.exists(ARCHIVO_USUARIOS_LEGACY):
        print("⚠️  MIGRANDO SISTEMA DE USUARIOS A V-1.7.3...")
        try:
            with open(ARCHIVO_USUARIOS_LEGACY, "r", encoding="utf-8") as f:
                legacy_data = json.load(f)

            for u, data in legacy_data.items():
                if data.get("rol") == "Cliente":
                    clientes_login_db[u] = data
                else:
                    empleados_db[u] = data

            guardar_empleados()
            guardar_clientes_login()
            os.rename(ARCHIVO_USUARIOS_LEGACY, ARCHIVO_USUARIOS_LEGACY + ".bak")
            print("✅ Migración completada.")
        except Exception as e:
            print(f"❌ Error migrando: {e}")

    # B) Cargar Empleados
    if os.path.exists(ARCHIVO_EMPLEADOS):
        try:
            with open(ARCHIVO_EMPLEADOS, "r", encoding="utf-8") as f:
                empleados_db.update(json.load(f))
        except:
            pass
    else:
        if not empleados_db and not os.path.exists(ARCHIVO_USUARIOS_LEGACY + ".bak"):
            pass_hash = hashlib.sha256("123".encode()).hexdigest()
            empleados_db["admin"] = {
                "pass_hash": pass_hash,
                "rol": "Administrador",
                "permisos": ROLES_PLANTILLA["Administrador"],
                "bloqueado": False,
                "codigo_recuperacion": "ADMIN1",
            }
            guardar_empleados()

    # C) Cargar Clientes Login
    if os.path.exists(ARCHIVO_CLIENTES_LOGIN):
        try:
            with open(ARCHIVO_CLIENTES_LOGIN, "r", encoding="utf-8") as f:
                clientes_login_db.update(json.load(f))
        except:
            pass

    # D) FUSIÓN EN RAM
    usuarios_db.clear()
    usuarios_db.update(empleados_db)
    usuarios_db.update(clientes_login_db)

    # 5. PENDIENTES
    if os.path.exists(ARCHIVO_PENDIENTES):
        try:
            with open(ARCHIVO_PENDIENTES, "r", encoding="utf-8") as f:
                pendientes_db.clear()
                pendientes_db.update(json.load(f))
        except:
            pendientes_db.clear()
    else:
        pendientes_db.clear()


# --- FUNCIONES DE GUARDADO ---
def guardar_inventario():
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(inventario_db, f, indent=4)


def guardar_historial_ventas():
    if nombre_archivo_ventas_hoy:
        with open(nombre_archivo_ventas_hoy, "w", encoding="utf-8") as f:
            json.dump(ventas_db, f, indent=4)


def guardar_clientes():
    with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(clientes_db, f, indent=4)


def guardar_empleados():
    with open(ARCHIVO_EMPLEADOS, "w", encoding="utf-8") as f:
        json.dump(empleados_db, f, indent=4)


def guardar_clientes_login():
    with open(ARCHIVO_CLIENTES_LOGIN, "w", encoding="utf-8") as f:
        json.dump(clientes_login_db, f, indent=4)


def guardar_pendientes():
    with open(ARCHIVO_PENDIENTES, "w", encoding="utf-8") as f:
        json.dump(pendientes_db, f, indent=4)


# ========================================================
# 🔧 PUENTE DE COMPATIBILIDAD (¡ESTO ARREGLA EL ERROR!)
# ========================================================
def guardar_usuarios():
    """
    Esta función existe para que 'operaciones.py' no falle.
    Guarda TODO (Empleados y Clientes) para asegurar que los cambios se reflejen.
    """
    guardar_empleados()
    guardar_clientes_login()


# --- ACCIONES ---
def resetear_password(usuario, nueva_pass):
    h = hashlib.sha256(nueva_pass.encode()).hexdigest()
    if usuario in empleados_db:
        empleados_db[usuario]["pass_hash"] = h
        guardar_empleados()
        return True
    elif usuario in clientes_login_db:
        clientes_login_db[usuario]["pass_hash"] = h
        guardar_clientes_login()
        return True
    return False


def bloquear_usuario(usuario):
    if usuario in empleados_db:
        empleados_db[usuario]["bloqueado"] = True
        guardar_empleados()
    elif usuario in clientes_login_db:
        clientes_login_db[usuario]["bloqueado"] = True
        guardar_clientes_login()
    if usuario in usuarios_db:
        usuarios_db[usuario]["bloqueado"] = True


def rehabilitar_usuario(usuario):
    if usuario in empleados_db:
        empleados_db[usuario]["bloqueado"] = False
        guardar_empleados()
        return True
    elif usuario in clientes_login_db:
        clientes_login_db[usuario]["bloqueado"] = False
        guardar_clientes_login()
        return True
    return False
