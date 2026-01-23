import hashlib
import getpass
import os
from datetime import datetime

# IMPORTS CORREGIDOS DESDE CORE
from core.datos import (
    guardar_inventario,
    guardar_historial_ventas,
    guardar_usuarios,
    usuarios_db,
    inventario_db,
    ventas_db,
    clientes_db,
    PERMISOS_DISPONIBLES,
    ROLES_PLANTILLA,
)
from core.utils import limpiar_pantalla, generar_qr
from core.config import CARPETA_FACTURAS
import cli.menus as menus


# --- AUTENTICACIÓN ---
def login():
    intentos = 0
    while intentos < 3:
        limpiar_pantalla()
        print("🔐 INICIO DE SESIÓN - HADES")
        print("(Si olvidaste tu clave, escribe: RECUPERAR)")

        user = input("Usuario: ")

        # --- BLOQUE DE RECUPERACIÓN ---
        if user.upper() == "RECUPERAR":
            from core.config import CLAVE_MAESTRA

            key = getpass.getpass("🔑 Ingrese Llave Maestra: ")

            if key == CLAVE_MAESTRA:
                print("\n--- RESTABLECER CONTRASEÑA ---")
                u_reset = input("Usuario a recuperar: ")
                if u_reset in usuarios_db:
                    new_p = input("Nueva Contraseña: ")
                    # Llamamos a la función que creamos en datos.py
                    from core.datos import resetear_password

                    resetear_password(u_reset, new_p)
                    print("✅ Contraseña actualizada. Intenta entrar ahora.")
                    input("Enter para continuar...")
                    continue  # Vuelve al inicio del while
                else:
                    print("❌ Usuario no existe.")
            else:
                print("⛔ Llave incorrecta.")
            input("Enter para continuar...")
            continue
        # ------------------------------

        pwd = getpass.getpass("Contraseña: ")

        if user in usuarios_db:
            hash_input = hashlib.sha256(pwd.encode()).hexdigest()
            if hash_input == usuarios_db[user]["pass_hash"]:
                return user

        print("❌ Credenciales incorrectas.")
        intentos += 1
        input("Enter para reintentar...")

    print("⛔ Demasiados intentos fallidos.")
    exit()


def tiene_permiso(usuario, permiso_requerido):
    if usuario in usuarios_db:
        if permiso_requerido in usuarios_db[usuario]["permisos"]:
            return True
    return False


# --- GESTIÓN DE PRODUCTOS ---
def registrar_producto():
    print("\n--- NUEVO PRODUCTO ---")
    cod = input("Código: ").strip().upper()
    if cod in inventario_db:
        print("❌ Ya existe ese código.")
        return

    nom = input("Nombre: ")
    cat = input("Categoría: ")
    try:
        pre = float(input("Precio: "))
        stk = int(input("Stock Inicial: "))
    except:
        print("Error: Ingrese números válidos.")
        return

    inventario_db[cod] = {"nombre": nom, "categoria": cat, "precio": pre, "stock": stk}
    guardar_inventario()
    print("✅ Producto guardado.")


def consultar_inventario():
    limpiar_pantalla()
    print(f"{'COD':<10} {'NOMBRE':<25} {'PRECIO':<10} {'STOCK'}")
    print("-" * 55)
    for c, d in inventario_db.items():
        print(f"{c:<10} {d['nombre']:<25} ${d['precio']:<9.2f} {d['stock']}")
    input("\nEnter para volver...")


# --- GESTIÓN USUARIOS (Resumen) ---
def registrar_nuevo_usuario():
    u = input("Nuevo Usuario: ")
    if u in usuarios_db:
        print("Ya existe.")
        return
    p = input("Contraseña: ")
    rol = input("Rol (Administrador/Cajero/Bodeguero): ")
    if rol not in ROLES_PLANTILLA:
        print("Rol no válido. Se asignará Cajero.")
        rol = "Cajero"

    ph = hashlib.sha256(p.encode()).hexdigest()
    usuarios_db[u] = {"pass_hash": ph, "rol": rol, "permisos": ROLES_PLANTILLA[rol]}
    guardar_usuarios()
    print("Usuario creado.")


def listar_usuarios():
    for u, d in usuarios_db.items():
        print(f"- {u} ({d['rol']})")


# --- PLACEHOLDERS PARA QUE NO FALLE ---
def editar_producto():
    print("Función CLI editar pendiente.")
    input()


def eliminar_producto():
    print("Función CLI eliminar pendiente.")
    input()


def regenerar_qr_manualmente():
    print("Generando QRs...")
    input()


def registrar_movimiento():
    print("Movimientos CLI pendiente.")
    input()


def registrar_venta():
    print("Caja CLI pendiente. Use GUI.")
    input()


def consultar_historial_ventas():
    print("Historial...")
    input()


def realizar_cierre_caja():
    print("Cierre...")
    input()


def eliminar_usuario(actual):
    print("Eliminar usuario...")
    input()


def modificar_permisos_usuario(actual):
    print("Permisos...")
    input()


def editar_datos_usuario(actual):
    print("Editar usuario...")
    input()
