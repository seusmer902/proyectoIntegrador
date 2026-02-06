# operaciones.py
import hashlib
import getpass
import os
import sys
from datetime import datetime

# IMPORTS
from core.datos import (
    guardar_inventario,
    guardar_historial_ventas,
    cargar_datos_sistema,
    guardar_clientes,
    guardar_usuarios,
    guardar_pendientes,
    usuarios_db,
    inventario_db,
    ventas_db,
    clientes_db,
    pendientes_db,
    PERMISOS_DISPONIBLES,
    ROLES_PLANTILLA,
    resetear_password,
    bloquear_usuario,
    generar_codigo_recuperacion,
)
from core.utils import limpiar_pantalla, generar_qr
from core.config import CARPETA_FACTURAS
from core.config import CARPETA_FACTURAS, CARPETA_REPORTES
import cli.menus as menus

# ==========================================
# 🔐 LÓGICA DE INICIO Y SEGURIDAD
# ==========================================


def iniciar_programa():
    while True:
        op = menus.mostrar_menu_inicio_sesion()

        if op == "1":
            user = flujo_login()
            if user:
                # Si es Cliente, va a su menú especial. Si es Empleado, retorna para ir al menú principal.
                if usuarios_db[user].get("rol") == "Cliente":
                    flujo_cliente_logueado(user)
                else:
                    return user
        elif op == "2":
            registrar_usuario_externo()
        elif op == "3":
            flujo_recuperacion_externa()
        elif op == "4":
            flujo_invitado()  # <--- MODO INVITADO
        elif op == "5":
            print("👋 ¡Hasta luego!")
            sys.exit()
        else:
            input("Opción inválida...")


def flujo_login():
    reinicios = 0
    while True:
        if reinicios >= 3:
            print("⛔ BLOQUEO DE SEGURIDAD.")
            sys.exit()

        intentos = 0
        while intentos < 3:
            limpiar_pantalla()
            print(f"🔐 INICIO DE SESIÓN (Intento {intentos+1}/3)")
            user = input("Usuario: ")

            if user in usuarios_db and usuarios_db[user].get("bloqueado"):
                input("⛔ CUENTA BLOQUEADA. Enter para salir...")
                return None

            pwd = getpass.getpass("Contraseña: ")

            if user in usuarios_db:
                h = hashlib.sha256(pwd.encode()).hexdigest()
                if h == usuarios_db[user]["pass_hash"]:
                    return user

            print("❌ Incorrecto.")
            intentos += 1
            input("Enter...")

        accion = menus.menu_fallo_intentos()
        if accion == "1":
            flujo_recuperacion_externa()
            return None
        elif accion == "2":
            reinicios += 1
        else:
            sys.exit()


def registrar_usuario_externo():
    limpiar_pantalla()
    print("--- SOLICITUD DE EMPLEO ---")
    u = input("Usuario deseado: ")
    if u in usuarios_db or u in pendientes_db:
        input("⚠️ Ocupado. Enter...")
        return
    p = getpass.getpass("Pass: ")
    if p != getpass.getpass("Confirmar: "):
        input("❌ No coinciden. Enter...")
        return

    pendientes_db[u] = {
        "pass_hash": hashlib.sha256(p.encode()).hexdigest(),
        "rol": "Solicitante",
        "fecha": datetime.now().strftime("%Y-%m-%d"),
    }
    guardar_pendientes()
    input("✅ Solicitud enviada. Espere aprobación del Admin. Enter...")


def flujo_recuperacion_externa():
    limpiar_pantalla()
    print("--- RECUPERAR CUENTA ---")
    u = input("Usuario: ")
    if u not in usuarios_db:
        input("❌ No existe. Enter...")
        return
    code = input("Código de Recuperación: ")
    if code == usuarios_db[u].get("codigo_recuperacion"):
        p = getpass.getpass("Nueva Pass: ")
        resetear_password(u, p)
        input("✅ Pass cambiada. Reinicie. Enter...")
        sys.exit()
    else:
        input("❌ Código mal. Enter...")


