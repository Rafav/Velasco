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
    # Eliminar controles y normalizar espacios
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
            # Valor primitivo
            valores.append(limpiar_valor(v))

    recorrer(objeto)
    return ' '.join(valores)

def procesar_archivo(ruta):
    items = []
    nombre_archivo = ruta.name
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Si no es JSON válido, intentar buscar JSON dentro (como en logs)
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        # Buscar bloques JSON
        matches = re.findall(r'\{(?:[^{}]|(?R))*\}', contenido, re.DOTALL)
        if not matches:
            print(f"⚠️  No se encontró JSON válido en {nombre_archivo}")
            return []
        data = None
        for m in matches:
            try:
                data = json.loads(m)
                break
            except:
                continue
        if data is None:
            print(f"⚠️  Imposible parsear JSON en {nombre_archivo}")
            return []

    # Buscar arrays de objetos
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
        # Si no hay array conocido, tratar el JSON completo como un solo objeto
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
        items.append({
            'filename': nombre_archivo,
            'fila': i,
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
        writer = csv.DictWriter(f, fieldnames=['filename', 'fila', 'transcripcion'])
        writer.writeheader()
        writer.writerows(todos_items)

    print(f"\n✅ Generado: {salida.absolute()}")
    print(f"   {len(todos_items)} filas escritas.")

if __name__ == '__main__':
    main()
