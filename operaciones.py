import hashlib
import getpass
import sys
from datetime import datetime

import datos  # Para acceder a las variables globales
from datos import guardar_inventario, guardar_historial_ventas, cargar_datos_sistema
from utils import limpiar_pantalla, generar_qr
from datos import clientes_db, guardar_clientes
from config import usuarios_db


# ==========================================
# ADMINISTRACIÓN DE PRODUCTOS (CRUD)
# ==========================================
def registrar_producto():
    print("\n--- REGISTRO DE PRODUCTO ---")
    codigo = input("Código (ej: PAP-001): ").strip()
    if codigo in datos.inventario_db:
        print("⚠️ Error: Código ya existe.")
        return

    nombre = input("Nombre: ")
    categoria = input("Categoría: ")
    try:
        precio = float(input("Precio: "))
        stock = int(input("Stock inicial: "))
    except ValueError:
        print("⚠️ Error: Ingrese números válidos.")
        return

    datos.inventario_db[codigo] = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
    }
    guardar_inventario()

    # Generar QR
    datos_qr = f"ID:{codigo}\nProd:{nombre}\nPrecio:${precio:.2f}"
    generar_qr(codigo, datos_qr)
    print("✅ Producto registrado correctamente.")


def editar_producto():
    print("\n--- EDITAR PRODUCTO ---")
    codigo = input("Código a editar: ").strip()
    if codigo not in datos.inventario_db:
        print("⚠️ No existe.")
        return

    prod = datos.inventario_db[codigo]
    print(f">> Editando: {prod['nombre']} (Enter para mantener)")

    nuevo_nom = input(f"Nombre [{prod['nombre']}]: ")
    if nuevo_nom:
        prod["nombre"] = nuevo_nom

    nuevo_cat = input(f"Categoría [{prod['categoria']}]: ")
    if nuevo_cat:
        prod["categoria"] = nuevo_cat

    nuevo_pre = input(f"Precio [{prod['precio']}]: ")
    if nuevo_pre:
        prod["precio"] = float(nuevo_pre)

    guardar_inventario()
    print("✅ Actualizado correctamente.")


def eliminar_producto():
    codigo = input("\nCódigo a eliminar: ").strip()
    if codigo in datos.inventario_db:
        if input("¿Seguro? (SI/NO): ").upper() == "SI":
            del datos.inventario_db[codigo]
            guardar_inventario()
            print("🗑️ Producto eliminado.")
    else:
        print("⚠️ No existe.")


def regenerar_qr_manualmente():
    print("\n--- REGENERAR QRS ---")
    op = input("1. Uno solo\n2. Todos\nOpción: ")

    if op == "1":
        codigo = input("Código: ").strip()
        if codigo in datos.inventario_db:
            p = datos.inventario_db[codigo]
            info = f"ID:{codigo}\nProd:{p['nombre']}\nPrecio:${p['precio']:.2f}"
            generar_qr(codigo, info)
    elif op == "2":
        if input("¿Seguro? (SI/NO): ").upper() == "SI":
            count = 0
            for cod, p in datos.inventario_db.items():
                info = f"ID:{cod}\nProd:{p['nombre']}\nPrecio:${p['precio']:.2f}"
                generar_qr(cod, info)
                count += 1
            print(f"✅ {count} QRs regenerados.")


# ==========================================
# OPERACIONES (VENTAS Y MOVIMIENTOS)
# ==========================================
def registrar_movimiento():
    print("\n--- MOVIMIENTOS DE STOCK ---")
    codigo = input("Código del producto: ").strip()
    if codigo not in datos.inventario_db:
        print("⚠️ No existe.")
        return

    tipo = input("Tipo (E=Entrada / S=Salida): ").upper()
    try:
        cant = int(input("Cantidad: "))
    except ValueError:
        return

    stock_actual = datos.inventario_db[codigo]["stock"]

    if tipo == "E":
        datos.inventario_db[codigo]["stock"] += cant
        print(f"✅ Nuevo stock: {datos.inventario_db[codigo]['stock']}")
        guardar_inventario()
    elif tipo == "S":
        if cant <= stock_actual:
            datos.inventario_db[codigo]["stock"] -= cant
            print(f"✅ Nuevo stock: {datos.inventario_db[codigo]['stock']}")
            guardar_inventario()
        else:
            print("⚠️ Stock insuficiente.")
    else:
        print("⚠️ Tipo inválido.")


