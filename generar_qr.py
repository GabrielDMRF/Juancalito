#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Código QR para Asistencia
Crea un código QR que apunte al servidor de Railway
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def generar_qr_asistencia():
    """Generar código QR para el sistema de asistencia"""
    
    # URL del servidor de Railway
    url_servidor = "https://juancalito-production.up.railway.app"
    
    print("🎯 Generando código QR para asistencia...")
    print(f"📱 URL: {url_servidor}")
    
    # Crear código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Agregar datos al QR
    qr.add_data(url_servidor)
    qr.make(fit=True)
    
    # Crear imagen del QR
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Crear imagen con información adicional
    img_width = qr_image.width
    img_height = qr_image.height + 100  # Espacio extra para texto
    
    # Crear imagen final
    final_image = Image.new('RGB', (img_width, img_height), 'white')
    final_image.paste(qr_image, (0, 0))
    
    # Agregar texto
    draw = ImageDraw.Draw(final_image)
    
    # Intentar usar una fuente más grande
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
    
    # Texto del título
    titulo = "Sistema de Asistencia QR"
    titulo_bbox = draw.textbbox((0, 0), titulo, font=font)
    titulo_width = titulo_bbox[2] - titulo_bbox[0]
    titulo_x = (img_width - titulo_width) // 2
    draw.text((titulo_x, img_height - 80), titulo, fill='black', font=font)
    
    # Texto de instrucciones
    instrucciones = "Escanea con tu móvil para registrar asistencia"
    try:
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        try:
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
        except:
            font_small = ImageFont.load_default()
    
    instrucciones_bbox = draw.textbbox((0, 0), instrucciones, font=font_small)
    instrucciones_width = instrucciones_bbox[2] - instrucciones_bbox[0]
    instrucciones_x = (img_width - instrucciones_width) // 2
    draw.text((instrucciones_x, img_height - 50), instrucciones, fill='gray', font=font_small)
    
    # Guardar imagen
    filename = "qr_asistencia.png"
    final_image.save(filename)
    
    print(f"✅ Código QR generado: {filename}")
    print(f"📏 Tamaño: {img_width}x{img_height} píxeles")
    print(f"📱 Los empleados pueden escanear este QR con sus móviles")
    print(f"🌐 Se abrirá: {url_servidor}")
    
    return filename

def generar_qr_con_logo():
    """Generar código QR con logo de la empresa (versión premium)"""
    
    url_servidor = "https://juancalito-production.up.railway.app"
    
    print("🎨 Generando código QR premium con logo...")
    
    # Crear código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Mayor corrección de errores
        box_size=10,
        border=4,
    )
    
    qr.add_data(url_servidor)
    qr.make(fit=True)
    
    # Crear imagen del QR
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a RGBA para poder agregar logo
    qr_image = qr_image.convert('RGBA')
    
    # Crear imagen final más grande
    img_width = qr_image.width + 100
    img_height = qr_image.height + 150
    
    final_image = Image.new('RGB', (img_width, img_height), 'white')
    
    # Centrar el QR
    qr_x = (img_width - qr_image.width) // 2
    qr_y = 50
    final_image.paste(qr_image, (qr_x, qr_y), qr_image)
    
    # Agregar texto
    draw = ImageDraw.Draw(final_image)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_subtitle = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
    
    # Título principal
    titulo = "Sistema de Asistencia QR"
    titulo_bbox = draw.textbbox((0, 0), titulo, font=font_title)
    titulo_width = titulo_bbox[2] - titulo_bbox[0]
    titulo_x = (img_width - titulo_width) // 2
    draw.text((titulo_x, 20), titulo, fill='black', font=font_title)
    
    # Subtítulo
    subtitulo = "Flore Juncalito"
    subtitulo_bbox = draw.textbbox((0, 0), subtitulo, font=font_subtitle)
    subtitulo_width = subtitulo_bbox[2] - subtitulo_bbox[0]
    subtitulo_x = (img_width - subtitulo_width) // 2
    draw.text((subtitulo_x, img_height - 80), subtitulo, fill='darkblue', font=font_subtitle)
    
    # Instrucciones
    instrucciones = "Escanea con tu móvil para registrar entrada/salida"
    instrucciones_bbox = draw.textbbox((0, 0), instrucciones, font=font_subtitle)
    instrucciones_width = instrucciones_bbox[2] - instrucciones_bbox[0]
    instrucciones_x = (img_width - instrucciones_width) // 2
    draw.text((instrucciones_x, img_height - 50), instrucciones, fill='gray', font=font_subtitle)
    
    # Guardar imagen
    filename = "qr_asistencia_premium.png"
    final_image.save(filename)
    
    print(f"✅ Código QR premium generado: {filename}")
    print(f"📏 Tamaño: {img_width}x{img_height} píxeles")
    
    return filename

if __name__ == "__main__":
    print("🚀 GENERADOR DE CÓDIGO QR PARA ASISTENCIA")
    print("=" * 50)
    
    # Generar ambas versiones
    qr_basico = generar_qr_asistencia()
    qr_premium = generar_qr_con_logo()
    
    print("\n🎯 CÓDIGOS QR GENERADOS:")
    print(f"📱 Básico: {qr_basico}")
    print(f"🎨 Premium: {qr_premium}")
    print("\n💡 INSTRUCCIONES:")
    print("1. Imprime el código QR que prefieras")
    print("2. Colócalo en un lugar visible")
    print("3. Los empleados escanearán con sus móviles")
    print("4. Se abrirá el formulario de asistencia")
    print("5. Podrán registrar entrada o salida")
    
    print(f"\n🌐 URL del servidor: https://juancalito-production.up.railway.app")
    print("✅ ¡Sistema listo para usar!")
