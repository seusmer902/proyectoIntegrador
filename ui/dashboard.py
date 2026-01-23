import customtkinter as ctk
from tkinter import messagebox
from core import datos

# Configuración Visual Global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class HadesApp(ctk.CTk):
    def __init__(self, usuario_actual, rol_actual):
        super().__init__()

        self.title(f"HADES POS V-2.0 | Usuario: {usuario_actual} ({rol_actual})")
        self.geometry("1100x650")
        self.usuario = usuario_actual
        self.rol = rol_actual

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # MENÚ LATERAL
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            self.sidebar_frame,
            text="SISTEMA\nHADES 🔥",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10))

        ctk.CTkButton(
            self.sidebar_frame, text="🛒 Caja / Ventas", command=self.mostrar_ventas
        ).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(
            self.sidebar_frame, text="📦 Inventario", command=self.mostrar_inventario
        ).grid(row=2, column=0, padx=20, pady=10)

        if self.rol == "Administrador":
            ctk.CTkButton(
                self.sidebar_frame,
                text="👮 Usuarios",
                fg_color="#B22222",
                command=lambda: print("Admin Panel"),
            ).grid(row=5, column=0, padx=20, pady=10)

        ctk.CTkButton(
            self.sidebar_frame,
            text="Cerrar Sesión",
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=self.cerrar_sesion,
        ).grid(row=8, column=0, padx=20, pady=(50, 20))

        # ÁREA PRINCIPAL
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.mostrar_ventas()  # Pantalla por defecto

    def limpiar_panel(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def cerrar_sesion(self):
        if messagebox.askyesno("Salir", "¿Desea cerrar sesión?"):
            self.destroy()

    # --- MÓDULO INVENTARIO ---
    def mostrar_inventario(self):
        self.limpiar_panel()

        # Barra superior
        frame_top = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame_top.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(frame_top, text="📦 INVENTARIO", font=("Arial", 24, "bold")).pack(
            side="left"
        )
        ctk.CTkButton(
            frame_top,
            text="+ Nuevo",
            fg_color="#2CC985",
            command=self.evento_nuevo_producto,
        ).pack(side="right", padx=5)

        # Tabla
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame)
        scroll_frame.pack(fill="both", expand=True)

        headers = ["CÓDIGO", "NOMBRE", "PRECIO", "STOCK", "ACCIONES"]
        for i, col in enumerate(headers):
            ctk.CTkLabel(scroll_frame, text=col, font=("Arial", 12, "bold")).grid(
                row=0, column=i, padx=10, sticky="w"
            )

        row = 1
        for codigo, prod in datos.inventario_db.items():
            color = "white"
            if prod["stock"] <= 5:
                color = "#FF5555"

            ctk.CTkLabel(scroll_frame, text=codigo).grid(
                row=row, column=0, padx=10, sticky="w"
            )
            ctk.CTkLabel(scroll_frame, text=prod["nombre"]).grid(
                row=row, column=1, padx=10, sticky="w"
            )
            ctk.CTkLabel(scroll_frame, text=f"${prod['precio']}").grid(
                row=row, column=2, padx=10, sticky="w"
            )
            ctk.CTkLabel(scroll_frame, text=str(prod["stock"]), text_color=color).grid(
                row=row, column=3, padx=10, sticky="w"
            )

            ctk.CTkButton(
                scroll_frame,
                text="🗑️",
                width=30,
                fg_color="#FF5555",
                command=lambda c=codigo: self.evento_eliminar(c),
            ).grid(row=row, column=4, padx=10)
            row += 1

    def evento_nuevo_producto(self):
        win = ctk.CTkToplevel(self)
        win.geometry("300x300")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="Código:").pack()
        e_cod = ctk.CTkEntry(win)
        e_cod.pack()
        ctk.CTkLabel(win, text="Nombre:").pack()
        e_nom = ctk.CTkEntry(win)
        e_nom.pack()
        ctk.CTkLabel(win, text="Precio:").pack()
        e_pre = ctk.CTkEntry(win)
        e_pre.pack()
        ctk.CTkLabel(win, text="Stock:").pack()
        e_stk = ctk.CTkEntry(win)
        e_stk.pack()

        def guardar():
            c, n, p, s = e_cod.get().upper(), e_nom.get(), e_pre.get(), e_stk.get()
            datos.inventario_db[c] = {
                "nombre": n,
                "categoria": "Gen",
                "precio": float(p),
                "stock": int(s),
            }
            datos.guardar_inventario()
            win.destroy()
            self.mostrar_inventario()

        ctk.CTkButton(win, text="Guardar", command=guardar).pack(pady=20)

    def evento_eliminar(self, cod):
        if messagebox.askyesno("Borrar", "¿Seguro?"):
            del datos.inventario_db[cod]
            datos.guardar_inventario()
            self.mostrar_inventario()

    # --- MÓDULO VENTAS ---
    def mostrar_ventas(self):
        self.limpiar_panel()
        self.carrito = []

        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # El carrito expande

        # Buscador
        frame_bus = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame_bus.grid(row=0, column=0, sticky="ew", padx=10)
        self.entry_bus = ctk.CTkEntry(
            frame_bus, width=300, placeholder_text="Código..."
        )
        self.entry_bus.pack(side="left")
        self.entry_bus.bind("<Return>", self.add_carrito)
        ctk.CTkButton(
            frame_bus, text="Agregar", width=100, command=lambda: self.add_carrito(None)
        ).pack(side="left", padx=10)

        # Encabezados
        frame_head = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame_head.grid(row=1, column=0, sticky="ew", padx=10)
        ctk.CTkLabel(frame_head, text="PRODUCTO", width=250, anchor="w").grid(
            row=0, column=0
        )
        ctk.CTkLabel(frame_head, text="PRECIO", width=80).grid(row=0, column=1)
        ctk.CTkLabel(frame_head, text="TOTAL", width=80).grid(row=0, column=2)

        # Tabla Carrito
        self.scroll_cart = ctk.CTkScrollableFrame(self.main_frame)
        self.scroll_cart.grid(row=2, column=0, sticky="nsew", padx=10)

        # Panel Total
        frame_tot = ctk.CTkFrame(self.main_frame)
        frame_tot.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=10)
        ctk.CTkLabel(frame_tot, text="TOTAL", font=("Arial", 20)).pack(pady=20)
        self.lbl_total = ctk.CTkLabel(
            frame_tot, text="$0.00", font=("Arial", 40, "bold"), text_color="#2CC985"
        )
        self.lbl_total.pack()

    def add_carrito(self, event):
        cod = self.entry_bus.get().upper().strip()
        self.entry_bus.delete(0, "end")
        if cod in datos.inventario_db:
            prod = datos.inventario_db[cod]
            self.carrito.append(prod)
            self.pintar_carrito()
        else:
            messagebox.showerror("Error", "No existe")

    def pintar_carrito(self):
        for w in self.scroll_cart.winfo_children():
            w.destroy()
        total = 0
        for i, prod in enumerate(self.carrito):
            ctk.CTkLabel(
                self.scroll_cart, text=prod["nombre"], width=250, anchor="w"
            ).grid(row=i, column=0)
            ctk.CTkLabel(self.scroll_cart, text=f"${prod['precio']}", width=80).grid(
                row=i, column=1
            )
            total += prod["precio"]

        self.lbl_total.configure(text=f"${total:.2f}")
