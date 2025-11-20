import os
import json
import time
from pathlib import Path

import dashscope

# === CONFIGURACIÓN ===
CARPETA_IMAGENES = "/home/rafa/Descargas/Velasco/a_jpg_afinado"
CARPETA_SALIDA = "salida_ocr"
ARCHIVO_PROGRESO = "progreso.json"

# Crear carpeta de salida
Path(CARPETA_SALIDA).mkdir(exist_ok=True)

# Configurar región (Singapur, como en tu ejemplo)
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

# Cargar progreso
if os.path.exists(ARCHIVO_PROGRESO):
    with open(ARCHIVO_PROGRESO, "r") as f:
        progreso = set(json.load(f))
else:
    progreso = set()

# Listar y ordenar imágenes: pagina_0001.jpg, pagina_0002.jpg, etc.
carpeta = Path(CARPETA_IMAGENES)
if not carpeta.exists():
    raise FileNotFoundError(f"La carpeta de imágenes no existe: {CARPETA_IMAGENES}")

archivos = sorted(
    carpeta.glob("pagina_*.jpg"),
    key=lambda x: int(x.stem.split("_")[1])
)

print(f"Encontradas {len(archivos)} imágenes. Iniciando procesamiento...")

for archivo in archivos:
    nombre = archivo.stem  # Ej: pagina_0010
    if nombre in progreso:
        print(f"⏭️  Saltando {nombre} (ya procesado)")
        continue

    print(f"🖼️  Procesando {nombre}...")

    image_path = f"file://{archivo.absolute()}"

    messages = [
        {
            "role": "user",
            "content": [
                {"image": image_path, "min_pixels": 65536, "max_pixels": 28 * 28 * 8192},
                {
                    "text": "ocr a json. Es un inventario de catálogo de autores, libros, datos , precios, y sumas Respeta el castellano y latín. mantén los datos de precios y números, también los de páginas"
                },
            ],
        }
    ]

    try:
        response = dashscope.MultiModalConversation.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen3-vl-plus",
            messages=messages,
        )

        # === Guardar respuesta completa de forma segura ===
        ruta_full = Path(CARPETA_SALIDA) / f"{nombre}.full_response.json"
        try:
            if hasattr(response, 'to_dict'):
                resp_data = response.to_dict()
            else:
                # Fallback manual si to_dict no existe
                resp_data = {
                    "status_code": getattr(response, 'status_code', None),
                    "output": getattr(response, 'output', None),
                    "usage": getattr(response, 'usage', None),
                    "request_id": getattr(response, 'request_id', None),
                    "headers": getattr(response, 'headers', None),
                    "raw_repr": repr(response)
                }
        except Exception as e_ser:
            resp_data = {
                "error_al_serializar": str(e_ser),
                "tipo_de_respuesta": str(type(response)),
                "repr": repr(response)
            }

        with open(ruta_full, "w", encoding="utf-8") as f_full:
            json.dump(resp_data, f_full, ensure_ascii=False, indent=2)
        print(response)

        # === Extraer OCR si la llamada fue exitosa ===
        if getattr(response, 'status_code', None) == 200:
            try:
                texto_ocr = response["output"]["choices"][0]["message"]["content"][0]["text"]
                resultado = {"pagina": nombre, "ocr": texto_ocr}
                ruta_ocr = Path(CARPETA_SALIDA) / f"{nombre}.json"
                with open(ruta_ocr, "w", encoding="utf-8") as f_ocr:
                    json.dump(resultado, f_ocr, ensure_ascii=False, indent=2)
                print(f"✅ {nombre} procesado con éxito")
            except (KeyError, IndexError, TypeError) as e_ocr:
                print(f"⚠️  OCR no disponible en {nombre}: {e_ocr}")
                with open("errores.log", "a", encoding="utf-8") as err_log:
                    err_log.write(f"{nombre}: OCR parsing failed - {e_ocr}\n")
        else:
            print(f"❌ Error en API para {nombre}: status={getattr(response, 'status_code', 'unknown')}")
            with open("errores.log", "a", encoding="utf-8") as err_log:
                err_log.write(f"{nombre}: API error - status={getattr(response, 'status_code', 'unknown')}\n")

    except Exception as e_call:
        print(f"💥 Excepción crítica en {nombre}: {e_call}")
        # Guardar error en archivo de respuesta completa
        ruta_full = Path(CARPETA_SALIDA) / f"{nombre}.full_response.json"
        with open(ruta_full, "w", encoding="utf-8") as f_full:
            json.dump({
                "error": str(e_call),
                "pagina": nombre,
                "timestamp": time.time(),
                "tipo_error": str(type(e_call))
            }, f_full, ensure_ascii=False, indent=2)
        with open("errores.log", "a", encoding="utf-8") as err_log:
            err_log.write(f"{nombre}: Exception - {e_call}\n")
        continue  # No marcar como completado

    # Marcar como procesado (solo si llegamos aquí)
    progreso.add(nombre)
    with open(ARCHIVO_PROGRESO, "w") as f:
        json.dump(list(progreso), f)

    time.sleep(0.5)  # Evitar límites de tasa (opcional, ajusta según necesites)

print("🎉 Procesamiento finalizado.")