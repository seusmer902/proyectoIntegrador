from core import datos
import cli.operaciones as ops
import cli.menus as menus

USUARIO_ACTUAL = None


def ejecutar_sistema():
    global USUARIO_ACTUAL
    datos.cargar_datos_sistema()
    USUARIO_ACTUAL = ops.login()

    while True:
        rol = datos.usuarios_db[USUARIO_ACTUAL]["rol"]
        op = menus.mostrar_menu_principal(USUARIO_ACTUAL, rol)

        if op == "1":
            ops.registrar_producto()
        elif op == "7":
            ops.consultar_inventario()
        elif op == "5":
            ops.listar_usuarios()
        elif op == "11":
            break
        else:
            input("Opción en construcción para CLI. Enter...")


if __name__ == "__main__":
    ejecutar_sistema()
