from datos import cargar_datos_sistema
import operaciones as ops
import menus


def ejecutar_sistema():
    cargar_datos_sistema()
    rol = ops.login()

    while True:
        op = menus.mostrar_menu_principal(rol)

        if op in ["1", "2", "3", "4"]:
            if rol == "Administrador":
                if op == "1":
                    ops.registrar_producto()
                elif op == "2":
                    ops.editar_producto()
                elif op == "3":
                    ops.eliminar_producto()
                elif op == "4":
                    ops.regenerar_qr_manualmente()
            else:
                print("⛔ Acceso denegado (Requiere Admin).")

        elif op == "5":
            ops.registrar_movimiento()
        elif op == "6":
            ops.consultar_inventario()
        elif op == "7":
            ops.registrar_venta()
        elif op == "8":
            ops.consultar_historial_ventas()
        elif op == "9":
            menus.menu_gestion_clientes()
        elif op == "10":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("⚠️ Opción no válida.")

        print("\n" + "-" * 40)
        input("Presione [ENTER] para continuar...")


if __name__ == "__main__":
    ejecutar_sistema()