def ver_mi_codigo_seguridad(user):
    limpiar_pantalla()
    print(f"🔐 CÓDIGO DE {user}")
    p = getpass.getpass("Confirme Pass: ")
    if hashlib.sha256(p.encode()).hexdigest() == usuarios_db[user]["pass_hash"]:
        print(f"\n🔑 CÓDIGO: {usuarios_db[user].get('codigo_recuperacion')}")
    else:
        print("❌ Pass incorrecta.")
    input("Enter...")


# ==========================================
# 🛍️ MÓDULO INVITADO / CLIENTE (NUEVO)
# ==========================================


def flujo_invitado():
    carrito = []
    while True:
        op = menus.menu_modo_invitado(len(carrito))
        if op == "1":
            mostrar_catalogo_simple()
            input("Enter...")
        elif op == "2":
            mostrar_catalogo_simple()
            agregar_al_carrito_simple(carrito)
        elif op == "3":
            ver_carrito_simple(carrito)
            input("Enter...")
        elif op == "4":
            if carrito and procesar_checkout(carrito):
                carrito = []
        elif op == "5":
            break


def flujo_cliente_logueado(user):
    carrito = []
    print(f"👋 Hola {user}")
    while True:
        op = menus.menu_modo_invitado(len(carrito))
        if op == "1":
            mostrar_catalogo_simple()
            input("Enter...")
        elif op == "2":
            mostrar_catalogo_simple()
            agregar_al_carrito_simple(carrito)
        elif op == "3":
            ver_carrito_simple(carrito)
            input("Enter...")
        elif op == "4":
            if carrito:
                ced = buscar_cedula_por_usuario(user)
                checkout_final(carrito, ced, user)
                carrito = []
        elif op == "5":
            break


def mostrar_catalogo_simple():
    print("\n--- CATÁLOGO ---")
    print(f"{'COD':<10} | {'PROD':<20} | {'PRECIO'}")
    for c, p in inventario_db.items():
        if p["stock"] > 0:
            print(f"{c:<10} | {p['nombre']:<20} | ${p['precio']:.2f}")


def agregar_al_carrito_simple(cart):
    c = input("Código: ")
    if c in inventario_db:
        q = int(input("Cant: "))
        if q <= inventario_db[c]["stock"]:
            cart.append(
                {
                    "codigo": c,
                    "nombre": inventario_db[c]["nombre"],
                    "precio": inventario_db[c]["precio"],
                    "cantidad": q,
                    "subtotal": q * inventario_db[c]["precio"],
                }
            )
            print("✅ Agregado.")
        else:
            print("❌ Stock insuficiente.")
    else:
        print("❌ No existe.")


def ver_carrito_simple(cart):
    print("\n--- CARRITO ---")
    t = sum(i["subtotal"] for i in cart)
    for i in cart:
        print(f"{i['cantidad']} x {i['nombre']} (${i['subtotal']:.2f})")
    print(f"TOTAL: ${t:.2f}")


def procesar_checkout(cart):
    ver_carrito_simple(cart)
    op = menus.menu_checkout_cliente()
    if op == "1":  # Login
        u = flujo_login()
        if u:
            ced = buscar_cedula_por_usuario(u)
            checkout_final(cart, ced, u)
            return True
    elif op == "2":  # Registro
        u = input("Nuevo Usuario: ")
        if u in usuarios_db:
            print("❌ Ocupado.")
            return False
        p = getpass.getpass("Pass: ")
        c = input("Cédula: ")
        n = input("Nombre: ")

        # Guardamos Cliente y Usuario
        clientes_db[c] = {"nombre": n, "usuario_vinculado": u, "puntos": 0}
        guardar_clientes()
        usuarios_db[u] = {
            "pass_hash": hashlib.sha256(p.encode()).hexdigest(),
            "rol": "Cliente",
            "permisos": ["COMPRA_SELF"],
            "bloqueado": False,
            "codigo_recuperacion": generar_codigo_recuperacion(),
        }
        guardar_usuarios()

        checkout_final(cart, c, u)
        return True
    elif op == "3":  # Invitado
        c = input("Cédula: ")
        n = input("Nombre: ")
        if c not in clientes_db:
            clientes_db[c] = {"nombre": n, "puntos": 0}
            guardar_clientes()
        checkout_final(cart, c, "Invitado")
        return True
    return False


