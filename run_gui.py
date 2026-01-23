from core import datos
from ui.login import LoginWindow
from ui.dashboard import HadesApp

if __name__ == "__main__":
    print("Cargando sistema GUI...")
    datos.cargar_datos_sistema()

    while True:
        # 1. Login
        app_login = LoginWindow()
        app_login.mainloop()

        # 2. Dashboard
        if app_login.exito:
            dash = HadesApp(app_login.usuario_logueado, app_login.rol_logueado)
            dash.mainloop()
            print("Reiniciando...")
        else:
            print("Saliendo.")
            break
