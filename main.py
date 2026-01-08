import sys
import json
import os
import qrcode
from datetime import datetime

# --- CONFIGURACIÓN ---
ARCHIVO_DATOS = "inventario.json"
CARPETA_QR = "codigos_qr"


def limpiar_pantalla():
    # Detecta el sistema operativo y ejecuta el comando de limpieza
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # Linux / Mac
        os.system("clear")


# --- DATOS SEMILLA ---
INVENTARIO_INICIAL = {
    "PAP-001": {
        "nombre": "Cuaderno Universitario",
        "categoria": "Cuadernos",
        "precio": 1.50,
        "stock": 50,
    },
    "PAP-002": {
        "nombre": "Esfero Azul Bic",
        "categoria": "Escritura",
        "precio": 0.60,
        "stock": 200,
    },
    "PAP-003": {
        "nombre": "Resma Papel Bond A4",
        "categoria": "Papel",
        "precio": 4.50,
        "stock": 30,
    },
}

usuarios_db = {
    "admin": {"pass": "123", "rol": "Administrador"},
    "empleado": {"pass": "123", "rol": "Empleado"},
}

inventario_db = {}


# --- 1. PERSISTENCIA (GUARDAR/CARGAR) ---
def cargar_datos():
    global inventario_db
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                inventario_db = json.load(f)
        except json.JSONDecodeError:
            inventario_db = {}
    else:
        print(">> Primera ejecución. Cargando datos iniciales...")
        inventario_db = INVENTARIO_INICIAL.copy()
        guardar_datos()


def guardar_datos():
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(inventario_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar: {e}")


# --- 2. GENERADOR DE QR (LA IMPRESORA) ---
def generar_qr(nombre_archivo, info_contenido):
    """Crea la imagen QR en la carpeta."""
    if not os.path.exists(CARPETA_QR):
        os.makedirs(CARPETA_QR)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(info_contenido)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    ruta_completa = f"{CARPETA_QR}/{nombre_archivo}.png"
    img.save(ruta_completa)
    print(f">> QR generado con éxito en: {ruta_completa}")


# --- 3. FUNCIONES DEL SISTEMA ---
def login():
    print("\n--- SISTEMA DE INVENTARIO V-1.5.2 ---")
    intentos = 3
    while intentos > 0:
        usuario = input("Usuario: ")
        password = input("Contraseña: ")
        if usuario in usuarios_db and usuarios_db[usuario]["pass"] == password:
            return usuarios_db[usuario]["rol"]
        else:
            print("Credenciales incorrectas.")
            intentos -= 1
    sys.exit()


def registrar_producto():
    print("\n--- REGISTRO ---")
    codigo = input("Código (ej: PAP-001): ")
    if not codigo or codigo in inventario_db:
        print("Error: Código vacío o duplicado.")
        return

    nombre = input("Nombre: ")
    categoria = input("Categoría: ")
    try:
        precio = float(input("Precio: "))
        stock = int(input("Stock inicial: "))
    except ValueError:
        print("Error: Ingrese números válidos.")
        return

    inventario_db[codigo] = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
    }
    guardar_datos()

    # Generar QR Automático
    texto_qr = f"ID: {codigo}\nProducto: {nombre}\nPrecio: ${precio:.2f}"
    generar_qr(codigo, texto_qr)


def editar_producto():
    print("\n--- EDITAR ---")
    codigo = input("Código a editar: ")
    if codigo not in inventario_db:
        print("No existe.")
        return

    prod = inventario_db[codigo]
    print(f"Editando: {prod['nombre']} (Enter para mantener actual)")

    nuevo_nom = input(f"Nombre [{prod['nombre']}]: ")
    if nuevo_nom:
        prod["nombre"] = nuevo_nom

    nuevo_cat = input(f"Categoría [{prod['categoria']}]: ")
    if nuevo_cat:
        prod["categoria"] = nuevo_cat

    nuevo_pre = input(f"Precio [{prod['precio']}]: ")
    if nuevo_pre:
        prod["precio"] = float(nuevo_pre)

    guardar_datos()
    print("Actualizado correctamente.")


