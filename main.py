import sys
from datetime import datetime

# --- SIMULACIÓN DE BASE DE DATOS (EN MEMORIA) ---
# En el futuro, esto se moverá a archivos o base de datos.

# Usuarios para el Login (RF-001, RF-002)
usuarios_db = {
    "admin": {"pass": "admin123", "rol": "Administrador"},
    "empleado": {"pass": "user123", "rol": "Empleado"}
}

# Inventario (RF-003, RF-007)
# Estructura: 'codigo': {'nombre', 'categoria', 'precio', 'stock'}
inventario_db = {}

# Historial de movimientos (Para auditoría básica)
movimientos_log = []

# --- FUNCIONES DEL SISTEMA ---

def login():
    """Gestiona el inicio de sesión (RF-001)."""
    print("\n--- BIENVENIDO AL SISTEMA DE INVENTARIO (PAPELERÍA) ---")
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

def registrar_producto():
    """Permite registrar nuevos productos (RF-003)."""
    print("\n--- REGISTRO DE NUEVO PRODUCTO ---")
    codigo = input("Ingrese Código del producto (o ENTER para cancelar): ")
    if not codigo: return

    if codigo in inventario_db:
        print("¡Error! Ese código ya existe.")
        return

    nombre = input("Nombre del producto: ")
    categoria = input("Categoría: ")
    
    # Validación simple de números
    try:
        precio = float(input("Precio unitario: "))
        cantidad = int(input("Cantidad inicial: "))
    except ValueError:
        print("Error: Precio y Cantidad deben ser números.")
        return

    # Guardamos en el diccionario
    inventario_db[codigo] = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": cantidad
    }
    
    # TODO: Aquí iría la generación del código QR (RF-002 descripción)
    print(f"Producto '{nombre}' registrado con éxito.")

def registrar_movimiento():
    """Control de Entradas y Salidas (RF-006)."""
    print("\n--- REGISTRO DE ENTRADAS / SALIDAS ---")
    codigo = input("Ingrese Código del producto: ")

    if codigo not in inventario_db:
        print("Error: Producto no encontrado.")
        return

    producto = inventario_db[codigo]
    print(f"Producto seleccionado: {producto['nombre']} | Stock actual: {producto['stock']}")

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

    # Lógica de actualización de stock
    if tipo == "E":
        producto['stock'] += cantidad
        print(f"Stock actualizado. Nuevo total: {producto['stock']}")
    elif tipo == "S":
        if cantidad > producto['stock']:
            print("Error: Stock insuficiente para realizar la salida.")
            return
        producto['stock'] -= cantidad
        print(f"Salida registrada. Nuevo total: {producto['stock']}")

    # Registro en log
    movimiento = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "producto": producto['nombre'],
        "tipo": "ENTRADA" if tipo == "E" else "SALIDA",
        "cantidad": cantidad
    }
    movimientos_log.append(movimiento)

def consultar_inventario():
    """Consulta de stock disponible (RF-007)."""
    print("\n--- INVENTARIO ACTUAL ---")
    if not inventario_db:
        print("El inventario está vacío.")
    else:
        print(f"{'CÓDIGO':<10} | {'NOMBRE':<20} | {'CATEGORÍA':<15} | {'PRECIO':<10} | {'STOCK':<5}")
        print("-" * 75)
        for codigo, datos in inventario_db.items():
            print(f"{codigo:<10} | {datos['nombre']:<20} | {datos['categoria']:<15} | ${datos['precio']:<9} | {datos['stock']:<5}")

def menu_principal():
    rol_usuario = login()
    
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Registrar Producto")
        print("2. Registrar Entrada/Salida")
        print("3. Consultar Inventario")
        print("4. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            # Según RF-003, esto es responsabilidad del Administrador principalmente
            if rol_usuario == "Administrador":
                registrar_producto()
            else:
                print("Acceso denegado. Solo administradores pueden crear productos.")
        elif opcion == "2":
            registrar_movimiento()
        elif opcion == "3":
            consultar_inventario()
        elif opcion == "4":
            print("Cerrando sistema...")
            break
        else:
            print("Opción no válida.")

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    menu_principal()