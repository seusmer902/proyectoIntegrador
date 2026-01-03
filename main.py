import sys
import json
import os
from datetime import datetime
import qrcode  # <--- NUEVO IMPORT

# --- CONFIGURACIÓN DE ARCHIVOS ---
ARCHIVO_DATOS = "inventario.json"

# --- DATOS POR DEFECTO (SEMILLA) ---
# Estos se cargarán solo si no existe un historial previo.
INVENTARIO_INICIAL = {
    "PAP-001": {"nombre": "Cuaderno Universitario 100h", "categoria": "Cuadernos", "precio": 1.50, "stock": 50},
    "PAP-002": {"nombre": "Esfero Azul Bic", "categoria": "Escritura", "precio": 0.60, "stock": 200},
    "PAP-003": {"nombre": "Resma Papel Bond A4", "categoria": "Papel", "precio": 4.50, "stock": 30},
    "PAP-004": {"nombre": "Juego Geométrico", "categoria": "Útiles", "precio": 2.25, "stock": 15},
    "PAP-005": {"nombre": "Lápiz Mongul HB", "categoria": "Escritura", "precio": 0.40, "stock": 100},
    "PAP-006": {"nombre": "Carpeta Plástica Roja", "categoria": "Oficina", "precio": 0.85, "stock": 60}
}

# --- BASE DE DATOS DE USUARIOS (SIMULADA) ---
usuarios_db = {
    "admin": {"pass": "admin123", "rol": "Administrador"},
    "empleado": {"pass": "user123", "rol": "Empleado"}
}

# Variable global para el inventario
inventario_db = {}

# --- FUNCIONES DE PERSISTENCIA (GUARDAR/CARGAR) ---

def cargar_datos():
    """Carga los datos del archivo JSON o crea los iniciales si no existe."""
    global inventario_db
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                inventario_db = json.load(f)
            # print(">> Datos cargados correctamente.") # (Opcional: para depuración)
        except json.JSONDecodeError:
            print(">> Error al leer el archivo. Se iniciará vacío.")
            inventario_db = {}
    else:
        print(">> Primera ejecución detectada. Cargando productos predeterminados...")
        inventario_db = INVENTARIO_INICIAL.copy()
        guardar_datos()

def guardar_datos():
    """Guarda el estado actual del inventario en el archivo JSON."""
    try:
        with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
            json.dump(inventario_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar datos: {e}")

# --- FUNCIONES DEL SISTEMA ---

def login():
    """Gestiona el inicio de sesión."""
    print("\n--- BIENVENIDO AL SISTEMA DE INVENTARIO (PAPELERÍA) V-1.2 ---")
    intentos = 3
    while intentos > 0:
        usuario = input("Usuario: ")
        password = input("Contraseña: ")

        if usuario in usuarios_db and usuarios_db[usuario]["pass"] == password:
            print(f"\n¡Bienvenido, {usuario}! Rol: {usuarios_db[usuario]['rol']}")
            return usuarios_db[usuario]['rol']
        else:
            print("Credenciales incorrectas.")
            intentos -= 1
    
    print("Demasiados intentos fallidos. Saliendo...")
    sys.exit()

def generar_qr(nombre_archivo, info_contenido):
    """
    Genera un QR.
    nombre_archivo: Cómo se llamará la imagen (ej: PAP-001).
    info_contenido: Texto que aparecerá al escanearlo.
    """
    carpeta = "codigos_qr"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    # Configuramos el QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Aquí metemos toda la información combinada
    qr.add_data(info_contenido)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    ruta = f"{carpeta}/{nombre_archivo}.png"
    img.save(ruta)
    print(f">> QR generado con éxito en: {ruta}")

def registrar_producto():
    """Registra productos y genera un QR con información detallada."""
    print("\n--- REGISTRO DE NUEVO PRODUCTO ---")
    codigo = input("Ingrese Código del producto (o ENTER para cancelar): ")
    if not codigo: return

    if codigo in inventario_db:
        print("¡Error! Ese código ya existe.")
        return

    nombre = input("Nombre del producto: ")
    categoria = input("Categoría: ")
    
    try:
        precio = float(input("Precio unitario: "))
        cantidad = int(input("Cantidad inicial: "))
    except ValueError:
        print("Error: Precio y Cantidad deben ser números.")
        return

    # 1. Guardar en la "Base de Datos"
    inventario_db[codigo] = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": cantidad
    }
    guardar_datos()
    
    # 2. Preparar la info para el QR (Aquí ocurre la magia)
    # Usamos \n para saltos de línea, así se ve ordenado en el celular.
    texto_qr = (
        f"ID: {codigo}\n"
        f"Producto: {nombre}\n"
        f"Categoría: {categoria}\n"
        f"Precio: ${precio:.2f}"
    )
    
    print("Generando código QR con información...")
    # Pasamos el ID (para el nombre del archivo) y el TEXTO COMPLETO (para el contenido)
    generar_qr(codigo, texto_qr) 
    
    print(f"Producto '{nombre}' registrado correctamente.")

