import hashlib
import getpass
import sys
import os  # Importante para las carpetas
from datetime import datetime

import datos  # Acceso a variables globales
from datos import (
    guardar_inventario,
    guardar_historial_ventas,
    cargar_datos_sistema,
    guardar_clientes,
)
from utils import limpiar_pantalla, generar_qr
from config import usuarios_db, CARPETA_FACTURAS


# ==========================================
# ADMINISTRACIÓN DE PRODUCTOS
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
    print("\n--- 🛒 NUEVA VENTA (CAJA V-1.6.2) ---")
    carrito = []
    total_venta = 0.0

    while True:
        print(f"\n>> Items: {len(carrito)} | Total Parcial: ${total_venta:.2f}")
        codigo = input("Código (o 'F' para pagar): ").strip()

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
                prod["stock"] -= cant  # Resta virtual
                print(f"   ✅ Agregado.")
            else:
                print(f"   ❌ Stock insuficiente.")
        except ValueError:
            print("   ⚠️ Error de cantidad.")

    if not carrito:
        print("\n🚫 Carrito vacío.")
        cargar_datos_sistema()
        return

    # 2. ASIGNACIÓN DE CLIENTE
    print("\n--- 👤 DATOS DE FACTURACIÓN ---")
    print("1. Consumidor Final")
    print("2. Cliente Ya Registrado (Buscar por Cédula)")
    print("3. Registrar Nuevo Cliente Ahora Mismo")

    op_cliente = input("Seleccione opción (1-3): ").strip()

    cliente_data = None
    cedula_cliente = "CONSUMIDOR_FINAL"
    nombre_cliente = "Consumidor Final"

    if op_cliente == "2":
        ced = input("Ingrese Cédula/RUC: ").strip()
        if ced in datos.clientes_db:
            cliente_data = datos.clientes_db[ced]
            nombre_cliente = cliente_data["nombre"]
            cedula_cliente = ced
            print(
                f"✅ Cliente detectado: {nombre_cliente} (Nivel: {cliente_data.get('nivel', 'Bronce')})"
            )
        else:
            print("⚠️ Cliente no encontrado. Se usará Consumidor Final.")

    elif op_cliente == "3":
        registrar_cliente_interactivo()
        # Recuperamos el último cliente registrado
        if datos.clientes_db:
            ced_nueva = list(datos.clientes_db.keys())[-1]
            cliente_data = datos.clientes_db[ced_nueva]
            nombre_cliente = cliente_data["nombre"]
            cedula_cliente = ced_nueva
            print(f"✅ Nuevo cliente asignado a la factura: {nombre_cliente}")

    # 3. CONFIRMACIÓN Y PUNTOS
    print("\n" + "=" * 40)
    print(f"TOTAL A PAGAR:      ${total_venta:.2f}")
    print("=" * 40)

    if input("\n¿Confirmar pago y generar factura? (S/N): ").upper() == "S":
        guardar_inventario()

        puntos_ganados = 0
        if cliente_data:
            puntos_ganados = int(total_venta)
            cliente_data["puntos"] += puntos_ganados
            # Subir Nivel
            if cliente_data["puntos"] > 500:
                cliente_data["nivel"] = "Oro"
            elif cliente_data["puntos"] > 100:
                cliente_data["nivel"] = "Plata"
            guardar_clientes()
            print(f"🎁 ¡El cliente ganó {puntos_ganados} Puntos Hades!")
            print(f"🌟 Nuevo Nivel: {cliente_data['nivel']}")

        generar_archivo_factura(
            carrito, total_venta, nombre_cliente, cedula_cliente, puntos_ganados
        )

        nueva_venta = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total_venta,
            "cliente": nombre_cliente,
            "items": carrito,
        }
        datos.ventas_db.append(nueva_venta)
        guardar_historial_ventas()
        print("✅ ¡Venta finalizada con éxito!")
    else:
        print("⚠️ Venta cancelada.")
        cargar_datos_sistema()


def generar_archivo_factura(items, total, nombre, cedula, puntos):
    if not os.path.exists(CARPETA_FACTURAS):
        os.makedirs(CARPETA_FACTURAS)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{CARPETA_FACTURAS}/FACT_{timestamp}_{cedula}.txt"

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("========================================\n")
        f.write("          TIENDA HADES - TICKET\n")
        f.write("========================================\n")
        f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"Cliente: {nombre}\n")
        f.write(f"RUC/CI:  {cedula}\n")
        f.write("----------------------------------------\n")
        f.write(f"{'CANT':<5} {'PRODUCTO':<20} {'SUBTOTAL'}\n")
        f.write("----------------------------------------\n")
        for i in items:
            f.write(f"{i['cantidad']:<5} {i['nombre']:<20} ${i['subtotal']:.2f}\n")
        f.write("----------------------------------------\n")
        f.write(f"TOTAL A PAGAR: $ {total:.2f}\n")
        f.write("========================================\n")
        if puntos > 0:
            f.write(f"¡Has ganado {puntos} Puntos Hades!\n")
            f.write("Gracias por tu preferencia.\n")

    print(f"📄 Factura generada: {nombre_archivo}")


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
    direccion = input("Dirección de entrega: ")
    notas = input("Notas adicionales: ")

    datos.clientes_db[cedula] = {
        "nombre": nombre,
        "telefono": telefono,
        "correo": correo,
        "direccion": direccion,
        "notas": notas,
        "puntos": 0,
        "nivel": "Bronce",
        "fecha_registro": datetime.now().strftime("%Y-%m-%d"),
    }
    guardar_clientes()
    print(f"✅ ¡{nombre} registrado con éxito!")


def buscar_cliente_pro():
    cedula = input("\nIngrese Cédula/RUC para auditoría: ").strip()

    # Usamos .get() para evitar errores si la cédula no existe
    cliente = datos.clientes_db.get(cedula)

    if cliente:
        print(f"\n🌟 EXPEDIENTE DE CLIENTE 🌟")
        print(f"---------------------------")
        # El truco: .get('clave', 'valor_por_defecto')
        # Si 'nivel' no existe, usará "Bronce" en vez de tronar
        nivel = cliente.get("nivel", "Bronce")
        nombre = cliente.get("nombre", "Desconocido")

        print(f"Nombre: {nombre} [{nivel}]")

        # Hacemos lo mismo con los otros campos nuevos
        direccion = cliente.get("direccion", "Sin dirección registrada")
        notas = cliente.get("notas", "Sin observaciones")
        puntos = cliente.get("puntos", 0)

        print(f"Ubicación: {direccion}")
        print(f"Fidelidad: {puntos} puntos")
        print(f"Observaciones: {notas}")
        print(f"---------------------------")
    else:
        print("❌ El expediente no existe en el Inframundo (Hades).")


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
    print(f"\n--- 🔒 ACCESO SEGURO HADES V-1.6.3 ---")
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
