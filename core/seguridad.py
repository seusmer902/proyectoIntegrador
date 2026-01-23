# seguridad.py
import hashlib
import json
import os


class ModuloSeguridad:

    def __init__(self, archivo_db="usuarios.json"):
        self.archivo_db = archivo_db
        self.MAX_INTENTOS = 3
        # Cargar la base de datos desde el archivo al iniciar
        self.usuarios_db = self._cargar_datos()

    def _cargar_datos(self):
        """Lee el archivo JSON. Si no existe, retorna diccionario vacío."""
        if not os.path.exists(self.archivo_db):
            print(f"Advertencia: No se encontró {self.archivo_db}. Iniciando vacío.")
            return {}
        try:
            with open(self.archivo_db, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _guardar_datos(self):
        """Escribe los cambios (bloqueos, nuevos pass) en el JSON."""
        with open(self.archivo_db, "w", encoding="utf-8") as f:
            json.dump(self.usuarios_db, f, indent=4)

    def _generar_hash(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, usuario, password):
        # 1. Validar existencia del usuario
        if usuario not in self.usuarios_db:
            return False, "Usuario incorrecto.", None

        user_data = self.usuarios_db[usuario]

        # --- AUTO-CORRECCIÓN DEL JSON ---
        # Si tu JSON antiguo no tiene estos campos, los creamos al vuelo
        if "intentos" not in user_data:
            user_data["intentos"] = 0
        if "bloqueado" not in user_data:
            user_data["bloqueado"] = False
        # --------------------------------

        # 2. Verificar si YA está bloqueado antes de comprobar nada
        if user_data["bloqueado"]:
            return False, "❌ CUENTA BLOQUEADA. Contacte al Admin.", None

        # 3. Verificar Contraseña
        hash_input = self._generar_hash(password)

        if user_data.get("pass_hash") == hash_input:
            # --- ÉXITO ---
            user_data["intentos"] = 0  # Reseteamos contador
            self._guardar_datos()  # GUARDAR (Importante)
            return True, f"Bienvenido {usuario}", user_data["rol"]

        else:
            # --- FALLO ---
            user_data["intentos"] += 1  # Aumentamos contador

            # Calculamos cuántos le quedan
            restantes = self.MAX_INTENTOS - user_data["intentos"]

            # Verificamos si debemos bloquear
            if user_data["intentos"] >= self.MAX_INTENTOS:
                user_data["bloqueado"] = True
                msg = "🚫 HAS EXCEDIDO LOS INTENTOS. CUENTA BLOQUEADA."
            else:
                msg = f"⚠️ Contraseña incorrecta. Te quedan {restantes} intentos."

            self._guardar_datos()  # GUARDAR INMEDIATAMENTE EL FALLO/BLOQUEO
            return False, msg, None

    def recuperar_contrasena(self, usuario, pin_seguridad, nueva_password):
        if usuario not in self.usuarios_db:
            return False, "Usuario no encontrado."

        user_data = self.usuarios_db[usuario]

        # Validar PIN (asumiendo que existe en el JSON, si no, falla)
        pin_real = user_data.get("pin_recuperacion")

        if pin_real == pin_seguridad:
            # Actualizar contraseña y desbloquear
            user_data["pass_hash"] = self._generar_hash(nueva_password)
            user_data["intentos"] = 0
            user_data["bloqueado"] = False

            self._guardar_datos()  # <--- GUARDAMOS LA NUEVA CONTRASEÑA
            return True, "Cuenta recuperada exitosamente."
        else:
            return False, "PIN incorrecto o no configurado."


# --- EJEMPLO DE USO RÁPIDO ---
if __name__ == "__main__":
    seg = ModuloSeguridad("usuarios.json")

    # Prueba intentando entrar como 'admin' (pass: admin123)
    # O como 'Manuel' (pass: user123, según los hashes comunes)

    usuario = input("Usuario: ")
    password = input("Contraseña: ")

    exito, msg, rol = seg.login(usuario, password)
    print(msg)

    if exito:
        # Aquí podrías acceder a los permisos que mostraste en la imagen
        permisos = seg.usuarios_db[usuario].get("permisos", [])
        print(f"Tus permisos son: {permisos}")
