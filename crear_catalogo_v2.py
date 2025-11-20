#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear catalogo_depurado_v2.csv
Corrige lugares mal parseados que quedaron en el campo título
"""

import csv
import re

# Mapeo de abreviaturas de lugares a nombres completos
LUGARES_ABREV = {
    'Mad.': 'Madrid',
    'Mad': 'Madrid',
    'Matriti': 'Madrid',
    'Salaman.': 'Salamanca',
    'Salmanticae': 'Salamanca',
    'Compluti': 'Alcalá de Henares',
    'Hispali': 'Sevilla',
    'Valentiae': 'Valencia',
    'Barcinone': 'Barcelona',
    'Caesaraugusta': 'Zaragoza',
    'Granatae': 'Granada',
    'Parisiis': 'Paris',
    'Lugduni': 'Lugduni',
    'Venetiis': 'Venecia',
    'Romae': 'Roma',
}

def extraer_lugar_del_titulo(titulo):
    """
    Busca abreviaturas de lugar al final del título
    Retorna (titulo_limpio, lugar_encontrado)
    """
    if not titulo:
        return titulo, None

    titulo = titulo.strip()

    # Buscar patrones como "texto Mad." o "texto Mad"
    for abrev, lugar in LUGARES_ABREV.items():
        # Patrón: espacio + abreviatura al final (con o sin punto)
        pattern = r'\s+' + re.escape(abrev.rstrip('.')) + r'\.?\s*$'
        match = re.search(pattern, titulo)
        if match:
            # Remover la abreviatura del título
            titulo_limpio = titulo[:match.start()].strip()
            return titulo_limpio, lugar

    return titulo, None

def corregir_catalogo():
    """Lee catalogo_depurado_v1.csv y crea catalogo_depurado_v2.csv"""

    entrada_count = 0
    corregidos = 0

    with open('/home/user/Velasco/catalogo_depurado_v1.csv', 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames

        with open('/home/user/Velasco/catalogo_depurado_v2.csv', 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                entrada_count += 1

                # Si el lugar está vacío, intentar extraerlo del título
                if not row['lugar'] or row['lugar'].strip() == '':
                    titulo_original = row['titulo']
                    titulo_limpio, lugar_extraido = extraer_lugar_del_titulo(titulo_original)

                    if lugar_extraido:
                        row['titulo'] = titulo_limpio
                        row['lugar'] = lugar_extraido
                        corregidos += 1
                        if corregidos <= 5:  # Mostrar primeros 5
                            print(f"Corregido: '{titulo_original}' → Título: '{titulo_limpio}', Lugar: '{lugar_extraido}'")

                writer.writerow(row)

    print(f"\n{'='*80}")
    print(f"PROCESAMIENTO COMPLETADO")
    print(f"{'='*80}")
    print(f"Total de entradas procesadas: {entrada_count}")
    print(f"Entradas corregidas: {corregidos}")
    print(f"\nArchivo generado: catalogo_depurado_v2.csv")
    print(f"{'='*80}")

if __name__ == "__main__":
    print("Creando catalogo_depurado_v2.csv...")
    print("Corrigiendo lugares mal parseados en títulos...")
    print()
    corregir_catalogo()
