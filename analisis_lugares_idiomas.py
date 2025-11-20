#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis completo del catálogo de libros antiguos
Agrupa lugares por nombres castellanos actuales y desglosapor idioma
"""

import csv
import re
from collections import defaultdict, Counter

# Mapeo de lugares a nombres castellanos actuales
LUGARES_CASTELLANO = {
    # España
    'Madrid': 'Madrid',
    'madrid': 'Madrid',
    'Matriti': 'Madrid',
    'matriti': 'Madrid',
    'MAtriti': 'Madrid',
    'mad.': 'Madrid',
    'Mad.': 'Madrid',
    'Mad': 'Madrid',
    'Matrit': 'Madrid',

    'Salamanca': 'Salamanca',
    'Salmanticae': 'Salamanca',
    'Salmant.': 'Salamanca',
    'Salmanitae': 'Salamanca',

    'Zaragoza': 'Zaragoza',
    'Caesaraugusta': 'Zaragoza',

    'Valencia': 'Valencia',
    'Valentiae': 'Valencia',
    'valencia': 'Valencia',
    'Valent.': 'Valencia',

    'Sevilla': 'Sevilla',
    'Hispali': 'Sevilla',
    'Hispal.': 'Sevilla',

    'Barcelona': 'Barcelona',
    'Barcinone': 'Barcelona',
    'Barcinon.': 'Barcelona',

    'Granada': 'Granada',
    'Granata': 'Granada',
    'Gramatae': 'Granada',

    'Alcalá de Henares': 'Alcalá de Henares',
    'Alcalá': 'Alcalá de Henares',
    'Compluti': 'Alcalá de Henares',
    'compluti': 'Alcalá de Henares',
    'Compl.': 'Alcalá de Henares',

    'Burgos': 'Burgos',
    'Burgi': 'Burgos',

    'Pamplona': 'Pamplona',
    'Pampilonae': 'Pamplona',

    'Cádiz': 'Cádiz',
    'Cadiz': 'Cádiz',
    'Gades': 'Cádiz',

    'Lugo': 'Lugo',

    # Francia
    'Paris': 'París',
    'PAris': 'París',
    'Parisiis': 'París',
    'Lutetis Parisiorum': 'París',
    'Lutetiae': 'París',

    'Lugduni': 'Lyon',
    'Lugdun': 'Lyon',
    'Lyon': 'Lyon',
    'lyon': 'Lyon',

    'Estrasburgo': 'Estrasburgo',
    'Argentorati': 'Estrasburgo',
    'Argentinae': 'Estrasburgo',

    # Italia
    'Roma': 'Roma',
    'Romae': 'Roma',
    'Rome': 'Roma',

    'Venecia': 'Venecia',
    'Venetiis': 'Venecia',
    'Venet': 'Venecia',

    'Firenze': 'Florencia',
    'Florentia': 'Florencia',

    'Lecce': 'Lecce',

    'Turin': 'Turín',
    'Turino': 'Turín',

    # Países Bajos y Bélgica
    'Amberes': 'Amberes',
    'Antuerpiæ': 'Amberes',
    'Antuerpiae': 'Amberes',
    'Anverpie': 'Amberes',
    'Antwerp': 'Amberes',
    'Antucap': 'Amberes',  # Error OCR

    'Amsterdam': 'Ámsterdam',
    'Hemsterdamii': 'Ámsterdam',

    'Leiden': 'Leiden',
    'Lugduni Batavorum': 'Leiden',
    'Lugdun Batavorum': 'Leiden',
    'Lugd. Batav.': 'Leiden',

    'La Haye': 'La Haya',
    'la Haye': 'La Haya',

    # Alemania
    'Coloniae': 'Colonia',
    'Colonia': 'Colonia',
    'coloniae': 'Colonia',

    'Basilea': 'Basilea',
    'Basileæ': 'Basilea',

    'Soetingae': 'Gotinga',
    'Goettingae': 'Gotinga',

    # Suiza
    'Geneva': 'Ginebra',
    'Ginebra': 'Ginebra',
    'Genevæ': 'Ginebra',
    'Coloniae Allobrogum': 'Ginebra',

    # Reino Unido
    'London': 'Londres',
    'Londres': 'Londres',
    'Londini': 'Londres',

    # Portugal
    'Lisboa': 'Lisboa',
    'Olisipone': 'Lisboa',

    # Otros
    'Malta': 'Malta',
    'in Malta': 'Malta',
}

# Patrones para detectar idiomas
PATRONES_LATIN = [
    r'\b(de|et|ad|in|ex|cum|pro|per|inter|post|ante|contra|super)\b',
    r'\b(que|qua|qui|quod|quae|quibus|quorum|quam)\b',
    r'\b(est|sunt|erat|erant|sit|sint|esse|fuit|fuerant)\b',
    r'\b(orum|arum|ibus|æ|œ)\b',
    r'(tio|tione|tionem|tiones|tatis|tus|mentum)',
]

PATRONES_FRANCES = [
    r'\b(le|la|les|un|une|des|du|de|et|ou|à|dans|pour|sur|avec)\b',
    r'\b(histoire|traité|dissertation|mémoire|œuvre|oeuvre)\b',
]

PATRONES_ITALIANO = [
    r'\b(il|la|le|lo|gli|un|una|dei|delle|degli|di|da|in|con|per|su)\b',
    r'\b(storia|trattato|opera|delle|della)\b',
]

def normalizar_lugar(lugar):
    """Normaliza el lugar a su nombre castellano actual"""
    if not lugar or lugar.strip() == '':
        return None

    lugar = lugar.strip()

    # Ignorar referencias
    if lugar.lower() in ['ibid', 'ibid.', 'ibidem']:
        return 'ibid'

    # Buscar en el diccionario
    if lugar in LUGARES_CASTELLANO:
        return LUGARES_CASTELLANO[lugar]

    return lugar

def detectar_idioma(titulo, autor):
    """Detecta el idioma basándose en el título y autor"""
    if not titulo:
        return 'Desconocido'

    texto = f"{titulo} {autor}".lower()

    # Contador de coincidencias
    puntos_latin = sum(len(re.findall(patron, texto, re.IGNORECASE)) for patron in PATRONES_LATIN)
    puntos_frances = sum(len(re.findall(patron, texto, re.IGNORECASE)) for patron in PATRONES_FRANCES)
    puntos_italiano = sum(len(re.findall(patron, texto, re.IGNORECASE)) for patron in PATRONES_ITALIANO)

    # Si tiene desinencias latinas fuertes
    if puntos_latin >= 3:
        return 'Latín'

    if puntos_frances >= 2:
        return 'Francés'

    if puntos_italiano >= 2:
        return 'Italiano'

    # Si tiene palabras claramente castellanas
    palabras_castellano = [
        'historia', 'tratado', 'obras', 'vida', 'arte', 'discurso',
        'relación', 'política', 'derecho', 'comentario', 'libro'
    ]

    if any(palabra in texto for palabra in palabras_castellano):
        return 'Castellano'

    return 'Castellano'  # Por defecto, asumimos castellano

def analizar_catalogo():
    """Analiza el catálogo completo"""

    obras = []

    with open('/home/user/Velasco/catalogo_depurado_v2.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            obras.append(row)

    # Normalizar lugares
    lugares_normalizados = Counter()
    lugares_por_pais = defaultdict(list)
    obras_por_lugar = defaultdict(list)

    # Idiomas
    idiomas = Counter()
    obras_por_idioma = defaultdict(list)

    # Análisis por lugar e idioma combinado
    lugar_idioma = defaultdict(lambda: defaultdict(int))

    for obra in obras:
        # Normalizar lugar
        lugar_original = obra['lugar']
        lugar_norm = normalizar_lugar(lugar_original)

        if lugar_norm and lugar_norm != 'ibid':
            lugares_normalizados[lugar_norm] += 1
            obras_por_lugar[lugar_norm].append(obra)

        # Detectar idioma
        idioma = detectar_idioma(obra['titulo'], obra['autor'])
        idiomas[idioma] += 1
        obras_por_idioma[idioma].append(obra)

        # Combinación lugar-idioma
        if lugar_norm and lugar_norm != 'ibid':
            lugar_idioma[lugar_norm][idioma] += 1

    return {
        'total_obras': len(obras),
        'lugares_normalizados': lugares_normalizados,
        'obras_por_lugar': obras_por_lugar,
        'idiomas': idiomas,
        'obras_por_idioma': obras_por_idioma,
        'lugar_idioma': lugar_idioma,
        'obras': obras
    }

def generar_reporte(datos):
    """Genera un reporte completo en texto"""

    output = []
    output.append("=" * 80)
    output.append("ANÁLISIS COMPLETO: LUGARES DE IMPRESIÓN E IDIOMAS")
    output.append("Catálogo de Libros Antiguos (1427-1799)")
    output.append("=" * 80)
    output.append("")

    output.append(f"TOTAL DE OBRAS ANALIZADAS: {datos['total_obras']}")
    output.append("")

    # 1. LUGARES NORMALIZADOS
    output.append("=" * 80)
    output.append("1. LUGARES DE IMPRESIÓN (NOMBRES CASTELLANOS ACTUALES)")
    output.append("=" * 80)
    output.append("")

    # Agrupar por países
    lugares_españa = {}
    lugares_francia = {}
    lugares_italia = {}
    lugares_paises_bajos = {}
    lugares_alemania = {}
    lugares_portugal = {}
    lugares_otros = {}

    for lugar, count in datos['lugares_normalizados'].most_common():
        if lugar in ['Madrid', 'Salamanca', 'Zaragoza', 'Valencia', 'Sevilla',
                     'Barcelona', 'Granada', 'Alcalá de Henares', 'Burgos',
                     'Pamplona', 'Cádiz', 'Lugo']:
            lugares_españa[lugar] = count
        elif lugar in ['París', 'Lyon', 'Estrasburgo']:
            lugares_francia[lugar] = count
        elif lugar in ['Roma', 'Venecia', 'Florencia', 'Lecce', 'Turín']:
            lugares_italia[lugar] = count
        elif lugar in ['Amberes', 'Ámsterdam', 'Leiden', 'La Haya']:
            lugares_paises_bajos[lugar] = count
        elif lugar in ['Colonia', 'Basilea', 'Gotinga']:
            lugares_alemania[lugar] = count
        elif lugar in ['Lisboa']:
            lugares_portugal[lugar] = count
        elif lugar in ['Londres', 'Malta', 'Ginebra']:
            lugares_otros[lugar] = count

    # España
    output.append("ESPAÑA:")
    output.append("-" * 80)
    total_españa = 0
    for lugar in sorted(lugares_españa.keys(), key=lambda x: lugares_españa[x], reverse=True):
        count = lugares_españa[lugar]
        total_españa += count
        porcentaje = (count / datos['total_obras']) * 100
        output.append(f"  {lugar:30} {count:5} obras ({porcentaje:5.2f}%)")
    output.append(f"  {'TOTAL ESPAÑA':30} {total_españa:5} obras ({(total_españa/datos['total_obras'])*100:5.2f}%)")
    output.append("")

    # Francia
    output.append("FRANCIA:")
    output.append("-" * 80)
    total_francia = 0
    for lugar in sorted(lugares_francia.keys(), key=lambda x: lugares_francia[x], reverse=True):
        count = lugares_francia[lugar]
        total_francia += count
        porcentaje = (count / datos['total_obras']) * 100
        output.append(f"  {lugar:30} {count:5} obras ({porcentaje:5.2f}%)")
    output.append(f"  {'TOTAL FRANCIA':30} {total_francia:5} obras ({(total_francia/datos['total_obras'])*100:5.2f}%)")
    output.append("")

    # Italia
    output.append("ITALIA:")
    output.append("-" * 80)
    total_italia = 0
    for lugar in sorted(lugares_italia.keys(), key=lambda x: lugares_italia[x], reverse=True):
        count = lugares_italia[lugar]
        total_italia += count
        porcentaje = (count / datos['total_obras']) * 100
        output.append(f"  {lugar:30} {count:5} obras ({porcentaje:5.2f}%)")
    output.append(f"  {'TOTAL ITALIA':30} {total_italia:5} obras ({(total_italia/datos['total_obras'])*100:5.2f}%)")
    output.append("")

    # Países Bajos
    output.append("PAÍSES BAJOS Y BÉLGICA:")
    output.append("-" * 80)
    total_paises_bajos = 0
    for lugar in sorted(lugares_paises_bajos.keys(), key=lambda x: lugares_paises_bajos[x], reverse=True):
        count = lugares_paises_bajos[lugar]
        total_paises_bajos += count
        porcentaje = (count / datos['total_obras']) * 100
        output.append(f"  {lugar:30} {count:5} obras ({porcentaje:5.2f}%)")
    output.append(f"  {'TOTAL PAÍSES BAJOS':30} {total_paises_bajos:5} obras ({(total_paises_bajos/datos['total_obras'])*100:5.2f}%)")
    output.append("")

    # Alemania y Suiza
    output.append("ALEMANIA Y SUIZA:")
    output.append("-" * 80)
    total_alemania = 0
    for lugar in sorted(lugares_alemania.keys(), key=lambda x: lugares_alemania[x], reverse=True):
        count = lugares_alemania[lugar]
        total_alemania += count
        porcentaje = (count / datos['total_obras']) * 100
        output.append(f"  {lugar:30} {count:5} obras ({porcentaje:5.2f}%)")
    output.append(f"  {'TOTAL ALEMANIA/SUIZA':30} {total_alemania:5} obras ({(total_alemania/datos['total_obras'])*100:5.2f}%)")
    output.append("")

    # Portugal
    output.append("PORTUGAL:")
    output.append("-" * 80)
    total_portugal = 0
    for lugar in sorted(lugares_portugal.keys(), key=lambda x: lugares_portugal[x], reverse=True):
        count = lugares_portugal[lugar]
        total_portugal += count
        porcentaje = (count / datos['total_obras']) * 100
        output.append(f"  {lugar:30} {count:5} obras ({porcentaje:5.2f}%)")
    output.append(f"  {'TOTAL PORTUGAL':30} {total_portugal:5} obras ({(total_portugal/datos['total_obras'])*100:5.2f}%)")
    output.append("")

    # Otros
    if lugares_otros:
        output.append("OTROS PAÍSES:")
        output.append("-" * 80)
        total_otros = 0
        for lugar in sorted(lugares_otros.keys(), key=lambda x: lugares_otros[x], reverse=True):
            count = lugares_otros[lugar]
            total_otros += count
            porcentaje = (count / datos['total_obras']) * 100
            output.append(f"  {lugar:30} {count:5} obras ({porcentaje:5.2f}%)")
        output.append(f"  {'TOTAL OTROS':30} {total_otros:5} obras ({(total_otros/datos['total_obras'])*100:5.2f}%)")
        output.append("")

    # 2. IDIOMAS
    output.append("=" * 80)
    output.append("2. DISTRIBUCIÓN POR IDIOMAS")
    output.append("=" * 80)
    output.append("")

    for idioma, count in datos['idiomas'].most_common():
        porcentaje = (count / datos['total_obras']) * 100
        output.append(f"  {idioma:20} {count:5} obras ({porcentaje:5.2f}%)")
    output.append("")

    # 3. COMBINACIÓN LUGAR-IDIOMA (Top lugares)
    output.append("=" * 80)
    output.append("3. IDIOMAS POR LUGAR DE IMPRESIÓN (Top 15 ciudades)")
    output.append("=" * 80)
    output.append("")

    top_lugares = [lugar for lugar, _ in datos['lugares_normalizados'].most_common(15)]

    for lugar in top_lugares:
        if lugar in datos['lugar_idioma']:
            output.append(f"\n{lugar.upper()}:")
            output.append("-" * 80)
            total_lugar = sum(datos['lugar_idioma'][lugar].values())

            for idioma in ['Castellano', 'Latín', 'Francés', 'Italiano', 'Desconocido']:
                count = datos['lugar_idioma'][lugar].get(idioma, 0)
                if count > 0:
                    porcentaje = (count / total_lugar) * 100
                    output.append(f"  {idioma:20} {count:5} obras ({porcentaje:5.2f}%)")

    output.append("")

    # 4. OBRAS EN CASTELLANO VS LATÍN POR PERIODO
    output.append("=" * 80)
    output.append("4. EVOLUCIÓN CASTELLANO VS LATÍN POR SIGLO")
    output.append("=" * 80)
    output.append("")

    siglos = {
        'XV': (1400, 1499),
        'XVI': (1500, 1599),
        'XVII': (1600, 1699),
        'XVIII': (1700, 1799),
    }

    for siglo, (inicio, fin) in siglos.items():
        output.append(f"\nSIGLO {siglo} ({inicio}-{fin}):")
        output.append("-" * 80)

        obras_siglo = [o for o in datos['obras'] if o['año'] and o['año'].isdigit()
                      and inicio <= int(o['año']) <= fin]

        if obras_siglo:
            castellano = sum(1 for o in obras_siglo
                           if detectar_idioma(o['titulo'], o['autor']) == 'Castellano')
            latin = sum(1 for o in obras_siglo
                       if detectar_idioma(o['titulo'], o['autor']) == 'Latín')
            frances = sum(1 for o in obras_siglo
                         if detectar_idioma(o['titulo'], o['autor']) == 'Francés')
            otros = len(obras_siglo) - castellano - latin - frances

            total = len(obras_siglo)
            output.append(f"  Total obras:        {total:5}")
            output.append(f"  Castellano:         {castellano:5} ({(castellano/total)*100:5.2f}%)")
            output.append(f"  Latín:              {latin:5} ({(latin/total)*100:5.2f}%)")
            output.append(f"  Francés:            {frances:5} ({(frances/total)*100:5.2f}%)")
            output.append(f"  Otros:              {otros:5} ({(otros/total)*100:5.2f}%)")

    output.append("")
    output.append("=" * 80)
    output.append("Fin del análisis")
    output.append("=" * 80)

    return "\n".join(output)

if __name__ == "__main__":
    print("Analizando catálogo...")
    datos = analizar_catalogo()

    print("Generando reporte...")
    reporte = generar_reporte(datos)

    # Guardar reporte
    with open('/home/user/Velasco/analisis_lugares_idiomas.txt', 'w', encoding='utf-8') as f:
        f.write(reporte)

    print("Reporte guardado en: analisis_lugares_idiomas.txt")
    print(f"\nTotal obras analizadas: {datos['total_obras']}")
    print(f"Lugares únicos normalizados: {len(datos['lugares_normalizados'])}")
    print(f"Idiomas detectados: {len(datos['idiomas'])}")
