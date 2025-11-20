#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis comparativo de bibliotecas históricas españolas
Velasco (1791) vs. otras bibliotecas del Siglo de Oro y la Ilustración
"""

import csv
import re
from collections import Counter, defaultdict
import statistics

def cargar_catalogo():
    """Carga el catálogo Velasco v3"""
    obras = []
    with open('/home/user/Velasco/catalogo_depurado_v3.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            obras.append(row)
    return obras

def analizar_periodos_cronologicos(obras):
    """Analiza distribución cronológica"""
    periodos = {
        'Incunables (pre-1501)': 0,
        'Siglo XVI (1501-1600)': 0,
        'Siglo XVII (1601-1700)': 0,
        'Siglo XVIII (1701-1799)': 0,
        'Sin fecha': 0
    }

    for obra in obras:
        año_str = obra.get('año', '').strip()
        if not año_str:
            periodos['Sin fecha'] += 1
            continue

        try:
            año = int(año_str)
            if año < 1501:
                periodos['Incunables (pre-1501)'] += 1
            elif 1501 <= año <= 1600:
                periodos['Siglo XVI (1501-1600)'] += 1
            elif 1601 <= año <= 1700:
                periodos['Siglo XVII (1601-1700)'] += 1
            elif 1701 <= año <= 1799:
                periodos['Siglo XVIII (1701-1799)'] += 1
        except ValueError:
            periodos['Sin fecha'] += 1

    return periodos

def analizar_lugares_impresion(obras):
    """Analiza principales lugares de impresión"""
    lugares = Counter()

    for obra in obras:
        lugar = obra.get('lugar', '').strip()
        if lugar:
            lugares[lugar] += 1

    return lugares

def analizar_lenguas(obras):
    """Detecta lenguas principales basándose en títulos y lugares"""
    lenguas = Counter()

    # Palabras clave por lengua
    indicadores_latin = ['de', 'et', 'in', 'ad', 'ex', 'cum', 'pro', 'per', 'tractatus', 'liber', 'opus']
    indicadores_español = ['del', 'los', 'las', 'para', 'sobre', 'historia', 'relacion', 'libro']
    indicadores_frances = ['le', 'la', 'les', 'des', 'pour', 'histoire', 'traité']
    indicadores_italiano = ['della', 'degli', 'delle', 'storia', 'trattato']

    for obra in obras:
        titulo = obra.get('titulo', '').lower()
        lugar = obra.get('lugar', '').lower()

        if not titulo:
            lenguas['Desconocido'] += 1
            continue

        # Latín (muy común en obras antiguas)
        if any(ind in titulo for ind in indicadores_latin):
            if 'paris' in lugar or 'lyon' in lugar:
                lenguas['Latín'] += 1
            elif 'roma' in lugar or 'venecia' in lugar or 'florencia' in lugar:
                lenguas['Latín'] += 1
            elif not any(ind in titulo for ind in indicadores_español):
                lenguas['Latín'] += 1
                continue

        # Español
        if any(ind in titulo for ind in indicadores_español):
            lenguas['Español'] += 1
        # Francés
        elif any(ind in titulo for ind in indicadores_frances) or 'paris' in lugar or 'lyon' in lugar:
            lenguas['Francés'] += 1
        # Italiano
        elif any(ind in titulo for ind in indicadores_italiano) or 'roma' in lugar or 'venecia' in lugar:
            lenguas['Italiano'] += 1
        else:
            lenguas['Desconocido'] += 1

    return lenguas

def analizar_materias(obras):
    """Clasifica obras por materias principales"""

    materias = Counter()

    # Palabras clave por materia
    clasificacion = {
        'Teología y religión': ['teolog', 'theolog', 'sacred', 'sagra', 'sermon', 'sancti', 'santo',
                                'iglesia', 'ecclesiast', 'religion', 'catechism', 'biblia', 'evangel',
                                'dios', 'cristo', 'virgen', 'maria', 'jesus', 'padre', 'obispo'],
        'Derecho': ['derecho', 'ley', 'leyes', 'iure', 'jure', 'legal', 'juridic', 'forense',
                   'tribunal', 'justicia', 'codigo', 'pragmatic', 'fuero', 'ordenanza'],
        'Historia': ['historia', 'history', 'cronica', 'chronicon', 'anales', 'memoir',
                    'guerra', 'conquista', 'reino', 'rey', 'emperador'],
        'Filosofía': ['philosoph', 'filosof', 'metaphysic', 'logica', 'ethic', 'moral'],
        'Medicina': ['medic', 'anatomia', 'ciruj', 'pharmac', 'salud', 'enfermedad'],
        'Ciencias': ['mathemat', 'geometr', 'physic', 'astronomia', 'natura', 'scientia'],
        'Literatura': ['poesia', 'poeta', 'fabula', 'novela', 'comedia', 'teatro', 'drama'],
        'Política': ['politica', 'politic', 'estado', 'gobierno', 'principe', 'republica'],
        'Gramática y lenguas': ['gramatica', 'grammar', 'lingua', 'lengua', 'diccionario', 'vocabular'],
        'Geografía': ['geographia', 'geografia', 'cosmograph', 'viaje', 'descripcion'],
    }

    for obra in obras:
        texto = f"{obra.get('titulo', '')} {obra.get('autor', '')}".lower()

        clasificado = False
        for materia, palabras_clave in clasificacion.items():
            if any(palabra in texto for palabra in palabras_clave):
                materias[materia] += 1
                clasificado = True
                break

        if not clasificado:
            materias['Otros'] += 1

    return materias

def analizar_formatos(obras):
    """Analiza distribución de formatos"""
    formatos = Counter()

    for obra in obras:
        formato = obra.get('formato', '').strip()
        if formato:
            formatos[formato] += 1
        else:
            formatos['Sin especificar'] += 1

    return formatos

def analizar_volumenes(obras):
    """Analiza distribución de número de tomos"""

    tomos_totales = 0
    obras_multivolumen = 0
    max_tomos = 0

    for obra in obras:
        tomos_str = obra.get('tomos', '').strip()
        if tomos_str:
            match = re.search(r'(\d+)', tomos_str)
            if match:
                num_tomos = int(match.group(1))
                tomos_totales += num_tomos
                if num_tomos > 1:
                    obras_multivolumen += 1
                if num_tomos > max_tomos:
                    max_tomos = num_tomos
            else:
                tomos_totales += 1
        else:
            tomos_totales += 1

    return {
        'tomos_totales': tomos_totales,
        'obras_multivolumen': obras_multivolumen,
        'max_tomos': max_tomos
    }

def generar_reporte_comparativo():
    """Genera reporte completo para comparación"""

    obras = cargar_catalogo()
    total_obras = len(obras)

    print("=" * 100)
    print("ANÁLISIS COMPARATIVO: BIBLIOTECA DE VELASCO Y CEBALLOS (1791)")
    print("Preparación para comparación con bibliotecas históricas españolas")
    print("=" * 100)
    print()

    print(f"TAMAÑO DE LA COLECCIÓN: {total_obras:,} obras catalogadas")
    print()

    # 1. Análisis cronológico
    print("=" * 100)
    print("1. DISTRIBUCIÓN CRONOLÓGICA")
    print("=" * 100)
    print()

    periodos = analizar_periodos_cronologicos(obras)
    for periodo, count in sorted(periodos.items()):
        porcentaje = (count / total_obras) * 100
        print(f"  {periodo:35} {count:6,} obras ({porcentaje:5.2f}%)")
    print()

    # 2. Lugares de impresión
    print("=" * 100)
    print("2. PRINCIPALES LUGARES DE IMPRESIÓN (Top 20)")
    print("=" * 100)
    print()

    lugares = analizar_lugares_impresion(obras)
    for lugar, count in lugares.most_common(20):
        porcentaje = (count / total_obras) * 100
        print(f"  {lugar:30} {count:6,} obras ({porcentaje:5.2f}%)")
    print()

    # 3. Lenguas
    print("=" * 100)
    print("3. DISTRIBUCIÓN POR LENGUAS (estimación)")
    print("=" * 100)
    print()

    lenguas = analizar_lenguas(obras)
    for lengua, count in lenguas.most_common():
        porcentaje = (count / total_obras) * 100
        print(f"  {lengua:20} {count:6,} obras ({porcentaje:5.2f}%)")
    print()

    # 4. Materias
    print("=" * 100)
    print("4. DISTRIBUCIÓN POR MATERIAS")
    print("=" * 100)
    print()

    materias = analizar_materias(obras)
    for materia, count in sorted(materias.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (count / total_obras) * 100
        print(f"  {materia:30} {count:6,} obras ({porcentaje:5.2f}%)")
    print()

    # 5. Formatos
    print("=" * 100)
    print("5. DISTRIBUCIÓN POR FORMATOS")
    print("=" * 100)
    print()

    formatos = analizar_formatos(obras)
    for formato, count in sorted(formatos.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (count / total_obras) * 100
        print(f"  {formato:20} {count:6,} obras ({porcentaje:5.2f}%)")
    print()

    # 6. Volúmenes
    print("=" * 100)
    print("6. ANÁLISIS DE VOLÚMENES")
    print("=" * 100)
    print()

    volumenes = analizar_volumenes(obras)
    print(f"  Total de tomos físicos: {volumenes['tomos_totales']:,}")
    print(f"  Obras multivolumen: {volumenes['obras_multivolumen']:,}")
    print(f"  Mayor número de tomos: {volumenes['max_tomos']}")
    print()

    # 7. Análisis económico (si hay datos de precios)
    print("=" * 100)
    print("7. RESUMEN ECONÓMICO")
    print("=" * 100)
    print()

    precios = []
    for obra in obras:
        precio_str = obra.get('precio', '').strip()
        if precio_str:
            try:
                precio = float(precio_str)
                precios.append(precio)
            except ValueError:
                pass

    if precios:
        total_valor = sum(precios)
        print(f"  Obras con precio: {len(precios):,} ({(len(precios)/total_obras)*100:.1f}%)")
        print(f"  Valor total tasado: {total_valor:,.2f} reales")
        print(f"  Precio medio: {statistics.mean(precios):.2f} reales")
        print(f"  Precio mediano: {statistics.median(precios):.2f} reales")
        print(f"  Precio mínimo: {min(precios):.2f} reales")
        print(f"  Precio máximo: {max(precios):.2f} reales")
    print()

    print("=" * 100)
    print("FIN DEL ANÁLISIS COMPARATIVO")
    print("=" * 100)

if __name__ == "__main__":
    generar_reporte_comparativo()
