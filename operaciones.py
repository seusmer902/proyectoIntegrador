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
    print("\n--- 🛒 NUEVA VENTA (CAJA V-1.6.2.1) ---")
    carrito = []
    total_bruto = 0.0

    # 1. Bucle de Venta (Igual que antes)
    while True:
        print(f"\n>> Items: {len(carrito)} | Subtotal: ${total_bruto:.2f}")
        codigo = input("Código (o 'F' para pagar): ").strip()

        if codigo.upper() == "F":
            break

        if codigo not in datos.inventario_db:
            print("❌ Producto no encontrado.")
            continue

        prod = datos.inventario_db[codigo]
        # Mostramos stock y precio
        print(f"   Seleccionado: {prod['nombre']} | ${prod['precio']:.2f}")

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
                total_bruto += subtotal
                prod["stock"] -= cant  # Resta virtual
                print(f"   ✅ Agregado.")
            else:
                print(f"   ❌ Stock insuficiente.")
        except ValueError:
            print("   ⚠️ Error de cantidad.")

    if not carrito:
        print("\n🚫 Carrito vacío.")
        datos.cargar_datos_sistema()
        return

    # 2. ASIGNACIÓN DE CLIENTE
    print("\n--- 👤 DATOS DE FACTURACIÓN ---")
    print("1. Consumidor Final")
    print("2. Cliente Ya Registrado")
    print("3. Registrar Nuevo")

    op_cliente = input("Seleccione: ").strip()

    cliente_data = None
    cedula_cliente = "9999999999"
    nombre_cliente = "Consumidor Final"
    nivel_cliente = "Bronce"  # Por defecto

    if op_cliente == "2":
        ced = input("Cédula/RUC: ").strip()
        if ced in datos.clientes_db:
            cliente_data = datos.clientes_db[ced]
            nombre_cliente = cliente_data["nombre"]
            cedula_cliente = ced
            nivel_cliente = cliente_data.get("nivel", "Bronce")
            print(f"✅ Hola {nombre_cliente}! Eres nivel {nivel_cliente}")
        else:
            print("⚠️ No encontrado. Se usará Consumidor Final.")

    elif op_cliente == "3":
        registrar_cliente_interactivo()
        # Recuperamos al último
        if datos.clientes_db:
            ced_nueva = list(datos.clientes_db.keys())[-1]
            cliente_data = datos.clientes_db[ced_nueva]
            nombre_cliente = cliente_data["nombre"]
            cedula_cliente = ced_nueva
            nivel_cliente = "Bronce"
            print(f"✅ Cliente nuevo asignado: {nombre_cliente}")

    # 3. CÁLCULO DE DESCUENTOS (¡LO NUEVO!)
    porcentaje_descuento = 0
    if nivel_cliente == "Plata":
        porcentaje_descuento = 0.05  # 5%
    elif nivel_cliente == "Oro":
        porcentaje_descuento = 0.10  # 10%

    monto_descuento = total_bruto * porcentaje_descuento
    total_neto = total_bruto - monto_descuento

    print("\n" + "=" * 40)
    print(f"SUBTOTAL:           ${total_bruto:.2f}")
    if porcentaje_descuento > 0:
        print(f"DESCUENTO ({nivel_cliente}): -${monto_descuento:.2f}")
    print(f"TOTAL A PAGAR:      ${total_neto:.2f}")
    print("=" * 40)

    if input("\n¿Confirmar venta? (S/N): ").upper() == "S":
        datos.guardar_inventario()

        # Lógica de Puntos (Basada en el total neto pagado)
        puntos_ganados = 0
        if cliente_data:
            puntos_ganados = int(total_neto)  # Gana puntos por lo que pagó realmente
            cliente_data["puntos"] = cliente_data.get("puntos", 0) + puntos_ganados

            # Recalcular Nivel
            pts = cliente_data["puntos"]
            nuevo_nivel = "Bronce"
            if pts > 500:
                nuevo_nivel = "Oro"
            elif pts > 100:
                nuevo_nivel = "Plata"

            if nuevo_nivel != nivel_cliente:
                print(f"🎉 ¡El cliente subió de nivel a {nuevo_nivel}!")

            cliente_data["nivel"] = nuevo_nivel
            datos.guardar_clientes()

        # Generar Factura (Pasamos todos los datos nuevos)
        generar_archivo_factura(
            carrito,
            total_bruto,
            monto_descuento,
            total_neto,
            nombre_cliente,
            cedula_cliente,
            puntos_ganados,
            nivel_cliente,
        )

        # Historial
        nueva_venta = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total_neto,
            "cliente": nombre_cliente,
            "items": carrito,
        }
        datos.ventas_db.append(nueva_venta)
        datos.guardar_historial_ventas()
        print("✅ Venta finalizada.")
    else:
        print("⚠️ Cancelado.")
        datos.cargar_datos_sistema()


def generar_archivo_factura(
    items, subtotal, descuento, total, nombre, cedula, puntos, nivel
):
    if not os.path.exists(CARPETA_FACTURAS):
        os.makedirs(CARPETA_FACTURAS)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{CARPETA_FACTURAS}/FACT_{timestamp}_{cedula}.txt"

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("=" * 40 + "\n")
        f.write(f"{'TIENDA HADES - TICKET':^40}\n")  # Centrado
        f.write("=" * 40 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"Cliente: {nombre}\n")
        f.write(f"RUC/CI:  {cedula}\n")
        if nivel != "Bronce":
            f.write(f"Nivel:   {nivel} (Desc. Aplicado)\n")
        f.write("-" * 40 + "\n")

        # ENCABEZADOS DE COLUMNAS FIJAS
        # {Texto : <Espacio} alinea a la izquierda
        # {Texto : >Espacio} alinea a la derecha
        f.write(f"{'CANT':<5} {'PRODUCTO':<20} {'SUBTOTAL':>10}\n")
        f.write("-" * 40 + "\n")

        for i in items:
            # TRUCO DE ALINEACIÓN:
            # i['nombre'][:19] -> Corta el nombre si tiene más de 19 letras
            # :<20 -> Rellena con espacios hasta llegar a 20 caracteres
            nombre_fmt = f"{i['nombre'][:19]:<20}"
            f.write(f"{i['cantidad']:<5} {nombre_fmt} ${i['subtotal']:>9.2f}\n")

        f.write("-" * 40 + "\n")
        f.write(f"SUBTOTAL:          ${subtotal:>10.2f}\n")
        if descuento > 0:
            f.write(f"DESCUENTO:        -${descuento:>10.2f}\n")
        f.write(f"TOTAL A PAGAR:     ${total:>10.2f}\n")
        f.write("=" * 40 + "\n")

        if puntos > 0:
            f.write(f"\n[+] Ganaste {puntos} Puntos Hades\n")
            f.write(f"    Gracias por tu compra.\n")

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
