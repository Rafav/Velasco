#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para extraer títulos de las páginas descargadas de BNE
Maneja correctamente HTML entities y codificación UTF-8
"""

import os
import re
import html
from pathlib import Path

INPUT_DIR = "bne_pages"
OUTPUT_FILE = "titulos_velasco.txt"

def decode_title(encoded_text):
    """
    Decodifica HTML entities y arregla problemas de UTF-8
    """
    # Primero decodificar HTML entities (&lt; -> <, &gt; -> >, etc.)
    decoded = html.unescape(encoded_text)

    # Extraer el texto entre <strong> y </strong>
    match = re.search(r'<strong>(.*?)</strong>', decoded)
    if match:
        title = match.group(1)

        # Intentar arreglar problemas de codificación UTF-8
        # (cuando bytes UTF-8 fueron interpretados como latin-1)
        try:
            # Si el texto parece tener problemas de codificación (Ã±, Ã³, etc.)
            if any(char in title for char in ['Ã', 'Â', 'Ã', 'Ã©', 'Ã­', 'Ã³', 'Ãº']):
                # Intentar re-codificar: latin-1 -> UTF-8
                title = title.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            # Si falla, mantener el título original
            pass

        return title.strip()

    return None

def extract_titles():
    """
    Extrae títulos de todos los archivos en INPUT_DIR
    """
    input_path = Path(INPUT_DIR)

    if not input_path.exists():
        print(f"Error: El directorio {INPUT_DIR} no existe")
        return

    titles = []

    # Patrón para encontrar el atributo title en los divs
    pattern = r'title="([^"]*)" class="search-item resource/"'

    # Procesar cada archivo
    page_files = sorted(input_path.glob("page_*.txt"))

    print(f"Extrayendo títulos de {len(page_files)} archivos...")
    print()

    for page_file in page_files:
        page_num = page_file.stem.replace('page_', '')
        print(f"Procesando: {page_file.name} (página {page_num})")

        try:
            # Leer el archivo
            with open(page_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Encontrar todos los atributos title
            matches = re.findall(pattern, content)

            for match in matches:
                title = decode_title(match)
                if title:
                    titles.append(title)

        except Exception as e:
            print(f"  Error procesando {page_file.name}: {e}")

    # Guardar títulos en el archivo de salida
    print()
    print(f"Guardando títulos en {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for title in titles:
            f.write(f"{title}\n")

    print()
    print(f"Extracción completada.")
    print(f"Total de títulos extraídos: {len(titles)}")
    print(f"Archivo de salida: {OUTPUT_FILE}")

    # Mostrar los primeros 10 títulos
    if titles:
        print()
        print("Primeros 10 títulos extraídos:")
        for i, title in enumerate(titles[:10], 1):
            print(f"{i}. {title}")

if __name__ == "__main__":
    extract_titles()
