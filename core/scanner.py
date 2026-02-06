import os
import json
from . import config


def correr_scanner_hades():
    print("\n" + "=" * 40)
    print("🔍 INICIANDO HADES HEALTH CHECK...")
    print("=" * 40)

    errores = 0
    advertencias = 0

    # 1. Verificar Carpetas Críticas
    carpetas = [
        config.DB_DIR,
        config.ASSETS_DIR,
        config.DIR_VENTAS_DIARIAS,
        config.CARPETA_FACTURAS,
        config.CARPETA_REPORTES,
        config.CARPETA_QR,
    ]

    for c in carpetas:
        if not os.path.exists(c):
            print(f"⚠️ [AVISO]: Creando carpeta faltante -> {os.path.basename(c)}")
            os.makedirs(c)
            advertencias += 1
        else:
            print(f"✅ [OK]: Carpeta {os.path.basename(c)} detectada.")

    # 2. Verificar Archivos de Base de Datos
    archivos = {
        "Inventario": config.ARCHIVO_DATOS,
        "Empleados": config.ARCHIVO_EMPLEADOS,
        "Clientes Digitales": config.ARCHIVO_CLIENTES_LOGIN,
        "Pendientes": config.ARCHIVO_PENDIENTES,
    }

    for nombre, ruta in archivos.items():
        if not os.path.exists(ruta):
            print(f"❌ [ERROR]: Falta archivo crítico -> {nombre}")
            errores += 1
        else:
            # Prueba de lectura (Verificar que no esté corrupto el JSON)
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    json.load(f)
                print(f"✅ [OK]: Archivo {nombre} íntegro.")
            except:
                print(f"🔥 [CRÍTICO]: Archivo {nombre} CORRUPTO.")
                errores += 1

    print("=" * 40)
    if errores > 0:
        print(f"🚨 ESCANEO FINALIZADO: {errores} errores críticos encontrados.")
        print("El sistema podría fallar. Revise los archivos JSON.")
    else:
        print(f"✨ SISTEMA SALUDABLE: {advertencias} ajustes menores realizados.")
    print("=" * 40 + "\n")

    return errores == 0  # Retorna True si puede continuar
