from docx import Document
from datetime import datetime
import os

def generar_contrato_word(empleado, datos_contrato, output_folder):
    plantilla_path = "templates/contrato_base.docx"
    doc = Document(plantilla_path)

    reemplazos = {
        "{NOMBRE_EMPLEADO}": empleado.nombre_completo,
        "{CEDULA}": empleado.cedula,
        "{CARGO}": empleado.cargo or "No definido",
        "{SALARIO}": f"${empleado.salario_base:,}",
        "{AREA}": empleado.area_trabajo or "No definida",
        "{FECHA_INICIO}": datos_contrato.get("fecha_inicio", "___"),
        "{FECHA_FIN}": datos_contrato.get("fecha_fin", "___"),
        "{TIPO_CONTRATO}": datos_contrato.get("tipo_contrato", "___"),
        "{FECHA_GENERACION}": datetime.now().strftime("%d/%m/%Y"),
    }

    for p in doc.paragraphs:
        for key, value in reemplazos.items():
            if key in p.text:
                p.text = p.text.replace(key, value)

    # Guardar contrato en carpeta del empleado
    nombre_archivo = f"contrato_{empleado.cedula}.docx"
    ruta_guardado = os.path.join(output_folder, nombre_archivo)
    os.makedirs(output_folder, exist_ok=True)
    doc.save(ruta_guardado)

    return ruta_guardado