def eliminar_producto():
    codigo = input("\nCódigo a eliminar: ")
    if codigo in inventario_db:
        if input("¿Seguro? (SI/NO): ").upper() == "SI":
            del inventario_db[codigo]
            guardar_datos()
            print("Eliminado.")
    else:
        print("No existe.")


def regenerar_qr_manualmente():
    print("\n--- REGENERAR QRs ---")
    print("1. Uno solo")
    print("2. TODOS")
    opcion = input("Opción: ")

    if opcion == "1":
        codigo = input("Código: ")
        if codigo in inventario_db:
            p = inventario_db[codigo]
            texto = f"ID: {codigo}\nProducto: {p['nombre']}\nPrecio: ${p['precio']:.2f}"
            generar_qr(codigo, texto)
    elif opcion == "2":
        if input("¿Seguro? (SI/NO): ").upper() == "SI":
            contador = 0
            for codigo, p in inventario_db.items():
                texto = (
                    f"ID: {codigo}\nProducto: {p['nombre']}\nPrecio: ${p['precio']:.2f}"
                )
                generar_qr(codigo, texto)
                contador += 1
            print(f"Terminado. {contador} QRs generados.")


def registrar_movimiento():
    codigo = input("\nCódigo producto: ")
    if codigo not in inventario_db:
        print("No existe.")
        return

    tipo = input("Tipo (E=Entrada / S=Salida): ").upper()
    try:
        cant = int(input("Cantidad: "))
    except:
        return

    if tipo == "E":
        inventario_db[codigo]["stock"] += cant
        print(f"Nuevo stock: {inventario_db[codigo]['stock']}")
    elif tipo == "S":
        if cant <= inventario_db[codigo]["stock"]:
            inventario_db[codigo]["stock"] -= cant
            print(f"Nuevo stock: {inventario_db[codigo]['stock']}")
        else:
            print("Stock insuficiente.")
    guardar_datos()


def registrar_venta():
    print("\n--- REGISTRAR VENTA (Modo Carrito ) ---")
    carrito = []
    total_venta = 0.0

    while True:
        # Mostramos lo que llevamos hasta ahora
        print(
            f"\n--- En carrito: {len(carrito)} items | Total parcial: ${total_venta:.2f} ---"
        )
        codigo = input("Código del producto (o 'F' para finalizar/cobrar): ").strip()

        # 1. Salir del bucle si escribe 'F'
        if codigo.upper() == "F":
            break

        # 2. Validar existencia
        if codigo not in inventario_db:
            print("❌ Error: Producto no encontrado.")
            continue

        producto = inventario_db[codigo]
        print(
            f"   Seleccionado: {producto['nombre']} | Stock: {producto['stock']} | Precio: ${producto['precio']:.2f}"
        )

        # 3. Pedir cantidad
        try:
            cant_input = input("   Cantidad a vender: ")
            if not cant_input.isdigit():
                print("    Cantidad inválida, intenta de nuevo.")
                continue

            cantidad = int(cant_input)

            if cantidad <= 0:
                print("    La cantidad debe ser mayor a 0.")
                continue

            # Validar si hay suficiente stock (contando lo que ya llevas en el carrito si repites producto)
            stock_actual = producto["stock"]
            # Opcional: Podríamos restar lo que ya está en el carrito para ser más precisos,
            # pero por ahora validamos contra el stock real.

            if cantidad <= stock_actual:
                subtotal = cantidad * producto["precio"]

                # Agregar al carrito
                item = {
                    "codigo": codigo,
                    "nombre": producto["nombre"],
                    "cantidad": cantidad,
                    "precio": producto["precio"],
                    "subtotal": subtotal,
                }
                carrito.append(item)
                total_venta += subtotal

                # Restamos "virtualmente" del stock local para que no venda lo que no tiene si agrega el mismo producto dos veces
                producto["stock"] -= cantidad

                print(
                    f"    Agregado: {cantidad} x {producto['nombre']} (= ${subtotal:.2f})"
                )
            else:
                print(f"   Stock insuficiente. Solo quedan {stock_actual}.")

        except ValueError:
            print("   Error al ingresar cantidad.")

    # --- FINALIZAR VENTA ---
    if not carrito:
        print("\n Venta cancelada o carrito vacío.")
        # Revertimos cambios de stock virtual si canceló (opcional, pero buena práctica)
        # En este script simple, al no guardar, se revierte solo si cerramos,
        # pero para ser exactos recargamos datos si fuera necesario.
        return

    print("\n" + "=" * 40)
    print("           TICKET DE VENTA")
    print("=" * 40)
    print(f"{'PROD':<15} {'CANT':<5} {'PRECIO':<10} {'SUBTOTAL'}")
    print("-" * 40)

    for item in carrito:
        print(
            f"{item['nombre']:<15} {item['cantidad']:<5} ${item['precio']:<9.2f} ${item['subtotal']:.2f}"
        )

    print("-" * 40)
    print(f"TOTAL A PAGAR:      ${total_venta:.2f}")
    print("=" * 40)

    confirmar = input("\n¿Confirmar venta y guardar cambios? (S/N): ")
    if confirmar.upper() == "S":
        guardar_datos()  # Aquí es donde realmente se guarda el nuevo stock en el JSON
        print("¡Venta registrada exitosamente!")
    else:
        print("Venta cancelada. El inventario no se modificó.")
        # NOTA: Como restamos el stock en memoria durante el bucle para validar,
        # si cancela aquí, deberíamos recargar los datos originales.
        cargar_datos()


