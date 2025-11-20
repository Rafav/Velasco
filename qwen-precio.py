#!/usr/bin/env python3
import json
import csv
import sys
from pathlib import Path
import re

def limpiar_valor(val):
    """Limpieza básica para que no rompa CSV ni sea ilegible."""
    if val is None:
        return ''
    s = str(val)
    # Eliminar caracteres de control y normalizar espacios
    s = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def extraer_valores(objeto):
    """
    Extrae recursivamente todos los valores primitivos (str, int, float, bool)
    de un objeto JSON, ignorando claves y estructura.
    """
    valores = []

    def recorrer(v):
        if isinstance(v, dict):
            for subv in v.values():
                recorrer(subv)
        elif isinstance(v, list):
            for item in v:
                recorrer(item)
        else:
            valores.append(limpiar_valor(v))

    recorrer(objeto)
    return ' '.join(valores)

def extraer_precio(objeto):
    """
    Busca recursivamente claves relacionadas con precios: 'price', 'precio', 'prices', 'precios'.
    Devuelve el primer valor numérico válido encontrado (como float), o None si no se encuentra.
    Intenta interpretar strings con símbolos monetarios o separadores.
    """
    claves_precio = {'price', 'precio', 'prices', 'precios'}

    def buscar_en(v):
        if isinstance(v, dict):
            for k, val in v.items():
                if k.lower() in claves_precio:
                    # Procesar este valor como candidato a precio
                    if isinstance(val, (int, float)):
                        return float(val)
                    elif isinstance(val, str):
                        # Limpiar símbolos comunes: $, €, £, espacios, etc.
                        limpio = re.sub(r'[^\d.,-]', '', val)
                        if not limpio:
                            pass
                        elif ',' in limpio and '.' in limpio:
                            # Caso ambiguo: asumir formato europeo si la coma está al final
                            if limpio.index(',') > limpio.index('.'):
                                # Ej: 1.000,50 → 1000.50
                                limpio = limpio.replace('.', '').replace(',', '.')
                            else:
                                # Ej: 1,000.50 → ya es válido en inglés
                                pass
                        elif ',' in limpio:
                            # Podría ser decimal (100,50) o miles (1,000)
                            partes = limpio.split(',')
                            if len(partes) == 2 and len(partes[1]) <= 3:
                                # Asumir decimal
                                limpio = limpio.replace(',', '.')
                            # Si no, dejar como está (puede ser entero con separador de miles)
                        # Intentar convertir
                        try:
                            return float(limpio)
                        except ValueError:
                            pass
                    elif isinstance(val, list) and val:
                        # Tomar el primer elemento de la lista
                        primer = val[0]
                        if isinstance(primer, (int, float)):
                            return float(primer)
                        elif isinstance(primer, str):
                            limpio = re.sub(r'[^\d.,-]', '', primer)
                            if ',' in limpio and '.' in limpio:
                                if limpio.index(',') > limpio.index('.'):
                                    limpio = limpio.replace('.', '').replace(',', '.')
                            elif ',' in limpio:
                                partes = limpio.split(',')
                                if len(partes) == 2 and len(partes[1]) <= 3:
                                    limpio = limpio.replace(',', '.')
                            try:
                                return float(limpio)
                            except ValueError:
                                pass
                    # Si no se pudo usar este valor, seguimos buscando en profundidad
                # Buscar en el valor recursivamente
                resultado = buscar_en(val)
                if resultado is not None:
                    return resultado
        elif isinstance(v, list):
            for item in v:
                resultado = buscar_en(item)
                if resultado is not None:
                    return resultado
        return None

    return buscar_en(objeto)

def encontrar_jsons_en_texto(texto):
    """Encuentra bloques JSON válidos en un texto (útil para logs o archivos mal formateados)."""
    resultados = []
    i = 0
    n = len(texto)
    while i < n:
        if texto[i] == '{':
            contador = 1
            inicio = i
            i += 1
            while i < n and contador > 0:
                if texto[i] == '{':
                    contador += 1
                elif texto[i] == '}':
                    contador -= 1
                i += 1
            if contador == 0:
                candidato = texto[inicio:i]
                try:
                    obj = json.loads(candidato)
                    resultados.append(obj)
                except json.JSONDecodeError:
                    pass  # no es JSON válido, ignorar
            # no incrementar i aquí porque ya avanzó en el bucle
        else:
            i += 1
    return resultados

def procesar_archivo(ruta):
    items = []
    nombre_archivo = ruta.name
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Intentar extraer JSONs desde texto (logs, etc.)
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        jsons_encontrados = encontrar_jsons_en_texto(contenido)
        if not jsons_encontrados:
            print(f"⚠️  No se encontró JSON válido en {nombre_archivo}")
            return []
        data = jsons_encontrados[0]  # usar el primer JSON válido

    # Buscar arrays comunes
    arrays_posibles = [
        'inventario', 'entries', 'inventory_entries', 'catalog_entries',
        'entradas', 'contenido', 'items', 'content'
    ]

    objetos = []
    for arr in arrays_posibles:
        if arr in data and isinstance(data[arr], list):
            objetos = data[arr]
            break
    else:
        # Si no hay array conocido, tratar como objeto único o lista
        if isinstance(data, dict):
            objetos = [data]
        elif isinstance(data, list):
            objetos = data
        else:
            objetos = []

    for i, obj in enumerate(objetos, 1):
        if not isinstance(obj, dict):
            continue
        transcripcion = extraer_valores(obj)
        precio = extraer_precio(obj)
        items.append({
            'filename': nombre_archivo,
            'fila': i,
            'price': precio,
            'transcripcion': transcripcion
        })
    return items

def main():
    if len(sys.argv) != 2:
        print("Uso: python json_a_csv_simple.py <directorio_json>")
        sys.exit(1)

    dir_path = Path(sys.argv[1])
    if not dir_path.is_dir():
        print(f"❌ No es un directorio: {dir_path}")
        sys.exit(1)

    archivos = list(dir_path.glob('*.json'))
    if not archivos:
        print(f"❌ No hay archivos .json en {dir_path}")
        sys.exit(1)

    todos_items = []
    for arch in sorted(archivos):
        print(f"Procesando: {arch.name}")
        items = procesar_archivo(arch)
        todos_items.extend(items)

    if not todos_items:
        print("❌ No se extrajeron datos.")
        sys.exit(1)

    salida = Path('output_simple.csv')
    with open(salida, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'fila', 'transcripcion' ,'price'])
        writer.writeheader()
        writer.writerows(todos_items)

    print(f"\n✅ Generado: {salida.absolute()}")
    print(f"   {len(todos_items)} filas escritas.")

if __name__ == '__main__':
    main()