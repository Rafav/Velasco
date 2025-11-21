#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser de bibliotecas BIDISO descargadas
Extrae metadatos de los HTMLs descargados
"""

import os
import re
from html.parser import HTMLParser
import csv

class BIDISOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_subtitulo = False
        self.in_resultados = False
        self.subtitulo_text = ""
        self.resultados_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'div' and attrs_dict.get('id') == 'subtitulo':
            self.in_subtitulo = True
        elif tag == 'span' and 'resultados' in attrs_dict.get('class', ''):
            self.in_resultados = True

    def handle_data(self, data):
        if self.in_subtitulo:
            self.subtitulo_text += data
        elif self.in_resultados:
            self.resultados_text += data

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_subtitulo:
            self.in_subtitulo = False
        elif tag == 'span' and self.in_resultados:
            self.in_resultados = False

def extract_library_info(html_file):
    """Extrae información de un HTML de BIDISO"""
    with open(html_file, 'r', encoding='iso-8859-1') as f:
        html_content = f.read()

    parser = BIDISOParser()
    parser.feed(html_content)

    # Extraer propietario y fecha del subtítulo
    # Formato: "Registros del Inventario: Nombre (fecha)"
    subtitulo = parser.subtitulo_text.strip()
    owner_match = re.search(r'Registros del Inventario:\s*(.+?)(?:\s+\(([^)]+)\))?$', subtitulo)

    owner = ""
    date = ""
    if owner_match:
        owner = owner_match.group(1).strip()
        if owner_match.group(2):
            date = owner_match.group(2).strip()

    # Extraer número de resultados
    resultados = parser.resultados_text.strip()
    num_obras = 0
    num_match = re.search(r'(\d+)', resultados)
    if num_match:
        num_obras = int(num_match.group(1))

    # ID del archivo
    library_id = os.path.basename(html_file).replace('.html', '')

    return {
        'id': library_id,
        'propietario': owner,
        'fecha': date,
        'num_obras': num_obras
    }

def main():
    """Procesa todos los HTMLs descargados"""
    bidiso_dir = '/home/user/Velasco/bidiso_data'

    if not os.path.exists(bidiso_dir):
        print(f"Error: Directorio {bidiso_dir} no existe")
        return

    libraries = []

    # Procesar todos los HTMLs
    html_files = sorted([f for f in os.listdir(bidiso_dir) if f.endswith('.html')])

    print(f"Procesando {len(html_files)} bibliotecas BIDISO...")
    print()

    for html_file in html_files:
        filepath = os.path.join(bidiso_dir, html_file)
        try:
            info = extract_library_info(filepath)
            libraries.append(info)
            print(f"✓ {info['id']}: {info['propietario']} ({info['fecha']}) - {info['num_obras']:,} obras")
        except Exception as e:
            print(f"✗ Error procesando {html_file}: {e}")

    print()
    print("=" * 100)
    print(f"TOTAL: {len(libraries)} bibliotecas procesadas")
    print("=" * 100)
    print()

    # Ordenar por número de obras
    libraries_sorted = sorted(libraries, key=lambda x: x['num_obras'], reverse=True)

    print("TOP 20 BIBLIOTECAS MÁS GRANDES:")
    print("-" * 100)
    for i, lib in enumerate(libraries_sorted[:20], 1):
        print(f"{i:2}. {lib['propietario']:50} {lib['fecha']:15} {lib['num_obras']:8,} obras")
    print()

    # Guardar CSV
    csv_file = '/home/user/Velasco/bibliotecas_bidiso_procesadas.csv'
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'propietario', 'fecha', 'num_obras'])
        writer.writeheader()
        for lib in libraries_sorted:
            writer.writerow(lib)

    print(f"Datos guardados en: {csv_file}")
    print()

    # Estadísticas
    total_obras = sum(lib['num_obras'] for lib in libraries)
    media_obras = total_obras / len(libraries) if libraries else 0

    print("ESTADÍSTICAS:")
    print(f"  Total bibliotecas: {len(libraries)}")
    print(f"  Total obras catalogadas: {total_obras:,}")
    print(f"  Media por biblioteca: {media_obras:,.1f} obras")
    print(f"  Biblioteca más grande: {libraries_sorted[0]['propietario']} ({libraries_sorted[0]['num_obras']:,} obras)")
    print(f"  Biblioteca más pequeña: {libraries_sorted[-1]['propietario']} ({libraries_sorted[-1]['num_obras']:,} obras)")

if __name__ == "__main__":
    main()
