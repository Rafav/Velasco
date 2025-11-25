#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para comparar obras del catálogo con títulos encontrados en BNE
Maneja discrepancias por errores de OCR usando matching aproximado
"""

import csv
import re
from difflib import SequenceMatcher

# Archivos de entrada y salida
CATALOGO_FILE = "catalogo_depurado_v3.csv"
TITULOS_BNE_FILE = "titulos_velasco.txt"
OUTPUT_FILE = "obras_en_BNE.txt"

# Umbral de similitud (0.0 a 1.0)
SIMILARITY_THRESHOLD = 0.75

def normalize_text(text):
    """
    Normaliza texto para comparación: minúsculas, sin acentos, sin puntuación
    """
    if not text:
        return ""

    # Convertir a minúsculas
    text = text.lower()

    # Eliminar corchetes
    text = re.sub(r'[\[\]]', '', text)

    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()

    # Eliminar puntuación al final
    text = re.sub(r'[.,;:!?]+$', '', text)

    # Reemplazar algunos caracteres comunes de OCR
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u',
        'ñ': 'n', 'ç': 'c',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text

def calculate_similarity(text1, text2):
    """
    Calcula la similitud entre dos textos (0.0 a 1.0)
    """
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    if not norm1 or not norm2:
        return 0.0

    # Usar SequenceMatcher para calcular similitud
    return SequenceMatcher(None, norm1, norm2).ratio()

def find_best_match(titulo_catalogo, titulos_bne):
    """
    Encuentra la mejor coincidencia de un título del catálogo en los títulos BNE
    Retorna (titulo_bne, similitud) o (None, 0.0) si no hay match
    """
    best_match = None
    best_similarity = 0.0

    for titulo_bne in titulos_bne:
        similarity = calculate_similarity(titulo_catalogo, titulo_bne)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = titulo_bne

    if best_similarity >= SIMILARITY_THRESHOLD:
        return best_match, best_similarity
    else:
        return None, 0.0

def main():
    """
    Función principal
    """
    print("Cargando archivos...")

    # Leer títulos de BNE
    titulos_bne = []
    try:
        with open(TITULOS_BNE_FILE, 'r', encoding='utf-8') as f:
            titulos_bne = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {TITULOS_BNE_FILE}")
        return

    print(f"  ✓ Cargados {len(titulos_bne)} títulos de BNE")

    # Leer catálogo
    obras_catalogo = []
    try:
        with open(CATALOGO_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('titulo'):
                    obras_catalogo.append({
                        'autor': row.get('autor', ''),
                        'titulo': row.get('titulo', ''),
                        'año': row.get('año', ''),
                        'lugar': row.get('lugar', ''),
                        'numero': row.get('numero', ''),
                        'volumen': row.get('volumen', ''),
                        'pagina': row.get('pagina', '')
                    })
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {CATALOGO_FILE}")
        return

    print(f"  ✓ Cargadas {len(obras_catalogo)} obras del catálogo")
    print()
    print("Buscando coincidencias...")
    print()

    # Buscar coincidencias
    coincidencias = []

    for i, obra in enumerate(obras_catalogo, 1):
        if i % 100 == 0:
            print(f"  Procesadas {i}/{len(obras_catalogo)} obras...")

        titulo_match, similarity = find_best_match(obra['titulo'], titulos_bne)

        if titulo_match:
            coincidencias.append({
                'obra': obra,
                'titulo_bne': titulo_match,
                'similitud': similarity
            })

    print(f"  ✓ Completado")
    print()
    print(f"Encontradas {len(coincidencias)} coincidencias")
    print()

    # Ordenar por similitud (mayor a menor)
    coincidencias.sort(key=lambda x: x['similitud'], reverse=True)

    # Guardar resultados
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("OBRAS DEL CATÁLOGO VELASCO ENCONTRADAS EN BNE\n")
        f.write("=" * 80 + "\n")
        f.write(f"\nTotal de coincidencias: {len(coincidencias)}\n")
        f.write(f"Umbral de similitud usado: {SIMILARITY_THRESHOLD:.0%}\n")
        f.write("\n" + "=" * 80 + "\n\n")

        for i, match in enumerate(coincidencias, 1):
            obra = match['obra']
            f.write(f"{i}. CATÁLOGO: {obra['titulo']}\n")

            if obra['autor']:
                f.write(f"   Autor: {obra['autor']}\n")
            if obra['año']:
                f.write(f"   Año: {obra['año']}\n")
            if obra['lugar']:
                f.write(f"   Lugar: {obra['lugar']}\n")
            if obra['numero']:
                f.write(f"   Número catálogo: {obra['numero']}\n")
            if obra['volumen'] and obra['pagina']:
                f.write(f"   Ubicación: Volumen {obra['volumen']}, {obra['pagina']}\n")

            f.write(f"\n   BNE: {match['titulo_bne']}\n")
            f.write(f"   Similitud: {match['similitud']:.1%}\n")
            f.write("\n" + "-" * 80 + "\n\n")

    print(f"Resultados guardados en: {OUTPUT_FILE}")
    print()

    # Mostrar estadísticas
    print("Estadísticas de similitud:")
    muy_alta = sum(1 for m in coincidencias if m['similitud'] >= 0.95)
    alta = sum(1 for m in coincidencias if 0.85 <= m['similitud'] < 0.95)
    media = sum(1 for m in coincidencias if 0.75 <= m['similitud'] < 0.85)

    print(f"  Muy alta (≥95%): {muy_alta}")
    print(f"  Alta (85-95%): {alta}")
    print(f"  Media (75-85%): {media}")
    print()

    # Mostrar primeras 5 coincidencias
    print("Primeras 5 coincidencias:")
    for i, match in enumerate(coincidencias[:5], 1):
        print(f"\n{i}. {match['obra']['titulo'][:60]}...")
        print(f"   → {match['titulo_bne'][:60]}...")
        print(f"   Similitud: {match['similitud']:.1%}")

if __name__ == "__main__":
    main()
