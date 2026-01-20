ARCHIVO_CLIENTES = "clientes.json"
ARCHIVO_DATOS = "inventario.json"
ARCHIVO_VENTAS = "ventas.json"
CARPETA_QR = "codigos_qr"

# Datos Semilla (Solo si el archivo no existe)
INVENTARIO_INICIAL = {
    "PAP-001": {
        "nombre": "Cuaderno 100h",
        "categoria": "Cuadernos",
        "precio": 1.50,
        "stock": 50,
    },
    "PAP-002": {
        "nombre": "Esfero Azul",
        "categoria": "Escritura",
        "precio": 0.60,
        "stock": 200,
    },
    "PAP-003": {
        "nombre": "Resma Papel A4",
        "categoria": "Papel",
        "precio": 4.50,
        "stock": 30,
    },
}

# SEGURIDAD: Usuarios con HASH (SHA-256)
usuarios_db = {
    "admin": {
        "pass_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",  # 123
        "rol": "Administrador",
    },
    "empleado": {
        "pass_hash": "d5f12e53a182c062b6bf30c1445153faffd2213a0b5dd168c50099164dad7406",  # E12345
        "rol": "Empleado",
    },
}
