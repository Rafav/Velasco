#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script optimizado para comparar obras del catálogo con títulos encontrados en BNE
Maneja discrepancias por errores de OCR usando matching aproximado
"""

import csv
import re
from difflib import SequenceMatcher
from collections import defaultdict

# Archivos de entrada y salida
CATALOGO_FILE = "catalogo_depurado_v3.csv"
TITULOS_BNE_FILE = "titulos_velasco.txt"
OUTPUT_FILE = "obras_en_BNE.txt"

# Umbral de similitud (0.0 a 1.0)
SIMILARITY_THRESHOLD = 0.50  # Bajado a 50% para incluir más coincidencias con errores de OCR

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

def extract_keywords(text, num_keywords=3):
    """
    Extrae palabras clave significativas de un texto (omite palabras comunes)
    """
    # Palabras a ignorar
    stop_words = {
        'de', 'la', 'el', 'los', 'las', 'del', 'y', 'en', 'a', 'al',
        'para', 'por', 'con', 'un', 'una', 'su', 'que', 'sobre',
        'des', 'le', 'les', 'du', 'et', 'un', 'une', 'au', 'aux',
        'the', 'of', 'and', 'in', 'to', 'a', 'an', 'for'
    }

    normalized = normalize_text(text)
    words = normalized.split()

    # Filtrar palabras cortas y stop words
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]

    return keywords[:num_keywords]

def build_index(titulos):
    """
    Construye un índice de títulos por palabras clave para búsqueda rápida
    """
    index = defaultdict(list)

    for i, titulo in enumerate(titulos):
        keywords = extract_keywords(titulo)
        for keyword in keywords:
            # Indexar por prefijo de palabra (primeros 4 caracteres)
            if len(keyword) >= 4:
                prefix = keyword[:4]
                index[prefix].append(i)

    return index

def find_candidates(titulo, titulos_bne, index):
    """
    Encuentra candidatos potenciales usando el índice
    """
    keywords = extract_keywords(titulo)
    candidate_indices = set()

    for keyword in keywords:
        if len(keyword) >= 4:
            prefix = keyword[:4]
            if prefix in index:
                candidate_indices.update(index[prefix])

    # Si no hay suficientes candidatos, buscar con prefijos más cortos
    if len(candidate_indices) < 50 and keywords:
        for keyword in keywords:
            if len(keyword) >= 3:
                prefix = keyword[:3]
                for key in index:
                    if key.startswith(prefix):
                        candidate_indices.update(index[key])

    # Si aún no hay candidatos suficientes, usar todos (último recurso)
    if len(candidate_indices) < 20:
        candidate_indices = set(range(len(titulos_bne)))

    return [titulos_bne[i] for i in candidate_indices]

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

def find_best_match(titulo_catalogo, titulos_bne, index):
    """
    Encuentra la mejor coincidencia de un título del catálogo en los títulos BNE
    Retorna (titulo_bne, similitud) o (None, 0.0) si no hay match
    """
    # Primero, obtener candidatos usando el índice
    candidates = find_candidates(titulo_catalogo, titulos_bne, index)

    best_match = None
    best_similarity = 0.0

    # Solo comparar con candidatos
    for titulo_bne in candidates:
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

    # Construir índice para búsqueda rápida
    print("  Construyendo índice de búsqueda...")
    index = build_index(titulos_bne)
    print(f"  ✓ Índice construido con {len(index)} entradas")

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
    print("Buscando coincidencias (optimizado con índice)...")
    print()

    # Buscar coincidencias
    coincidencias = []

    for i, obra in enumerate(obras_catalogo, 1):
        if i % 500 == 0:
            print(f"  Procesadas {i}/{len(obras_catalogo)} obras... ({len(coincidencias)} coincidencias encontradas)")

        titulo_match, similarity = find_best_match(obra['titulo'], titulos_bne, index)

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
    media = sum(1 for m in coincidencias if 0.70 <= m['similitud'] < 0.85)
    baja = sum(1 for m in coincidencias if 0.50 <= m['similitud'] < 0.70)

    print(f"  Muy alta (≥95%): {muy_alta}")
    print(f"  Alta (85-95%): {alta}")
    print(f"  Media (70-85%): {media}")
    print(f"  Baja (50-70%): {baja}")
    print()

    # Mostrar primeras 10 coincidencias
    print("Primeras 10 coincidencias:")
    for i, match in enumerate(coincidencias[:10], 1):
        print(f"\n{i}. {match['obra']['titulo'][:70]}...")
        print(f"   → {match['titulo_bne'][:70]}...")
        print(f"   Similitud: {match['similitud']:.1%}")

if __name__ == "__main__":
    main()
