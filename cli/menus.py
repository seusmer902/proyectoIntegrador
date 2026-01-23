from core.utils import limpiar_pantalla
from core.datos import PERMISOS_DISPONIBLES, ROLES_PLANTILLA


def mostrar_menu_principal(usuario, rol):
    limpiar_pantalla()
    print("=" * 40)
    print(f"   🔥 SISTEMA HADES POS - CLI V1.7")
    print(f"   👤 Usuario: {usuario} | Rol: {rol}")
    print("=" * 40)
    print("1. Registrar Producto")
    print("2. Editar Producto")
    print("3. Eliminar Producto")
    print("4. Regenerar QR")
    print("5. Gestión de Usuarios (Admin)")
    print("6. Movimientos Stock (Entrada/Salida)")
    print("7. Consultar Inventario")
    print("8. CAJA / Registrar Venta")
    print("9. Reportes y Cierre")
    print("10. Gestión de Clientes")
    print("11. Salir")
    print("-" * 40)
    return input("Seleccione una opción: ")


def menu_gestion_usuarios():
    print("\n--- GESTIÓN DE PERSONAL ---")
    print("1. Crear Usuario")
    print("2. Listar Usuarios")
    print("3. Eliminar Usuario")
    print("4. Modificar Permisos")
    print("5. Editar Datos Usuario")
    print("6. Volver")
    return input("Opción: ")


def menu_gestion_clientes():
    print("\n--- GESTIÓN DE CLIENTES ---")
    print("(Funcionalidad en construcción para CLI)")
    input("Enter para volver...")


def menu_reportes():
    print("\n--- REPORTES ---")
    print("1. Historial de Ventas")
    print("2. Cierre de Caja (Z)")
    print("3. Volver")
    return input("Opción: ")