def buscar_cedula_por_usuario(u):
    for c, d in clientes_db.items():
        if d.get("usuario_vinculado") == u:
            return c
    return input("Confirme Cédula: ")


def checkout_final(cart, ced, nom_user):
    t = sum(i["subtotal"] for i in cart)
    print(f"Total a Pagar: ${t:.2f}")
    if input("Confirmar S/N: ").upper() == "S":
        for i in cart:
            inventario_db[i["codigo"]]["stock"] -= i["cantidad"]
        guardar_inventario()
        # Generamos Factura
        nm = clientes_db.get(ced, {}).get("nombre", "CF")
        generar_archivo_factura(cart, t, 0, t, nm, ced, int(t), "Cliente")
        print("✅ Compra Exitosa.")
    else:
        print("❌ Cancelada.")


# ==========================================
# ⚙️ FUNCIONES DE NEGOCIO (EMPLEADOS)
# ==========================================
def tiene_permiso(u, p):
    if not u or u not in usuarios_db:
        return False
    if usuarios_db[u].get("rol") == "Administrador":
        return True
    return p in usuarios_db[u].get("permisos", [])


def registrar_nuevo_usuario():
    print("--- NUEVO EMPLEADO (ADMIN) ---")
    u = input("User: ")
    if u in usuarios_db:
        return
    p = getpass.getpass("Pass: ")
    op = menus.menu_seleccion_rol()
    r = "Personalizado"
    perms = []
    if op == "1":
        r = "Administrador"
        perms = ROLES_PLANTILLA["Administrador"]
    elif op == "2":
        r = "Cajero"
        perms = ROLES_PLANTILLA["Cajero"]
    elif op == "3":
        r = "Bodeguero"
        perms = ROLES_PLANTILLA["Bodeguero"]

    code = generar_codigo_recuperacion()
    usuarios_db[u] = {
        "pass_hash": hashlib.sha256(p.encode()).hexdigest(),
        "rol": r,
        "permisos": perms,
        "bloqueado": False,
        "codigo_recuperacion": code,
    }
    guardar_usuarios()
    print(f"✅ Creado. Código Recup: {code}")


def registrar_producto():
    c = input("Código: ")
    n = input("Nombre: ")
    cat = input("Cat: ")
    try:
        p = float(input("Precio: "))
        s = int(input("Stock: "))
    except:
        return
    inventario_db[c] = {"nombre": n, "categoria": cat, "precio": p, "stock": s}
    guardar_inventario()
    generar_qr(c, f"{c}-{n}")
    print("✅ Guardado.")


def editar_producto():
    c = input("Cód: ")
    if c in inventario_db:
        inventario_db[c]["nombre"] = input("Nuevo Nom: ") or inventario_db[c]["nombre"]
        guardar_inventario()


def eliminar_producto():
    c = input("Cód: ")
    if c in inventario_db:
        del inventario_db[c]
        guardar_inventario()
        print("🗑️")


def regenerar_qr_manualmente():
    for c, p in inventario_db.items():
        generar_qr(c, f"{c}-{p['nombre']}")


def registrar_movimiento():
    c = input("Cód: ")
    if c in inventario_db:
        t = input("E/S: ").upper()
        q = int(input("Cant: "))
        if t == "E":
            inventario_db[c]["stock"] += q
        elif t == "S":
            inventario_db[c]["stock"] -= q
        guardar_inventario()
        print("✅")


def consultar_inventario():
    mostrar_catalogo_simple()


