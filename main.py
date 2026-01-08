import sys
import json
import os
import qrcode
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CONSTANTES
# ==========================================
ARCHIVO_DATOS = "inventario.json"
ARCHIVO_VENTAS = "ventas.json"
CARPETA_QR = "codigos_qr"

# Variables Globales en Memoria
inventario_db = {}
ventas_db = []
usuarios_db = {
    "admin": {"pass": "123", "rol": "Administrador"},
    "empleado": {"pass": "123", "rol": "Empleado"},
}

# Datos Semilla (Solo si el archivo no existe)
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
    "PAP-003": {
        "nombre": "Resma Papel A4",
        "categoria": "Papel",
        "precio": 4.50,
        "stock": 30,
    },
}


# ==========================================
# 2. PERSISTENCIA (MANEJO DE ARCHIVOS)
# ==========================================
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


# ==========================================
# 3. UTILIDADES Y HERRAMIENTAS
# ==========================================
def limpiar_pantalla():
    """Limpia la consola según el SO."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def generar_qr(nombre_archivo, info_contenido):
    """Genera una imagen QR en la carpeta designada."""
    if not os.path.exists(CARPETA_QR):
        os.makedirs(CARPETA_QR)

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(info_contenido)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    ruta = f"{CARPETA_QR}/{nombre_archivo}.png"
    img.save(ruta)
    print(f">> QR generado: {ruta}")


# ==========================================
# 4. ADMINISTRACIÓN DE PRODUCTOS (CRUD)
# ==========================================
def registrar_producto():
    print("\n--- REGISTRO DE PRODUCTO ---")
    codigo = input("Código (ej: PAP-001): ").strip()
    if codigo in inventario_db:
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

    inventario_db[codigo] = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
    }
    guardar_inventario()

    # Generar QR automático
    datos_qr = f"ID:{codigo}\nProd:{nombre}\nPrecio:${precio:.2f}"
    generar_qr(codigo, datos_qr)
    print("✅ Producto registrado correctamente.")


def editar_producto():
    print("\n--- EDITAR PRODUCTO ---")
    codigo = input("Código a editar: ").strip()
    if codigo not in inventario_db:
        print("⚠️ No existe.")
        return

    prod = inventario_db[codigo]
    print(f">> Editando: {prod['nombre']} (Enter para mantener valor actual)")

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
    if codigo in inventario_db:
        if input("¿Seguro? (SI/NO): ").upper() == "SI":
            del inventario_db[codigo]
            guardar_inventario()
            print("🗑️ Producto eliminado.")
    else:
        print("⚠️ No existe.")


def regenerar_qr_manualmente():
    print("\n--- REGENERAR QRS ---")
    op = input("1. Uno solo\n2. Todos\nOpción: ")

    if op == "1":
        codigo = input("Código: ").strip()
        if codigo in inventario_db:
            p = inventario_db[codigo]
            info = f"ID:{codigo}\nProd:{p['nombre']}\nPrecio:${p['precio']:.2f}"
            generar_qr(codigo, info)
    elif op == "2":
        if input("¿Seguro? (SI/NO): ").upper() == "SI":
            count = 0
            for cod, p in inventario_db.items():
                info = f"ID:{cod}\nProd:{p['nombre']}\nPrecio:${p['precio']:.2f}"
                generar_qr(cod, info)
                count += 1
            print(f"✅ {count} QRs regenerados.")


# ==========================================
# 5. OPERACIONES (VENTAS Y MOVIMIENTOS)
# ==========================================
def registrar_movimiento():
    """Entrada o Salida de stock por logística (no venta)."""
    print("\n--- MOVIMIENTOS DE STOCK ---")
    codigo = input("Código del producto: ").strip()
    if codigo not in inventario_db:
        print("⚠️ No existe.")
        return

    tipo = input("Tipo (E=Entrada / S=Salida): ").upper()
    try:
        cant = int(input("Cantidad: "))
    except ValueError:
        return

    stock_actual = inventario_db[codigo]["stock"]

    if tipo == "E":
        inventario_db[codigo]["stock"] += cant
        print(f"✅ Nuevo stock: {inventario_db[codigo]['stock']}")
        guardar_inventario()
    elif tipo == "S":
        if cant <= stock_actual:
            inventario_db[codigo]["stock"] -= cant
            print(f"✅ Nuevo stock: {inventario_db[codigo]['stock']}")
            guardar_inventario()
        else:
            print("⚠️ Stock insuficiente.")
    else:
        print("⚠️ Tipo inválido.")


def registrar_venta():
    """Sistema de Ventas con Carrito de Compras."""
    print("\n--- 🛒 NUEVA VENTA (CARRITO) ---")
    carrito = []
    total_venta = 0.0

    while True:
        print(f"\n>> Items: {len(carrito)} | Total Parcial: ${total_venta:.2f}")
        codigo = input("Código (o 'F' para finalizar): ").strip()

        if codigo.upper() == "F":
            break

        if codigo not in inventario_db:
            print("❌ Producto no encontrado.")
            continue

        prod = inventario_db[codigo]
        print(
            f"   Seleccionado: {prod['nombre']} | Precio: ${prod['precio']:.2f} | Stock: {prod['stock']}"
        )

        try:
            cant = int(input("   Cantidad: "))
            if cant <= 0:
                print("   ⚠️ Cantidad inválida.")
                continue

            # Validación simple de stock
            # (Nota: Para mayor precisión se debería restar lo que ya está en carrito,
            # pero para este nivel, validar contra el stock actual está bien)
            if cant <= prod["stock"]:
                subtotal = cant * prod["precio"]

                # Agregar al carrito
                item = {
                    "codigo": codigo,
                    "nombre": prod["nombre"],
                    "cantidad": cant,
                    "precio": prod["precio"],
                    "subtotal": subtotal,
                }
                carrito.append(item)
                total_venta += subtotal

                # Resta virtual temporal para no vender lo que no hay
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
        ventas_db.append(nueva_venta)
        guardar_historial_ventas()

        print("✅ ¡Venta registrada exitosamente!")
    else:
        print("⚠️ Venta cancelada.")
        cargar_datos_sistema()  # Revertir cambios


# ==========================================
# 6. REPORTES Y CONSULTAS
# ==========================================
def consultar_inventario():
    print("\n" + "=" * 60)
    print(f"{'CÓDIGO':<10} | {'NOMBRE':<30} | {'PRECIO':<8} | {'STOCK'}")
    print("-" * 60)

    for cod, datos in inventario_db.items():
        print(
            f"{cod:<10} | {datos['nombre']:<30} | ${datos['precio']:<7.2f} | {datos['stock']}"
        )

    print("=" * 60)


def consultar_historial_ventas():
    print("\n--- HISTORIAL DE VENTAS ---")
    if not ventas_db:
        print("No hay registros.")
        return

    total_acumulado = 0.0
    print(f"{'FECHA':<20} {'ITEMS':<10} {'TOTAL'}")
    print("-" * 45)

    for v in ventas_db:
        cant_items = sum(item["cantidad"] for item in v["items"])
        print(f"{v['fecha']:<20} {cant_items:<10} ${v['total']:.2f}")
        total_acumulado += v["total"]

    print("-" * 45)
    print(f"💰 INGRESOS TOTALES: ${total_acumulado:.2f}")


# ==========================================
# 7. MENÚ PRINCIPAL Y LOGIN
# ==========================================
def login():
    print(f"\n--- SISTEMA DE INVENTARIO V-1.5.3 ---")
    intentos = 3
    while intentos > 0:
        user = input("Usuario: ")
        pwd = input("Contraseña: ")

        if user in usuarios_db and usuarios_db[user]["pass"] == pwd:
            return usuarios_db[user]["rol"]

        print("⛔ Credenciales incorrectas.")
        intentos -= 1
    sys.exit()


def menu_principal():
    cargar_datos_sistema()
    rol = login()

    while True:
        limpiar_pantalla()
        print("=" * 40)
        print(f"   SISTEMA HADES - TERMINAL (V-1.5.3)")
        print(f"   Usuario: {rol}")
        print("=" * 40)

        print("\n[ ADMINISTRACIÓN ]")
        print("1. Registrar Producto")
        print("2. Editar Producto")
        print("3. Eliminar Producto")
        print("4. Regenerar QRs")

        print("\n[ OPERACIÓN ]")
        print("5. Movimientos Stock (Entrada/Salida)")
        print("6. Consultar Inventario")
        print("7. Registrar Venta (Caja) 🛒")
        print("8. Historial de Ventas 📊")

        print("\n9. Salir")

        op = input("\n>> Seleccione opción: ")

        # --- Lógica de Admin ---
        if op in ["1", "2", "3", "4"]:
            if rol == "Administrador":
                if op == "1":
                    registrar_producto()
                elif op == "2":
                    editar_producto()
                elif op == "3":
                    eliminar_producto()
                elif op == "4":
                    regenerar_qr_manualmente()
            else:
                print("⛔ Acceso denegado (Requiere Admin).")

        # --- Lógica General ---
        elif op == "5":
            registrar_movimiento()
        elif op == "6":
            consultar_inventario()
        elif op == "7":
            registrar_venta()
        elif op == "8":
            consultar_historial_ventas()
        elif op == "9":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("⚠️ Opción no válida.")

        # Pausa antes de limpiar pantalla
        print("\n" + "-" * 40)
        input("Presione [ENTER] para volver al menú...")


# PUNTO DE ENTRADA
if __name__ == "__main__":
    menu_principal()