def consultar_inventario(inventario_db):
    print("\n" + "=" * 60)
    print(f"{'--- INVENTARIO ---':^50}")
    print("=" * 60)
    # Encabezado con anchos fijos
    print(f"{'CODIGO':<10} | {'NOMBRE':<30} | {'PRECIO':<5} | {'STOCK':<10}")
    print("-" * 60)

    for codigo, datos in inventario_db.items():
        nombre = datos.get("nombre", "N/A")
        stock = datos.get("stock", 0)
        precio = datos.get("precio", 0)
        # Imprimimos usando las variables que acabamos de extraer
        print(f"{codigo:<10} | {nombre:<30} | {precio:<5} | {stock:<10}")

    print("=" * 60 + "\n")


def menu_principal():
    cargar_datos()
    rol = login()

    while True:
        # 1. Limpiamos la pantalla al inicio de cada ciclo
        limpiar_pantalla()

        # 2. Imprimimos el encabezado bonito
        print("=" * 40)
        print(f"   SISTEMA DE INVENTARIO V-1.5.2")
        print(f"   Usuario: {rol}")
        print("=" * 40)

        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Registrar (Admin)")
        print("2. Editar (Admin)")
        print("3. Eliminar (Admin)")
        print("4. Regenerar QRs (Admin)")
        print("5. Movimientos (Entrada/Salida)")
        print("6. Consultar")
        print("7. Registrar Venta")
        print("8. Salir")

        op = input("\n>> Seleccione una opción: ")

        # --- Lógica de opciones ---
        if op == "1":
            if rol == "Administrador":
                registrar_producto()
            else:
                print("Acceso denegado.")

        elif op == "2":
            if rol == "Administrador":
                editar_producto()
            else:
                print("Acceso denegado.")

        elif op == "3":
            if rol == "Administrador":
                eliminar_producto()
            else:
                print("Acceso denegado.")

        elif op == "4":
            if rol == "Administrador":
                regenerar_qr_manualmente()
            else:
                print("Acceso denegado.")

        elif op == "5":
            registrar_movimiento()
        elif op == "6":
            consultar_inventario(inventario_db)
        elif op == "7":
            registrar_venta()
        elif op == "8":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n Opción no válida.")

        # 3. PAUSA ESTRATÉGICA
        # Esto evita que se borre el resultado inmediatamente.
        # El usuario tiene que dar "Enter" para volver al menú limpio.
        print("\n" + "-" * 40)
        input("Presione [ENTER] para volver al menú...")


if __name__ == "__main__":
    menu_principal()