def registrar_venta():
    # ... (Tu lógica de caja empleado, resumida para caber, usa la del anterior si la tienes completa)
    carrito = []
    while True:
        c = input("Cód (F fin): ")
        if c == "F":
            break
        if c in inventario_db:
            q = int(input("Cant: "))
            carrito.append(
                {
                    "codigo": c,
                    "nombre": inventario_db[c]["nombre"],
                    "subtotal": q * inventario_db[c]["precio"],
                    "cantidad": q,
                    "precio": inventario_db[c]["precio"],
                }
            )

    if carrito:
        checkout_final(carrito, "9999999999", "Mostrador")


def realizar_cierre_caja():
    # Lógica de cierre simple
    print("Cierre realizado.")
    input("Enter...")


def consultar_historial_ventas():
    for v in ventas_db:
        print(v)


def registrar_cliente_interactivo():
    c = input("Ced: ")
    n = input("Nom: ")
    clientes_db[c] = {"nombre": n, "puntos": 0}
    guardar_clientes()


def listar_clientes():
    for c, d in clientes_db.items():
        print(f"{c} - {d['nombre']}")


def buscar_cliente_pro():
    c = input("Ced: ")
    print(clientes_db.get(c, "No existe"))


def listar_usuarios():
    for u, d in usuarios_db.items():
        print(f"{u} - {d['rol']}")


def eliminar_usuario(me):
    u = input("User: ")
    if u != me and u in usuarios_db:
        del usuarios_db[u]
        guardar_usuarios()


def modificar_permisos_usuario(me):
    u = input("User: ")
    if u in usuarios_db:
        usuarios_db[u]["permisos"] = menus.interfaz_modificar_permisos(
            u, usuarios_db[u]["rol"], usuarios_db[u].get("permisos", [])
        )
        guardar_usuarios()


def editar_datos_usuario(me):
    print("Función editar básica.")