def registrar_venta():
    print("\n--- 🛒 NUEVA VENTA (CARRITO) ---")
    carrito = []
    total_venta = 0.0

    while True:
        print(f"\n>> Items: {len(carrito)} | Total Parcial: ${total_venta:.2f}")
        codigo = input("Código (o 'F' para finalizar): ").strip()

        if codigo.upper() == "F":
            break

        if codigo not in datos.inventario_db:
            print("❌ Producto no encontrado.")
            continue

        prod = datos.inventario_db[codigo]
        print(
            f"   Seleccionado: {prod['nombre']} | Precio: ${prod['precio']:.2f} | Stock: {prod['stock']}"
        )

        try:
            cant = int(input("   Cantidad: "))
            if cant <= 0:
                print("   ⚠️ Cantidad inválida.")
                continue

            if cant <= prod["stock"]:
                subtotal = cant * prod["precio"]

                item = {
                    "codigo": codigo,
                    "nombre": prod["nombre"],
                    "cantidad": cant,
                    "precio": prod["precio"],
                    "subtotal": subtotal,
                }
                carrito.append(item)
                total_venta += subtotal

                # Resta virtual temporal
                prod["stock"] -= cant
                print(f"   ✅ Agregado al carrito.")
            else:
                print(f"   ❌ Stock insuficiente (Max: {prod['stock']}).")

        except ValueError:
            print("   ⚠️ Error al ingresar cantidad.")

    # --- FINALIZAR ---
    if not carrito:
        print("\n🚫 Venta cancelada o carrito vacío.")
        cargar_datos_sistema()  # Revertir restas virtuales
        return

    print("\n" + "=" * 40)
    print("           TICKET DE VENTA")
    print("=" * 40)
    print(f"{'PROD':<15} {'CANT':<5} {'PRECIO':<10} {'SUBTOTAL'}")
    print("-" * 40)
    for i in carrito:
        print(
            f"{i['nombre']:<15} {i['cantidad']:<5} ${i['precio']:<9.2f} ${i['subtotal']:.2f}"
        )
    print("-" * 40)
    print(f"TOTAL A PAGAR:      ${total_venta:.2f}")
    print("=" * 40)

    if input("\n¿Confirmar venta? (S/N): ").upper() == "S":
        # 1. Guardar cambios en inventario
        guardar_inventario()

        # 2. Registrar en historial
        nueva_venta = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total_venta,
            "items": carrito,
        }
        datos.ventas_db.append(nueva_venta)
        guardar_historial_ventas()

        print("✅ ¡Venta registrada exitosamente!")
    else:
        print("⚠️ Venta cancelada.")
        cargar_datos_sistema()  # Revertir cambios


# ==========================================
# REPORTES Y CONSULTAS
# ==========================================
def registrar_cliente_interactivo():
    print("\n--- 📝 REGISTRO DE NUEVO CLIENTE ---")
    cedula = input("Cédula o RUC: ").strip()
    if cedula in datos.clientes_db:
        print("⚠️ Este cliente ya existe.")
        return

    nombre = input("Nombre completo: ")
    telefono = input("Teléfono: ")
    correo = input("Correo electrónico: ")

    datos.clientes_db[cedula] = {
        "nombre": nombre,
        "telefono": telefono,
        "correo": correo,
        "puntos": 0,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d"),
    }
    datos.guardar_clientes()
    print(f"✅ ¡{nombre} ha sido registrado!")


def listar_clientes():
    print("\n" + "=" * 60)
    print(f"{'CÉDULA/RUC':<15} | {'NOMBRE':<25} | {'TELÉFONO'}")
    print("-" * 60)
    if not datos.clientes_db:
        print("   No hay clientes registrados.")
    else:
        for ced, info in datos.clientes_db.items():
            print(f"{ced:<15} | {info['nombre']:<25} | {info.get('telefono', 'N/A')}")
    print("=" * 60)


def consultar_inventario():
    print("\n" + "=" * 60)
    print(f"{'CÓDIGO':<10} | {'NOMBRE':<30} | {'PRECIO':<8} | {'STOCK'}")
    print("-" * 60)
    for cod, datos_prod in datos.inventario_db.items():
        print(
            f"{cod:<10} | {datos_prod['nombre']:<30} | ${datos_prod['precio']:<7.2f} | {datos_prod['stock']}"
        )
    print("=" * 60)


def consultar_historial_ventas():
    print("\n--- HISTORIAL DE VENTAS ---")
    if not datos.ventas_db:
        print("No hay registros.")
        return

    total_acumulado = 0.0
    print(f"{'FECHA':<20} {'ITEMS':<10} {'TOTAL'}")
    print("-" * 45)
    for v in datos.ventas_db:
        cant_items = sum(item["cantidad"] for item in v["items"])
        print(f"{v['fecha']:<20} {cant_items:<10} ${v['total']:.2f}")
        total_acumulado += v["total"]
    print("-" * 45)
    print(f"💰 INGRESOS TOTALES: ${total_acumulado:.2f}")


def login():
    print(f"\n--- 🔒 ACCESO SEGURO HADES V-1.6.1 ---")
    intentos = 3
    while intentos > 0:
        user = input("Usuario: ")
        pwd_input = getpass.getpass("Contraseña: ")

        if user in usuarios_db:
            hash_calculado = hashlib.sha256(pwd_input.encode()).hexdigest()
            if hash_calculado == usuarios_db[user]["pass_hash"]:
                return usuarios_db[user]["rol"]

        print(f"⛔ Credenciales incorrectas.")
        intentos -= 1
    sys.exit()
