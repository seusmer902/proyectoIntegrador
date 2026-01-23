# utils.py
import os
import platform
import qrcode
from .config import CARPETA_QR  # Importamos desde la misma carpeta core


def limpiar_pantalla():
    sistema = platform.system()
    if sistema == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def generar_qr(codigo, info):
    if not os.path.exists(CARPETA_QR):
        os.makedirs(CARPETA_QR)

    qr = qrcode.make(info)
    ruta_imagen = os.path.join(CARPETA_QR, f"{codigo}.png")
    qr.save(ruta_imagen)
    print(f"✅ QR generado en: {ruta_imagen}")