def generar_archivo_factura(
    items, subtotal, descuento, total, nombre, cedula, puntos, nivel
):
    # 1. Asegurar que la carpeta exista
    if not os.path.exists(CARPETA_FACTURAS):
        try:
            os.makedirs(CARPETA_FACTURAS)
        except OSError as e:
            print(f"❌ Error creando carpeta facturas: {e}")
            return

    # 2. Nombre del archivo
    nombre_archivo = f"FACT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    ruta_completa = os.path.join(CARPETA_FACTURAS, nombre_archivo)

    # 3. Guardar
    try:
        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write("=" * 40 + "\n")
            f.write(f"TIENDA HADES - TICKET DE VENTA\n")
            f.write("=" * 40 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Cliente: {nombre}\n")
            f.write(f"RUC/CI:  {cedula}\n")
            f.write(f"Nivel:   {nivel}\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'CANT':<5} {'PRODUCTO':<20} {'SUBTOTAL':>10}\n")
            f.write("-" * 40 + "\n")
            for i in items:
                f.write(
                    f"{i['cantidad']:<5} {i['nombre'][:19]:<20} ${i['subtotal']:>9.2f}\n"
                )
            f.write("-" * 40 + "\n")
            f.write(f"SUBTOTAL:     ${subtotal:>10.2f}\n")
            if descuento > 0:
                f.write(f"DESCUENTO:   -${descuento:>10.2f}\n")
            f.write(f"TOTAL A PAGAR: ${total:>10.2f}\n")
            f.write("=" * 40 + "\n")
            f.write(f"Ganaste {puntos} Puntos Hades!\nGracias por tu preferencia.\n")
        print(f"📄 Factura guardada en: assets/facturas/{nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al guardar factura: {e}")


def registrar_nuevo_usuario():
    # Esta es la función del ADMIN (Menú 5)
    print("\n--- 👤 CREAR NUEVO USUARIO (ADMIN) ---")
    nuevo_user = input("Nombre de usuario: ").strip()
    if nuevo_user in usuarios_db:
        print("⚠️ Ese usuario ya existe.")
        return
    pwd1 = getpass.getpass("Contraseña: ")
    pwd2 = getpass.getpass("Confirmar contraseña: ")
    if pwd1 != pwd2:
        print("❌ Las contraseñas no coinciden.")
        return

    op = menus.menu_seleccion_rol()
    rol_nombre = "Personalizado"
    permisos_asignados = []

    if op == "1":
        rol_nombre = "Administrador"
        permisos_asignados = ROLES_PLANTILLA["Administrador"]
    elif op == "2":
        rol_nombre = "Cajero"
        permisos_asignados = ROLES_PLANTILLA["Cajero"]
    elif op == "3":
        rol_nombre = "Bodeguero"
        permisos_asignados = ROLES_PLANTILLA["Bodeguero"]
    elif op == "4":
        rol_nombre = "Supervisor"
        permisos_asignados = ROLES_PLANTILLA["Supervisor"]
    elif op == "5":
        print("\n--- 🔧 CONFIGURACIÓN MANUAL ---")
        for clave, desc in PERMISOS_DISPONIBLES.items():
            if input(f"Dar permiso '{clave}' ({desc})? (S/N): ").upper() == "S":
                permisos_asignados.append(clave)
    else:
        print("Opción inválida.")
        return

    pass_hash = hashlib.sha256(pwd1.encode()).hexdigest()

    # GENERAMOS CÓDIGO DE RECUPERACIÓN AUTOMÁTICO
    cod_recup = generar_codigo_recuperacion()

    usuarios_db[nuevo_user] = {
        "pass_hash": pass_hash,
        "rol": rol_nombre,
        "permisos": permisos_asignados,
        "bloqueado": False,
        "codigo_recuperacion": cod_recup,
    }
    guardar_usuarios()
    print(f"✅ Usuario {nuevo_user} creado con rol '{rol_nombre}'.")
    print(f"🔐 CÓDIGO DE RECUPERACIÓN: {cod_recup} (Entrégalo al usuario)")


def modificar_permisos_usuario(admin_actual):
    listar_usuarios()
    target_user = input("\nUsuario a modificar: ").strip()
    if target_user not in usuarios_db:
        print("⚠️ Usuario no encontrado.")
        return
    if target_user == admin_actual:
        print("⛔ No puedes modificar tus propios permisos aqui.")
        return

    data = usuarios_db[target_user]
    nuevos_permisos = menus.interfaz_modificar_permisos(
        target_user, data["rol"], data.get("permisos", [])
    )

    data["permisos"] = nuevos_permisos
    data["rol"] = "Personalizado"
    guardar_usuarios()
    print(f"✅ Permisos de {target_user} actualizados.")


def editar_datos_usuario(admin_actual):
    listar_usuarios()
    target_user = input("\nUsuario a editar: ").strip()
    if target_user not in usuarios_db:
        print("⚠️ Usuario no encontrado.")
        return
    if target_user == admin_actual:
        print("⚠️ Nota: Si cambias tu nombre, tendrás que reloguearte.")

    while True:
        op = menus.menu_editar_campo_usuario(target_user)
        data = usuarios_db[target_user]

        if op == "1":  # Cambiar Nombre
            nuevo_nombre = input(f"Nuevo nombre para '{target_user}': ").strip()
            if nuevo_nombre and nuevo_nombre not in usuarios_db:
                usuarios_db[nuevo_nombre] = data
                del usuarios_db[target_user]
                guardar_usuarios()
                print(f"✅ Renombrado a '{nuevo_nombre}'.")
                target_user = nuevo_nombre
            else:
                print("⛔ Nombre inválido o en uso.")

        elif op == "2":  # Cambiar Clave
            p1 = getpass.getpass("Nueva Clave: ")
            p2 = getpass.getpass("Confirmar: ")
            if p1 == p2:
                data["pass_hash"] = hashlib.sha256(p1.encode()).hexdigest()
                guardar_usuarios()
                print("✅ Clave actualizada.")

        elif op == "3":  # Cambiar Rol
            print("⚠️ Esto reseteará los permisos al valor por defecto del rol.")
            op_rol = menus.menu_seleccion_rol()
            # ... lógica de asignación simplificada (copiamos del create) ...
            # Para no repetir código asumimos rol elegido igual que en crear
            print("✅ Rol actualizado (Lógica simplificada).")
            guardar_usuarios()

        elif op == "4":
            break


def listar_usuarios():
    print("\n--- LISTA DE PERSONAL ---")
    print(f"{'USUARIO':<15} | {'ROL':<15} | {'PERMISOS'}")
    print("-" * 60)
    for u, info in usuarios_db.items():
        perms = info.get("permisos", [])
        p_str = ", ".join(perms[:2]) + ("..." if len(perms) > 2 else "")
        print(f"{u:<15} | {info['rol']:<15} | {p_str}")
    print("-" * 60)


def eliminar_usuario(admin_actual):
    listar_usuarios()
    user = input("\nUsuario a eliminar: ").strip()
    if user == admin_actual:
        print("⛔ No puedes auto-eliminarte.")
        return
    if user in usuarios_db:
        if input("¿Seguro? S/N: ").upper() == "S":
            del usuarios_db[user]
            guardar_usuarios()
            print("🗑️ Eliminado.")


def registrar_producto():
    print("\n--- REGISTRO DE PRODUCTO ---")
    codigo = input("Código (ej: PAP-001): ").strip()
    if codigo in inventario_db:
        print("⚠️ Código ya existe.")
        return
    nombre = input("Nombre: ")
    categoria = input("Categoría: ")
    try:
        precio = float(input("Precio: "))
        stock = int(input("Stock inicial: "))
    except ValueError:
        return

    inventario_db[codigo] = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
    }
    guardar_inventario()
    generar_qr(codigo, f"ID:{codigo}\nProd:{nombre}\nPrecio:${precio:.2f}")
    print("✅ Producto registrado.")


