import customtkinter as ctk
from tkinter import messagebox, simpledialog
import hashlib
from core import datos
from core.config import CLAVE_MAESTRA  # Importamos la llave


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Acceso HADES V-2.0")
        self.geometry("400x550")  # Un poco más alto para el botón extra
        self.resizable(False, False)

        self.usuario_logueado = None
        self.rol_logueado = None
        self.exito = False

        frame = ctk.CTkFrame(self)
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🔐", font=("Arial", 60)).pack(pady=(20, 10))
        ctk.CTkLabel(frame, text="INICIAR SESIÓN", font=("Arial", 20, "bold")).pack(
            pady=10
        )

        self.user_entry = ctk.CTkEntry(frame, placeholder_text="Usuario", width=250)
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(
            frame, placeholder_text="Contraseña", show="*", width=250
        )
        self.pass_entry.pack(pady=10)
        self.pass_entry.bind("<Return>", self.intentar_login)

        ctk.CTkButton(
            frame,
            text="INGRESAR",
            width=250,
            height=40,
            fg_color="#2CC985",
            hover_color="#229A65",
            command=lambda: self.intentar_login(None),
        ).pack(pady=20)

        # --- BOTÓN DE RECUPERACIÓN ---
        btn_olvido = ctk.CTkButton(
            frame,
            text="¿Olvidaste tu contraseña?",
            fg_color="transparent",
            text_color="gray70",
            hover_color="#333333",
            command=self.abrir_recuperacion,
        )
        btn_olvido.pack(pady=5)

    def intentar_login(self, event):
        user = self.user_entry.get()
        pwd = self.pass_entry.get()

        import core.datos as datos

        if user in datos.usuarios_db:
            hash_input = hashlib.sha256(pwd.encode()).hexdigest()
            if hash_input == datos.usuarios_db[user]["pass_hash"]:
                self.usuario_logueado = user
                self.rol_logueado = datos.usuarios_db[user]["rol"]
                self.exito = True
                self.destroy()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta.")
        else:
            messagebox.showerror("Error", "Usuario no encontrado.")

    def abrir_recuperacion(self):
        # 1. Pedir Llave Maestra
        llave = ctk.CTkInputDialog(
            text="Ingrese la LLAVE MAESTRA de recuperación:", title="Seguridad"
        ).get_input()

        if llave == CLAVE_MAESTRA:
            # 2. Abrir ventanita para resetear
            self.ventana_reset()
        else:
            if llave:  # Si no le dio cancelar
                messagebox.showerror("Error", "Llave Maestra Incorrecta.")

    def ventana_reset(self):
        win = ctk.CTkToplevel(self)
        win.title("Restablecer Contraseña")
        win.geometry("300x350")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="RESTAURAR ACCESO", font=("Arial", 16, "bold")).pack(
            pady=20
        )

        ctk.CTkLabel(win, text="Usuario a recuperar:").pack()
        e_user = ctk.CTkEntry(win)
        e_user.pack(pady=5)

        ctk.CTkLabel(win, text="Nueva contraseña:").pack()
        e_pass = ctk.CTkEntry(win, show="*")
        e_pass.pack(pady=5)

        def guardar_cambio():
            u = e_user.get()
            p = e_pass.get()

            if datos.resetear_password(u, p):
                messagebox.showinfo(
                    "Éxito", f"La contraseña de '{u}' ha sido cambiada."
                )
                win.destroy()
            else:
                messagebox.showerror("Error", "El usuario no existe.")

        ctk.CTkButton(
            win,
            text="Guardar Nueva Clave",
            fg_color="#E6C200",
            text_color="black",
            command=guardar_cambio,
        ).pack(pady=20)
