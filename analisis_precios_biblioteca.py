#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis económico de la biblioteca de Velasco y Ceballos
Tasación de Antonio Baylo, junio de 1791
Análisis de mercado librario del siglo XVIII
"""

import csv
import re
from collections import Counter, defaultdict
import statistics

def extraer_numero_tomos(tomos_str):
    """Extrae el número de tomos de la cadena"""
    if not tomos_str or tomos_str.strip() == '':
        return 1  # Asumimos 1 tomo si no se especifica

    # Buscar números en la cadena
    match = re.search(r'(\d+)', tomos_str)
    if match:
        return int(match.group(1))
    return 1

def analizar_precios():
    """Análisis exhaustivo de precios"""

    obras = []
    with open('/home/user/Velasco/catalogo_depurado_v3.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            obras.append(row)

    # Filtrar obras con precio
    obras_con_precio = []
    for obra in obras:
        precio_str = obra.get('precio', '').strip()
        if precio_str:
            try:
                precio = float(precio_str)
                num_tomos = extraer_numero_tomos(obra.get('tomos', ''))
                obras_con_precio.append({
                    'obra': obra,
                    'precio_total': precio,
                    'num_tomos': num_tomos,
                    'precio_por_tomo': precio / num_tomos if num_tomos > 0 else precio
                })
            except ValueError:
                pass

    print("=" * 100)
    print("ANÁLISIS ECONÓMICO DE LA BIBLIOTECA DE VELASCO Y CEBALLOS")
    print("Tasación de Antonio Baylo, junio de 1791")
    print("=" * 100)
    print()

    total_obras = len(obras)
    con_precio = len(obras_con_precio)

    print(f"Total obras catalogadas: {total_obras}")
    print(f"Obras con precio tasado: {con_precio} ({(con_precio/total_obras)*100:.1f}%)")
    print(f"Obras sin precio: {total_obras - con_precio} ({((total_obras - con_precio)/total_obras)*100:.1f}%)")
    print()

    # Estadísticas básicas
    precios_totales = [o['precio_total'] for o in obras_con_precio]
    precios_por_tomo = [o['precio_por_tomo'] for o in obras_con_precio]

    print("=" * 100)
    print("ESTADÍSTICAS DE PRECIOS TOTALES")
    print("=" * 100)
    print()
    print(f"Mínimo: {min(precios_totales):.2f} reales")
    print(f"Máximo: {max(precios_totales):.2f} reales")
    print(f"Media: {statistics.mean(precios_totales):.2f} reales")
    print(f"Mediana: {statistics.median(precios_totales):.2f} reales")
    print(f"Desviación estándar: {statistics.stdev(precios_totales):.2f} reales")
    print()

    # Percentiles
    precios_ordenados = sorted(precios_totales)
    p25 = precios_ordenados[int(len(precios_ordenados) * 0.25)]
    p50 = precios_ordenados[int(len(precios_ordenados) * 0.50)]
    p75 = precios_ordenados[int(len(precios_ordenados) * 0.75)]
    p90 = precios_ordenados[int(len(precios_ordenados) * 0.90)]
    p95 = precios_ordenados[int(len(precios_ordenados) * 0.95)]
    p99 = precios_ordenados[int(len(precios_ordenados) * 0.99)]

    print("Distribución por percentiles:")
    print(f"  P25 (25%): {p25:.2f} reales")
    print(f"  P50 (50%, mediana): {p50:.2f} reales")
    print(f"  P75 (75%): {p75:.2f} reales")
    print(f"  P90 (90%): {p90:.2f} reales")
    print(f"  P95 (95%): {p95:.2f} reales")
    print(f"  P99 (99%): {p99:.2f} reales")
    print()

    # Valor total de la biblioteca
    valor_total = sum(precios_totales)
    print(f"VALOR TOTAL DE LA BIBLIOTECA: {valor_total:,.2f} reales")
    print(f"Equivalente aproximado: {valor_total/34:.2f} doblones de oro")
    print(f"Equivalente aproximado: {valor_total/20:.2f} escudos de plata")
    print()

    # Distribución por rangos de precio
    print("=" * 100)
    print("DISTRIBUCIÓN POR RANGOS DE PRECIO")
    print("=" * 100)
    print()

    rangos = [
        (0, 1, "Menos de 1 real (limosna)"),
        (1, 5, "1-5 reales (muy barato)"),
        (5, 10, "5-10 reales (barato)"),
        (10, 20, "10-20 reales (módico)"),
        (20, 50, "20-50 reales (moderado)"),
        (50, 100, "50-100 reales (caro)"),
        (100, 200, "100-200 reales (muy caro)"),
        (200, 500, "200-500 reales (costoso)"),
        (500, 1000, "500-1.000 reales (carísimo)"),
        (1000, 10000, "1.000-10.000 reales (excepcional)"),
        (10000, 100000, "Más de 10.000 reales (tesoro bibliográfico)")
    ]

    for min_p, max_p, desc in rangos:
        count = sum(1 for p in precios_totales if min_p <= p < max_p)
        valor = sum(p for p in precios_totales if min_p <= p < max_p)
        if count > 0:
            print(f"{desc:45} {count:5} obras ({(count/con_precio)*100:5.2f}%) - Valor: {valor:10,.2f} reales")
    print()

    # Top 20 obras más caras
    print("=" * 100)
    print("TOP 20 OBRAS MÁS CARAS")
    print("=" * 100)
    print()

    obras_ordenadas = sorted(obras_con_precio, key=lambda x: x['precio_total'], reverse=True)
    for i, item in enumerate(obras_ordenadas[:20], 1):
        obra = item['obra']
        print(f"{i:2}. {item['precio_total']:8.2f} reales - {item['num_tomos']} tomo(s)")
        print(f"    Autor: {obra['autor']}")
        print(f"    Título: {obra['titulo'][:100]}")
        print(f"    Lugar: {obra['lugar']} | Año: {obra['año']} | Formato: {obra['formato']}")
        print()

    # Análisis por número de tomos
    print("=" * 100)
    print("ANÁLISIS POR NÚMERO DE TOMOS")
    print("=" * 100)
    print()

    tomos_stats = defaultdict(list)
    for item in obras_con_precio:
        tomos_stats[item['num_tomos']].append(item['precio_total'])

    print("Precio promedio por número de tomos:")
    for num_tomos in sorted(tomos_stats.keys())[:20]:  # Primeros 20
        precios = tomos_stats[num_tomos]
        print(f"  {num_tomos:2} tomo(s): {len(precios):5} obras - Media: {statistics.mean(precios):8.2f} reales - Mediana: {statistics.median(precios):8.2f} reales")
    print()

    # Precio por tomo
    print("=" * 100)
    print("PRECIO POR TOMO (normalizado)")
    print("=" * 100)
    print()
    print(f"Media por tomo: {statistics.mean(precios_por_tomo):.2f} reales")
    print(f"Mediana por tomo: {statistics.median(precios_por_tomo):.2f} reales")
    print()

    # Análisis por lugar de impresión
    print("=" * 100)
    print("PRECIO MEDIO POR LUGAR DE IMPRESIÓN (Top 15)")
    print("=" * 100)
    print()

    lugar_stats = defaultdict(list)
    for item in obras_con_precio:
        lugar = item['obra']['lugar']
        if lugar and lugar.strip():
            lugar_stats[lugar].append(item['precio_total'])

    lugar_ordenado = sorted(lugar_stats.items(),
                           key=lambda x: statistics.mean(x[1]) if len(x[1]) > 5 else 0,
                           reverse=True)[:15]

    for lugar, precios in lugar_ordenado:
        if len(precios) >= 5:  # Al menos 5 obras
            print(f"{lugar:25} {len(precios):4} obras - Media: {statistics.mean(precios):8.2f} reales - Mediana: {statistics.median(precios):8.2f} reales")
    print()

    # Análisis por formato
    print("=" * 100)
    print("PRECIO MEDIO POR FORMATO")
    print("=" * 100)
    print()

    formato_stats = defaultdict(list)
    for item in obras_con_precio:
        formato = item['obra']['formato']
        if formato and formato.strip():
            formato_stats[formato].append(item['precio_total'])

    for formato in sorted(formato_stats.keys(), key=lambda x: statistics.mean(formato_stats[x]) if len(formato_stats[x]) > 5 else 0, reverse=True):
        precios = formato_stats[formato]
        if len(precios) >= 5:
            print(f"{formato:15} {len(precios):4} obras - Media: {statistics.mean(precios):8.2f} reales - Mediana: {statistics.median(precios):8.2f} reales")
    print()

    # Análisis temporal
    print("=" * 100)
    print("PRECIO MEDIO POR SIGLO")
    print("=" * 100)
    print()

    siglo_stats = defaultdict(list)
    for item in obras_con_precio:
        año_str = item['obra']['año']
        if año_str and año_str.strip():
            try:
                año = int(año_str)
                siglo = (año // 100) + 1
                siglo_stats[siglo].append(item['precio_total'])
            except ValueError:
                pass

    for siglo in sorted(siglo_stats.keys()):
        precios = siglo_stats[siglo]
        print(f"Siglo {siglo:2} ({len(precios):4} obras): Media: {statistics.mean(precios):8.2f} reales - Mediana: {statistics.median(precios):8.2f} reales")
    print()

    # Obras baratas más representativas
    print("=" * 100)
    print("20 EJEMPLOS DE OBRAS BARATAS (1-10 reales)")
    print("=" * 100)
    print()

    obras_baratas = [o for o in obras_con_precio if 1 <= o['precio_total'] <= 10]
    for i, item in enumerate(sorted(obras_baratas, key=lambda x: x['precio_total'])[:20], 1):
        obra = item['obra']
        print(f"{i:2}. {item['precio_total']:6.2f} reales - {obra['autor']} - {obra['titulo'][:80]}")
    print()

    return obras_con_precio, valor_total

if __name__ == "__main__":
    obras_con_precio, valor_total = analizar_precios()

    print("=" * 100)
    print("FIN DEL ANÁLISIS")
    print("=" * 100)