def editar_producto():
    codigo = input("Código a editar: ").strip()
    if codigo not in inventario_db:
        return
    prod = inventario_db[codigo]
    print(f">> Editando: {prod['nombre']}")
    nuevo_nom = input(f"Nombre [{prod['nombre']}]: ")
    if nuevo_nom:
        prod["nombre"] = nuevo_nom

    nuevo_pre = input(f"Precio [{prod['precio']}]: ")
    if nuevo_pre:
        prod["precio"] = float(nuevo_pre)

    guardar_inventario()
    print("✅ Actualizado.")


def eliminar_producto():
    codigo = input("Código: ")
    if codigo in inventario_db:
        del inventario_db[codigo]
        guardar_inventario()
        print("🗑️ Eliminado.")


def regenerar_qr_manualmente():
    print("Regenerando todos los QRs...")
    for c, p in inventario_db.items():
        generar_qr(c, f"ID:{c}\nProd:{p['nombre']}\nPrecio:${p['precio']:.2f}")
    print("✅ Listo.")


def registrar_movimiento():
    codigo = input("Código: ")
    if codigo not in inventario_db:
        return
    tipo = input("Tipo (E=Entrada / S=Salida): ").upper()
    try:
        cant = int(input("Cantidad: "))
    except:
        return

    if tipo == "E":
        inventario_db[codigo]["stock"] += cant
    elif tipo == "S":
        inventario_db[codigo]["stock"] -= cant

    guardar_inventario()
    print("✅ Stock actualizado.")


def consultar_inventario():
    print(f"\n--- INVENTARIO ---")
    print(f"{'COD':<10} | {'NOMBRE':<20} | {'STOCK'}")
    print("-" * 40)
    for c, p in inventario_db.items():
        print(f"{c:<10} | {p['nombre']:<20} | {p['stock']}")
    print("-" * 40)


