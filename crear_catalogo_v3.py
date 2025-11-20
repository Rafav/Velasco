#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear catalogo_depurado_v3.csv
Extrae lugares de impresión desde el campo transcripcion_original
cuando el campo lugar está vacío o incorrecto
"""

import csv
import re
from collections import Counter

# Diccionario completo de lugares y sus variantes
LUGARES_ABREV = {
    # Madrid (todas las variantes)
    'Madrid': 'Madrid',
    'madrid': 'Madrid',
    'Mad.': 'Madrid',
    'mad.': 'Madrid',
    'Mad': 'Madrid',
    'mad': 'Madrid',
    'Matriti': 'Madrid',
    'matriti': 'Madrid',
    'MAtriti': 'Madrid',
    'Matrit': 'Madrid',

    # Salamanca
    'Salamanca': 'Salamanca',
    'Salmanticae': 'Salamanca',
    'Salmanitae': 'Salamanca',
    'Salmant.': 'Salamanca',

    # Alcalá
    'Alcalá de Henares': 'Alcalá de Henares',
    'Alcalá': 'Alcalá de Henares',
    'Compluti': 'Alcalá de Henares',
    'compluti': 'Alcalá de Henares',
    'Compl.': 'Alcalá de Henares',

    # Sevilla
    'Sevilla': 'Sevilla',
    'Hispali': 'Sevilla',
    'Hispal.': 'Sevilla',

    # Valencia
    'Valencia': 'Valencia',
    'valencia': 'Valencia',
    'Valentiae': 'Valencia',
    'Valent.': 'Valencia',

    # Barcelona
    'Barcelona': 'Barcelona',
    'Barcinone': 'Barcelona',
    'Barcinon.': 'Barcelona',

    # Zaragoza
    'Zaragoza': 'Zaragoza',
    'Caesaraugusta': 'Zaragoza',

    # Granada
    'Granada': 'Granada',
    'Granata': 'Granada',
    'Gramatae': 'Granada',

    # Burgos
    'Burgos': 'Burgos',
    'Burgi': 'Burgos',

    # Pamplona
    'Pamplona': 'Pamplona',
    'Pampilonae': 'Pamplona',

    # Cádiz
    'Cádiz': 'Cádiz',
    'Cadiz': 'Cádiz',
    'Gades': 'Cádiz',

    # Lugo
    'Lugo': 'Lugo',

    # París
    'Paris': 'París',
    'PAris': 'París',
    'Parisiis': 'París',
    'Lutetis Parisiorum': 'París',
    'Lutetiae': 'París',

    # Lyon
    'Lyon': 'Lyon',
    'lyon': 'Lyon',
    'Lugduni': 'Lyon',
    'Lugdun': 'Lyon',
    'Lugdun.': 'Lyon',

    # Roma
    'Roma': 'Roma',
    'Romae': 'Roma',
    'Rome': 'Roma',

    # Venecia
    'Venecia': 'Venecia',
    'Venetiis': 'Venecia',
    'Venet': 'Venecia',
    'Venet.': 'Venecia',

    # Amberes
    'Amberes': 'Amberes',
    'Antuerpiæ': 'Amberes',
    'Antuerpiae': 'Amberes',
    'Antwerp': 'Amberes',
    'Anverpie': 'Amberes',
    'Antucap': 'Amberes',  # Error OCR

    # Lisboa
    'Lisboa': 'Lisboa',
    'Olisipone': 'Lisboa',

    # Colonia
    'Colonia': 'Colonia',
    'Coloniae': 'Colonia',

    # Amsterdam
    'Amsterdam': 'Ámsterdam',
    'Hemsterdamii': 'Ámsterdam',

    # Estrasburgo
    'Estrasburgo': 'Estrasburgo',
    'Argentorati': 'Estrasburgo',
    'Argentinae': 'Estrasburgo',

    # Basilea
    'Basilea': 'Basilea',
    'Basileæ': 'Basilea',

    # Londres
    'London': 'Londres',
    'Londres': 'Londres',
    'Londini': 'Londres',

    # Florencia
    'Firenze': 'Florencia',
    'Florentia': 'Florencia',

    # Turín
    'Turin': 'Turín',
    'Turino': 'Turín',

    # Ginebra
    'Geneva': 'Ginebra',
    'Genevæ': 'Ginebra',
    'Coloniae Allobrogum': 'Ginebra',

    # Leiden
    'Leiden': 'Leiden',
    'Lugduni Batavorum': 'Leiden',
    'Lugd. Batav.': 'Leiden',
    'Lugdun Batavorum': 'Leiden',

    # La Haya
    'La Haya': 'La Haya',
    'Hagae Comitum': 'La Haya',

    # Malta
    'Malta': 'Malta',

    # Lecce
    'Lecce': 'Lecce',

    # Gotinga
    'Gotinga': 'Gotinga',
    'Goettingae': 'Gotinga',
    'Soetingae': 'Gotinga',  # Error OCR

    # Rostock
    'Rostock': 'Rostock',
    'Rost.': 'Rostock',
}

def extraer_lugar_de_transcripcion(transcripcion, lugar_actual):
    """
    Extrae el lugar de impresión de la transcripción completa
    Prioriza patrones con año: "lugar YYYY"
    """
    if not transcripcion:
        return None

    # Lista de lugares encontrados con su posición y confianza
    lugares_encontrados = []

    # Patrón: lugar seguido de año (4 dígitos)
    # Ej: "mad. 1794", "Madrid 1665", "Parisiis 1580"
    patron_lugar_año = r'(\w+\.?)\s+(\d{4})'

    for match in re.finditer(patron_lugar_año, transcripcion):
        posible_lugar = match.group(1)
        año = match.group(2)
        pos = match.start()

        # Verificar si el posible lugar está en nuestro diccionario
        lugar_normalizado = None
        for variante, normalizado in LUGARES_ABREV.items():
            if posible_lugar.lower() == variante.lower():
                lugar_normalizado = normalizado
                break

        if lugar_normalizado:
            # Alta confianza: lugar + año
            lugares_encontrados.append({
                'lugar': lugar_normalizado,
                'posicion': pos,
                'confianza': 100,
                'patron': f'{posible_lugar} {año}'
            })

    # Patrón: lugar sin año pero con formato típico
    # Ej: "8º mad.", "fol. Parisiis"
    patron_lugar_solo = r'[\s\.]([\w]+\.?)[\s\.]'

    for match in re.finditer(patron_lugar_solo, transcripcion):
        posible_lugar = match.group(1)
        pos = match.start()

        # Verificar si está en el diccionario
        lugar_normalizado = None
        for variante, normalizado in LUGARES_ABREV.items():
            if posible_lugar.lower() == variante.lower():
                lugar_normalizado = normalizado
                break

        if lugar_normalizado:
            # Ya lo encontramos con año? Skip
            if any(l['lugar'] == lugar_normalizado and l['confianza'] == 100
                   for l in lugares_encontrados):
                continue

            # Confianza media: lugar sin año
            lugares_encontrados.append({
                'lugar': lugar_normalizado,
                'posicion': pos,
                'confianza': 50,
                'patron': posible_lugar
            })

    # Si no encontramos nada, retornar None
    if not lugares_encontrados:
        return None

    # Ordenar por confianza (desc) y luego por posición (asc)
    lugares_encontrados.sort(key=lambda x: (-x['confianza'], x['posicion']))

    # Si ya tenemos un lugar actual, verificar si es correcto
    if lugar_actual and lugar_actual.strip():
        # Si el lugar actual coincide con alguno encontrado, mantenerlo
        for encontrado in lugares_encontrados:
            if encontrado['lugar'] == lugar_actual:
                return lugar_actual

    # Retornar el lugar con mayor confianza
    return lugares_encontrados[0]['lugar']

def limpiar_titulo(titulo, lugar):
    """
    Limpia el título removiendo referencias al lugar que ya se extrajo
    """
    if not titulo or not lugar:
        return titulo

    # Remover variantes del lugar del final del título
    for variante in LUGARES_ABREV.keys():
        if LUGARES_ABREV[variante] == lugar:
            # Remover "variante" o "variante." del final
            pattern = r'\s+' + re.escape(variante.rstrip('.')) + r'\.?\s*$'
            titulo = re.sub(pattern, '', titulo, flags=re.IGNORECASE)

    # Remover concatenaciones tipo "pastaMadrid", "4ºMadrid"
    if lugar == 'Madrid':
        titulo = re.sub(r'(pasta|fol|4º|8º|12º)madrid\s*$', r'\1', titulo, flags=re.IGNORECASE)
        titulo = re.sub(r'madrid\s*$', '', titulo, flags=re.IGNORECASE)

    return titulo.strip()

def crear_catalogo_v3():
    """
    Crea la versión 3 del catálogo depurado
    Corrige lugares extraídos de transcripcion_original
    """

    print("=" * 80)
    print("CREACIÓN DE CATÁLOGO DEPURADO V3")
    print("Extracción mejorada de lugares desde transcripcion_original")
    print("=" * 80)
    print()

    obras = []

    # Leer v2
    with open('/home/user/Velasco/catalogo_depurado_v2.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            obras.append(row)

    print(f"Total obras leídas: {len(obras)}")
    print()

    # Estadísticas
    correcciones = 0
    lugares_añadidos = 0
    lugares_corregidos = 0
    titulos_limpiados = 0

    # Procesar cada obra
    for obra in obras:
        lugar_original = obra['lugar']
        transcripcion = obra['transcripcion_original']
        titulo_original = obra['titulo']

        # Intentar extraer lugar de transcripción
        lugar_extraido = extraer_lugar_de_transcripcion(transcripcion, lugar_original)

        # Si encontramos un lugar
        if lugar_extraido:
            # Caso 1: No había lugar, ahora lo agregamos
            if not lugar_original or lugar_original.strip() == '':
                obra['lugar'] = lugar_extraido
                lugares_añadidos += 1
                correcciones += 1

                # Limpiar título
                titulo_limpio = limpiar_titulo(titulo_original, lugar_extraido)
                if titulo_limpio != titulo_original:
                    obra['titulo'] = titulo_limpio
                    titulos_limpiados += 1

            # Caso 2: Había lugar pero es diferente (posible corrección)
            elif lugar_extraido != lugar_original:
                # Solo corregir si el nuevo tiene alta confianza
                # Por ahora, mantener el original a menos que esté en lista de errores
                if lugar_original in ['No especificado', 'Pasta']:
                    obra['lugar'] = lugar_extraido
                    lugares_corregidos += 1
                    correcciones += 1

        # Limpiar títulos con Madrid/mad. al final
        if 'mad.' in titulo_original.lower() or 'madrid' in titulo_original.lower():
            if obra['lugar']:
                titulo_limpio = limpiar_titulo(titulo_original, obra['lugar'])
                if titulo_limpio != titulo_original:
                    obra['titulo'] = titulo_limpio
                    titulos_limpiados += 1

    # Escribir v3
    print("Escribiendo catalogo_depurado_v3.csv...")
    with open('/home/user/Velasco/catalogo_depurado_v3.csv', 'w', encoding='utf-8', newline='') as f:
        fieldnames = obras[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(obras)

    print()
    print("=" * 80)
    print("RESUMEN DE CORRECCIONES")
    print("=" * 80)
    print(f"Total correcciones: {correcciones}")
    print(f"  • Lugares añadidos (campo vacío → lugar): {lugares_añadidos}")
    print(f"  • Lugares corregidos (error → correcto): {lugares_corregidos}")
    print(f"  • Títulos limpiados: {titulos_limpiados}")
    print()

    # Verificar Madrid
    madrid_count = sum(1 for o in obras if o['lugar'] == 'Madrid')
    print(f"Total obras en Madrid: {madrid_count}")
    print()

    # Contar lugares
    lugares_count = Counter(o['lugar'] for o in obras if o['lugar'])
    print("Top 10 lugares:")
    for lugar, count in lugares_count.most_common(10):
        print(f"  {lugar:30} {count:4} obras")
    print()

    print("✓ Catálogo v3 creado exitosamente")
    print("=" * 80)

if __name__ == "__main__":
    crear_catalogo_v3()
