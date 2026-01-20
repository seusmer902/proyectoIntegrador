from utils import limpiar_pantalla
import operaciones as ops


def mostrar_menu_principal(rol):
    limpiar_pantalla()
    print("=" * 40)
    print(f"   SISTEMA HADES - TERMINAL (V-1.6.1)")
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
    print("9. Gestión de Clientes 👥")
    print("\n10. Salir")

    return input("\n>> Seleccione opción: ")


def menu_gestion_clientes():
    while True:
        limpiar_pantalla()
        print("--- 👥 GESTIÓN DE CLIENTES ---")
        print("1. Registrar Cliente")
        print("2. Listar Clientes")
        print("3. Buscar Cliente (Detalles)")  # Opción creativa
        print("4. Volver")
        op = input("\n>> Seleccione: ")

        if op == "1":
            ops.registrar_cliente_interactivo()
        elif op == "2":
            ops.listar_clientes()
        elif op == "3":
            ops.buscar_cliente()
        elif op == "4":
            break

        input("\nPresione [ENTER] para continuar...")