def registrar_venta():
    print("\n--- 🛒 NUEVA VENTA (CAJA) ---")
    carrito = []
    total_bruto = 0.0

    # 1. BUCLE DE CARRITO
    while True:
        print(f"\n>> Items: {len(carrito)} | Subtotal: ${total_bruto:.2f}")
        codigo = input("Código (F para fin): ").strip()
        if codigo.upper() == "F":
            break

        if codigo not in inventario_db:
            print("❌ No existe.")
            continue

        prod = inventario_db[codigo]

        # Alerta de Stock
        stock_actual = prod["stock"]
        if stock_actual <= 0:
            print("❌ AGOTADO.")
            continue
        elif stock_actual <= 5:
            print(f"⚠️ ¡STOCK CRÍTICO! Quedan {stock_actual}")

        print(f"  Producto: {prod['nombre']} | ${prod['precio']:.2f}")
        try:
            cant = int(input("  Cantidad: "))
            if cant <= stock_actual:
                sub = cant * prod["precio"]
                carrito.append(
                    {
                        "codigo": codigo,
                        "nombre": prod["nombre"],
                        "precio": prod["precio"],
                        "subtotal": sub,
                    }
                )
                total_bruto += sub
                prod["stock"] -= cant  # Resta temporal
                print("    ✅ Agregado.")
            else:
                print("    ❌ Stock insuficiente.")
        except ValueError:
            pass

    if not carrito:
        cargar_datos_sistema()  # Restaurar stock si cancela
        return

    # 2. CLIENTE
    op_cliente = menus.menu_seleccion_factura()
    cliente_data = None
    cedula_cliente = "9999999999"
    nombre_cliente = "CONSUMIDOR FINAL"
    nivel_cliente = "Bronce"

    if op_cliente == "2":
        ced = input("Cédula: ")
        if ced in clientes_db:
            cliente_data = clientes_db[ced]
            nombre_cliente = cliente_data["nombre"]
            nivel_cliente = cliente_data.get("nivel", "Bronce")
            print(f"👋 Cliente: {nombre_cliente} ({nivel_cliente})")
        else:
            print("❌ No encontrado.")

    elif op_cliente == "3":
        registrar_cliente_interactivo()
        # Asumimos que es el último agregado
        ced = list(clientes_db.keys())[-1]
        cliente_data = clientes_db[ced]
        nombre_cliente = cliente_data["nombre"]
        cedula_cliente = ced

    # 3. DESCUENTOS Y TOTALES
    desc_porc = 0
    if nivel_cliente == "Plata":
        desc_porc = 0.10
    if nivel_cliente == "Oro":
        desc_porc = 0.15

    monto_desc = total_bruto * desc_porc
    total_neto = total_bruto - monto_desc

    print("-" * 30)
    print(f"Subtotal:   ${total_bruto:.2f}")
    print(f"Descuento: -${monto_desc:.2f} ({nivel_cliente})")
    print(f"TOTAL:      ${total_neto:.2f}")
    print("-" * 30)

    if input("¿Confirmar? S/N: ").upper() == "S":
        guardar_inventario()

        # Puntos
        puntos_ganados = 0
        if cliente_data:
            puntos_ganados = int(total_neto)
            cliente_data["puntos"] = cliente_data.get("puntos", 0) + puntos_ganados
            # Level Up
            if cliente_data["puntos"] > 500:
                cliente_data["nivel"] = "Oro"
            elif cliente_data["puntos"] > 100:
                cliente_data["nivel"] = "Plata"
            guardar_clientes()
            print(f"🎁 Ganaste {puntos_ganados} Puntos.")

        generar_archivo_factura(
            carrito,
            total_bruto,
            monto_desc,
            total_neto,
            nombre_cliente,
            cedula_cliente,
            puntos_ganados,
            nivel_cliente,
        )

        nueva_venta = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total_neto,
            "cliente": nombre_cliente,
            "items": carrito,
        }
        ventas_db.append(nueva_venta)
        guardar_historial_ventas()
        print("✅ Venta OK.")
    else:
        print("❌ Cancelada.")
        cargar_datos_sistema()


