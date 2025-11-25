#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para normalizar nombres de autores
Elimina abreviaturas de títulos, puntuación innecesaria, etc.
"""

import re
import csv

INPUT_FILE = "autores_unicos_pre_IA.txt"
OUTPUT_FILE = "autores_unicos_post_IA.tsv"

# Títulos y abreviaturas comunes a eliminar
TITULOS_ELIMINAR = [
    r'\bM\.\s*r\b',           # M. r (Monsieur)
    r'\bP\.\b',               # P. (Padre)
    r'\bD\.\s*n\b',           # D. n (Don)
    r'\bD\.\s*ª\b',           # D.ª (Doña)
    r'\bD\.\b',               # D. (Don)
    r'\bFr\.\b',              # Fr. (Fray)
    r'\bSt\.\b',              # St. (Santo/Saint)
    r'\bS\.\b',               # S. (San)
    r'\bR\.\s*P\.\b',         # R. P. (Reverendo Padre)
    r'\bDr\.\b',              # Dr. (Doctor)
    r'\bMr\.\b',              # Mr. (Mister)
    r'\bSr\.\b',              # Sr. (Señor)
    r'\bSra\.\b',             # Sra. (Señora)
    r'\bB\.\b',               # B. (Beato)
    r'\bV\.\b',               # V. (Venerable)
    r'\bPrincipe\b',          # Príncipe
    r'\bPrincesa\b',          # Princesa
    r'\bRey\b',               # Rey
    r'\bReyna\b',             # Reyna
    r'\bCardenal\b',          # Cardenal
    r'\bObispo\b',            # Obispo
    r'\bArzobispo\b',         # Arzobispo
    r'\bConde\b',             # Conde
    r'\bDuque\b',             # Duque
    r'\bMarques\b',           # Marques
    r'\bBarón\b',             # Barón
]

def normalizar_autor(autor_original):
    """
    Normaliza un nombre de autor eliminando títulos y abreviaturas
    """
    autor = autor_original.strip()

    # Si está vacío, retornar tal cual
    if not autor:
        return autor

    # Eliminar títulos y abreviaturas comunes
    for titulo in TITULOS_ELIMINAR:
        autor = re.sub(titulo, '', autor, flags=re.IGNORECASE)

    # Eliminar abreviaturas restantes sin punto (D, P, Fr) al inicio de paréntesis
    autor = re.sub(r'\(\s*D\s+', '(', autor)
    autor = re.sub(r'\(\s*P\s+', '(', autor)
    autor = re.sub(r'\(\s*Fr\s+', '(', autor)

    # Eliminar puntos sueltos después de eliminar abreviaturas
    autor = re.sub(r'\s+\.', '', autor)
    autor = re.sub(r'\.\s+', ' ', autor)

    # Eliminar puntos múltiples (...) y reducir a uno solo
    autor = re.sub(r'\.{2,}', '', autor)

    # Normalizar espacios múltiples
    autor = re.sub(r'\s+', ' ', autor)

    # Eliminar espacios antes/después de paréntesis
    autor = re.sub(r'\s*\(\s*', ' (', autor)
    autor = re.sub(r'\s*\)\s*', ') ', autor)

    # Eliminar paréntesis vacíos o con solo "de"
    autor = re.sub(r'\(\s*\)', '', autor)
    autor = re.sub(r'\(\s*de\s*\)', '', autor)

    # Limpiar espacios múltiples nuevamente
    autor = re.sub(r'\s+', ' ', autor)

    # Eliminar espacios al inicio/final
    autor = autor.strip()

    # Eliminar puntos finales innecesarios
    autor = re.sub(r'\.+$', '', autor)

    # Limpiar espacios otra vez
    autor = autor.strip()

    return autor

def main():
    """
    Función principal
    """
    print(f"Leyendo autores de: {INPUT_FILE}")

    # Leer autores
    autores_original = []
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            autores_original = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {INPUT_FILE}")
        return

    print(f"  ✓ Cargados {len(autores_original)} autores")
    print()
    print("Normalizando nombres...")

    # Normalizar autores
    autores_procesados = []
    cambios = 0

    for autor_orig in autores_original:
        autor_norm = normalizar_autor(autor_orig)
        autores_procesados.append({
            'original': autor_orig,
            'normalizado': autor_norm
        })

        if autor_orig != autor_norm:
            cambios += 1

    print(f"  ✓ Normalizados {len(autores_procesados)} autores")
    print(f"  ✓ {cambios} autores modificados ({cambios/len(autores_procesados)*100:.1f}%)")
    print()

    # Guardar resultados en TSV
    print(f"Guardando resultados en: {OUTPUT_FILE}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')

        # Escribir encabezado
        writer.writerow(['autor_original', 'autor_normalizado'])

        # Escribir datos
        for autor in autores_procesados:
            writer.writerow([autor['original'], autor['normalizado']])

    print(f"  ✓ Archivo guardado con {len(autores_procesados)} registros")
    print()

    # Mostrar ejemplos de cambios
    print("Ejemplos de normalizaciones (primeros 20 con cambios):")
    ejemplos = [a for a in autores_procesados if a['original'] != a['normalizado']][:20]

    for ejemplo in ejemplos:
        print(f"  {ejemplo['original']}")
        print(f"    → {ejemplo['normalizado']}")
        print()

if __name__ == "__main__":
    main()