def editar_producto():
    """Permite modificar nombre, categoría, precio o stock de un producto (RF-004)."""
    print("\n--- EDICIÓN DE PRODUCTO ---")
    codigo = input("Ingrese el Código del producto a editar: ")

    if codigo not in inventario_db:
        print("Error: El producto no existe.")
        return

    # Obtenemos los datos actuales
    producto = inventario_db[codigo]
    print(f"\nEditando: {producto['nombre']}")
    print("Presione ENTER sin escribir nada para mantener el valor actual.\n")

    # 1. Editar Nombre
    nuevo_nombre = input(f"Nombre actual [{producto['nombre']}]: ")
    if nuevo_nombre:  # Si el usuario escribió algo, lo actualizamos
        producto['nombre'] = nuevo_nombre

    # 2. Editar Categoría
    nueva_categoria = input(f"Categoría actual [{producto['categoria']}]: ")
    if nueva_categoria:
        producto['categoria'] = nueva_categoria

    # 3. Editar Precio (con validación)
    nuevo_precio_str = input(f"Precio actual [${producto['precio']}]: ")
    if nuevo_precio_str:
        try:
            producto['precio'] = float(nuevo_precio_str)
        except ValueError:
            print(">> Error: El precio debe ser un número. Se mantuvo el valor anterior.")

    # 4. Editar Stock (con validación)
    nuevo_stock_str = input(f"Stock actual [{producto['stock']}]: ")
    if nuevo_stock_str:
        try:
            producto['stock'] = int(nuevo_stock_str)
        except ValueError:
            print(">> Error: El stock debe ser un entero. Se mantuvo el valor anterior.")

    guardar_datos() # Guardamos los cambios en el JSON
    print(f"\n¡Producto '{producto['nombre']}' actualizado correctamente!")

def eliminar_producto():
    """Permite eliminar un producto del inventario (RF-005)."""
    print("\n--- ELIMINACIÓN DE PRODUCTO ---")
    codigo = input("Ingrese el Código del producto a eliminar: ")

    if codigo not in inventario_db:
        print("Error: El producto no existe.")
        return

    producto = inventario_db[codigo]
    print(f"\nVa a eliminar: {producto['nombre']} (Stock: {producto['stock']})")
    confirmacion = input("¿Está seguro? Escriba 'SI' para confirmar: ").upper()

    if confirmacion == "SI":
        del inventario_db[codigo] # Borra el producto del diccionario
        guardar_datos()           # Guarda el cambio en el JSON
        print(">> ¡Producto eliminado correctamente!")
    else:
        print(">> Operación cancelada.")

def registrar_movimiento():
    """Control de Entradas y Salidas y guarda cambios."""
    print("\n--- REGISTRO DE ENTRADAS / SALIDAS ---")
    codigo = input("Ingrese Código del producto: ")

    if codigo not in inventario_db:
        print("Error: Producto no encontrado.")
        return

    producto = inventario_db[codigo]
    print(f"Producto: {producto['nombre']} | Stock actual: {producto['stock']}")

    tipo = input("Tipo de movimiento (E = Entrada / S = Salida): ").upper()
    if tipo not in ["E", "S"]:
        print("Opción no válida.")
        return

    try:
        cantidad = int(input("Cantidad a mover: "))
        if cantidad <= 0:
            print("La cantidad debe ser mayor a 0.")
            return
    except ValueError:
        print("Error: Ingrese un número válido.")
        return

    if tipo == "E":
        producto['stock'] += cantidad
        print(f"Entrada registrada. Nuevo total: {producto['stock']}")
    elif tipo == "S":
        if cantidad > producto['stock']:
            print("Error: Stock insuficiente.")
            return
        producto['stock'] -= cantidad
        print(f"Salida registrada. Nuevo total: {producto['stock']}")

    guardar_datos() # <--- GUARDAMOS CAMBIOS

def consultar_inventario():
    """Muestra la tabla de productos."""
    print("\n--- INVENTARIO ACTUAL ---")
    if not inventario_db:
        print("El inventario está vacío.")
    else:
        print(f"{'CÓDIGO':<10} | {'NOMBRE':<25} | {'CATEGORÍA':<15} | {'PRECIO':<8} | {'STOCK':<5}")
        print("-" * 80)
        for codigo, datos in inventario_db.items():
            print(f"{codigo:<10} | {datos['nombre']:<25} | {datos['categoria']:<15} | ${datos['precio']:<7} | {datos['stock']:<5}")

def menu_principal():
    cargar_datos()
    rol_usuario = login()
    
    while True:
        print("\n=== MENÚ PRINCIPAL (V-1.3) ===")
        print("1. Registrar Producto (Admin)")
        print("2. Editar Producto (Admin)")
        print("3. Eliminar Producto (Admin)") # <--- NUEVA OPCIÓN
        print("4. Registrar Entrada/Salida")
        print("5. Consultar Inventario")
        print("6. Salir")
        
        opcion = input("Seleccione una opción: ")

        # --- GESTIÓN DE PRODUCTOS (SOLO ADMIN) ---
        if opcion == "1":
            if rol_usuario == "Administrador":
                registrar_producto()
            else:
                print("Acceso denegado. Solo Admin.")
        
        elif opcion == "2":
            if rol_usuario == "Administrador":
                editar_producto()
            else:
                print("Acceso denegado. Solo Admin.")

        elif opcion == "3": # <--- LÓGICA DE ELIMINACIÓN
            if rol_usuario == "Administrador":
                eliminar_producto()
            else:
                print("Acceso denegado. Solo Admin.")

        # --- OPERACIONES GENERALES ---
        elif opcion == "4":
            registrar_movimiento()
        elif opcion == "5":
            consultar_inventario()
        elif opcion == "6":
            print("Guardando datos y saliendo...")
            break
        else:
            print("Opción no válida.")

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    menu_principal()