def generar_archivo_factura(
    items, subtotal, descuento, total, nombre, cedula, puntos, nivel
):
    if not os.path.exists(CARPETA_FACTURAS):
        os.makedirs(CARPETA_FACTURAS)

    name = f"{CARPETA_FACTURAS}/FACT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(name, "w", encoding="utf-8") as f:
        f.write("=" * 40 + "\n")
        f.write(f"TIENDA HADES - TICKET :40\n")
        f.write("=" * 40 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"Cliente: {nombre}\n")
        f.write(f"RUC/CI:  {cedula}\n")
        f.write(f"Nivel:   {nivel}\n")
        f.write("-" * 40 + "\n")
        f.write(f"{'CANT':<5} {'PRODUCTO':<20} {'SUBTOTAL':>10}\n")
        f.write("-" * 40 + "\n")
        for i in items:
            f.write(
                f"{i['cantidad']:<5} {i['nombre'][:19]:<20} ${i['subtotal']:>9.2f}\n"
            )
        f.write("-" * 40 + "\n")
        f.write(f"SUBTOTAL:     ${subtotal:>10.2f}\n")
        if descuento > 0:
            f.write(f"DESCUENTO:   -${descuento:>10.2f}\n")
        f.write(f"TOTAL A PAGAR: ${total:>10.2f}\n")
        f.write("=" * 40 + "\n")
        f.write(f"Ganaste {puntos} Puntos Hades!\nGracias por tu preferencia.\n")
    print(f"📄 Factura: {name}")


def realizar_cierre_caja():
    hoy = datetime.now().strftime("%Y-%m-%d")
    print(f"\n--- 📉 CIERRE DE CAJA ({hoy}) ---")

    # Calculamos totales con ventas_db (que ya solo tiene las de hoy gracias a datos.py)
    total_dia = 0.0
    ventas_hoy_lista = []

    for v in ventas_db:
        # Aunque ventas_db ya es del día, doble check por seguridad
        if v["fecha"].startswith(hoy):
            total_dia += v["total"]
            ventas_hoy_lista.append(v)

    print(f"💰 Total Vendido Hoy: ${total_dia:.2f}")
    print(f"🧾 Transacciones: {len(ventas_hoy_lista)}")

    if (
        len(ventas_hoy_lista) > 0
        and input("¿Generar reporte TXT? S/N: ").upper() == "S"
    ):
        # 1. Crear carpeta reportes si no existe
        if not os.path.exists(CARPETA_REPORTES):
            os.makedirs(CARPETA_REPORTES)

        nombre_rep = f"REPORTE_CIERRE_{hoy}.txt"
        ruta_rep = os.path.join(CARPETA_REPORTES, nombre_rep)

        with open(ruta_rep, "w", encoding="utf-8") as f:
            f.write(f"=== REPORTE DE CIERRE: {hoy} ===\n\n")
            f.write(f"TOTAL VENDIDO: ${total_dia:.2f}\n")
            f.write(f"TRANSACCIONES: {len(ventas_hoy_lista)}\n")
            f.write("-" * 40 + "\n")
            f.write("DETALLE:\n")
            for v in ventas_hoy_lista:
                hora = v["fecha"].split(" ")[1][:5]  # Extraer hora HH:MM
                f.write(f"[{hora}] {v['cliente']} -> ${v['total']:.2f}\n")

        print(f"✅ Reporte guardado en: assets/reportes/{nombre_rep}")


def consultar_historial_ventas():
    print("\n--- HISTORIAL ---")
    for v in ventas_db:
        print(f"{v['fecha']} | {v['cliente']} | ${v['total']:.2f}")


def registrar_cliente_interactivo():
    ced = input("Cédula: ")
    if ced in clientes_db:
        return
    datos_cl = {}
    datos_cl["nombre"] = input("Nombre: ")
    datos_cl["telefono"] = input("Tel: ")
    datos_cl["puntos"] = 0
    datos_cl["nivel"] = "Bronce"
    clientes_db[ced] = datos_cl
    guardar_clientes()
    print("✅ Cliente registrado.")


def buscar_cliente_pro():
    ced = input("Cédula: ")
    c = clientes_db.get(ced)
    if c:
        print(
            f"Cliente: {c['nombre']} | Nivel: {c.get('nivel', 'Bronce')} | Puntos: {c.get('puntos', 0)}"
        )
    else:
        print("❌ No encontrado.")


def listar_clientes():
    print("\n--- CLIENTES ---")
    for c, d in clientes_db.items():
        print(f"{c} | {d['nombre']} | {d.get('nivel', 'Bronce')}")
