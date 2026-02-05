from core.utils import limpiar_pantalla
from core.datos import PERMISOS_DISPONIBLES, ROLES_PLANTILLA


# --- MENÚS DE ACCESO ---
def mostrar_menu_inicio_sesion():
    limpiar_pantalla()
    print("=" * 40)
    print("      🔐 BIENVENIDO A HADES POS")
    print("=" * 40)
    print("1. Iniciar Sesión (Personal y Clientes)")
    print("2. Registrarse como EMPLEADO (Solicitud)")
    print("3. Olvidé mi Usuario / Contraseña")
    print("-" * 40)
    print("4. 🛍️  ENTRAR COMO INVITADO (Ver Catálogo)")
    print("-" * 40)
    print("5. Salir")
    return input("\n>> Opción: ")


def menu_fallo_intentos():
    print("\n⚠️ ¡Aviso de Seguridad!")
    print("1. Olvidé mi contraseña (Recuperar)")
    print("2. Reiniciar intentos (Volver a probar)")
    print("3. Salir del programa")
    return input(">> ¿Qué desea hacer?: ")


# --- MENÚS DE INVITADO / CLIENTE ---
def menu_modo_invitado(items_carrito):
    limpiar_pantalla()
    print(f"🛍️  MODO CLIENTE/INVITADO | Carrito: {items_carrito} items")
    print("=" * 40)
    print("1. Ver Catálogo de Productos")
    print("2. Agregar Producto al Carrito")
    print("3. Ver mi Carrito")
    print("4. ✅ FINALIZAR COMPRA (Checkout)")
    print("5. Salir / Cerrar Sesión")
    return input("\n>> Opción: ")


def menu_checkout_cliente():
    print("\n--- 💳 CHECKOUT / FINALIZAR ---")
    print("Para procesar su compra, elija una opción:")
    print("1. 👤 Ya tengo cuenta (Iniciar Sesión)")
    print("2. 📝 Registrarme ahora (Crear cuenta y guardar datos)")
    print("3. 👻 Continuar como Invitado (Solo datos de factura)")
    print("4. Cancelar")
    return input(">> Seleccione: ")


# --- MENÚS DE EMPLEADO (Los clásicos) ---
def mostrar_menu_principal(usuario, rol):
    limpiar_pantalla()
    print("=" * 50)
    print(f" SISTEMA HADES - TERMINAL (V-1.7.2)")
    print(f" Usuario: {usuario} | Rol: {rol}")
    print("=" * 50)
    print("\n[ ADMINISTRACIÓN ]")
    print("1. Registrar Producto")
    print("2. Editar Producto")
    print("3. Eliminar Producto")
    print("4. Regenerar QRs")
    print("5. Gestión de Personal (Usuarios) 👮")
    print("\n[ OPERACIÓN ]")
    print("6. Movimientos Stock (Entrada/Salida)")
    print("7. Consultar Inventario")
    print("8. Registrar Venta (Caja) 🛒")
    print("9. Reportes y Cierre de Caja 📉")
    print("10. Gestión de Clientes 👥")
    print("\n[ SEGURIDAD ]")
    print("11. Ver MI CÓDIGO DE RECUPERACIÓN 🔐")
    print("\n12. Salir")
    return input("\n>> Seleccione opción: ")


def menu_reportes():
    limpiar_pantalla()
    print("--- 📉 REPORTES Y CIERRE ---")
    print("1. Ver Historial Completo de Ventas")
    print("2. 📠 Realizar CIERRE DE CAJA (Hoy)")
    print("3. Volver")
    return input("\n>> Seleccione: ")


def menu_gestion_clientes():
    # Evitamos circular import importando dentro
    import cli.operaciones as ops

    while True:
        limpiar_pantalla()
        print("--- 👥 GESTIÓN DE CLIENTES ---")
        print("1. Registrar Cliente")
        print("2. Listar Clientes")
        print("3. Buscar Cliente (Detalles)")
        print("4. Volver")
        op = input("\n>> Seleccione: ")

        if op == "1":
            ops.registrar_cliente_interactivo()
        elif op == "2":
            ops.listar_clientes()
        elif op == "3":
            ops.buscar_cliente_pro()
        elif op == "4":
            break
        input("\nPresione [ENTER] para continuar...")


def menu_gestion_usuarios():
    limpiar_pantalla()
    print("--- 👮 GESTIÓN DE PERSONAL ---")
    print("1. Crear Nuevo Usuario")
    print("2. Listar Personal")
    print("3. Eliminar Usuario")
    print("4. Modificar Permisos (Avanzado) 🔧")
    print("5. Editar Datos (Nombre/Clave/Rol) ✏️")
    print("6. Volver")
    return input("\n>> Seleccione: ")


def menu_editar_campo_usuario(usuario):
    print(f"\n--- ✏️ EDITANDO A: {usuario} ---")
    print("1. Cambiar Nombre de Usuario (Login)")
    print("2. Cambiar Contraseña")
    print("3. Cambiar Rol (Resetea permisos)")
    print("4. Volver")
    return input(">> ¿Qué desea modificar?: ")


def menu_seleccion_rol():
    print("\n--- SELECCIÓN DE ROL ---")
    print("1. Administrador (Control Total)")
    print("2. Cajero (Ventas + Clientes)")
    print("3. Bodeguero (Stock + Productos)")
    print("4. Supervisor (Gestión sin Admin)")
    print("5. 🔧 PERSONALIZADO (Elegir permisos manualmente)")
    return input(">> Seleccione Rol: ")


def interfaz_modificar_permisos(usuario, rol_actual, permisos_actuales):
    limpiar_pantalla()
    print(f"🔧 EDITANDO PERMISOS DE: {usuario}")
    print(f" Rol actual: {rol_actual}")
    print("-" * 50)
    nuevos = []
    for clave, desc in PERMISOS_DISPONIBLES.items():
        tiene = clave in permisos_actuales
        icon = "✅ SI" if tiene else "❌ NO"
        r = input(f"  [{icon}] {clave} ({desc}) -> Nuevo estado? (S/N): ").upper()
        if r == "S":
            nuevos.append(clave)
        elif r == "N":
            pass
        else:
            if tiene:
                nuevos.append(clave)
    return nuevos


def menu_seleccion_factura():
    print("\n--- 👤 DATOS DE FACTURACIÓN ---")
    print("1. Consumidor Final")
    print("2. Cliente Ya Registrado (Buscar por Cédula)")
    print("3. Registrar Nuevo Cliente Ahora Mismo")
    return input("Seleccione opción (1-3): ").strip()
