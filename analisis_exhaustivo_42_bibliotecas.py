#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis exhaustivo de 42 bibliotecas históricas españolas
Genera estadísticas avanzadas para ampliación del anexo
"""

import csv
from collections import defaultdict, Counter
import statistics

# Cargar datos
bidiso = []
with open('/home/user/Velasco/bibliotecas_bidiso_procesadas.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        bidiso.append(row)

adicionales = [
    {'id': 'velasco', 'propietario': 'Velasco y Ceballos, Fernando José de', 'fecha': '1791', 'num_obras': '7323'},
    {'id': 'campomanes', 'propietario': 'Rodríguez de Campomanes, Pedro', 'fecha': '†1802', 'num_obras': '5500'},
    {'id': 'jovellanos', 'propietario': 'Jovellanos, Gaspar Melchor de', 'fecha': '†1811', 'num_obras': '5374'}
]

todas = sorted(bidiso + adicionales, key=lambda x: int(x['num_obras']), reverse=True)

# Clasificar por perfil social
def clasificar_perfil(nombre):
    nombre_lower = nombre.lower()
    if 'magistrado' in nombre_lower or 'camarista' in nombre_lower or 'fiscal' in nombre_lower or 'ministro' in nombre_lower or 'oidor' in nombre_lower or 'inquisidor' in nombre_lower or 'relator' in nombre_lower or 'secretario' in nombre_lower:
        return 'Magistratura/Burocracia'
    elif 'duque' in nombre_lower or 'conde' in nombre_lower or 'marqués' in nombre_lower or 'príncipe' in nombre_lower:
        return 'Alta nobleza titulada'
    elif 'obispo' in nombre_lower or 'monasterio' in nombre_lower:
        return 'Alto clero/Instituciones'
    elif 'impresor' in nombre_lower:
        return 'Profesionales del libro'
    elif 'pintor' in nombre_lower or 'greco' in nombre_lower or 'velázquez' in nombre_lower:
        return 'Artistas'
    elif 'escritor' in nombre_lower or 'quevedo' in nombre_lower or 'inca garcilaso' in nombre_lower:
        return 'Literatos'
    elif 'maestro' in nombre_lower or 'humanista' in nombre_lower or 'erudito' in nombre_lower or 'pedagogo' in nombre_lower:
        return 'Humanistas/Eruditos'
    elif 'condesa' in nombre_lower or 'villalba' in nombre_lower or 'mencía' in nombre_lower or 'beatriz' in nombre_lower:
        return 'Nobleza femenina'
    else:
        return 'Otros nobles/Caballeros'

# Clasificar por período
def extraer_año(fecha_str):
    fecha_str = fecha_str.replace('†', '').replace('+', '').replace('-', '').strip()
    if ',' in fecha_str:
        fecha_str = fecha_str.split(',')[0]
    try:
        return int(fecha_str)
    except:
        return None

def clasificar_periodo(año):
    if año is None:
        return 'Desconocido'
    if año < 1550:
        return 'Renacimiento (1518-1549)'
    elif año < 1600:
        return 'Siglo de Oro temprano (1550-1599)'
    elif año < 1650:
        return 'Barroco temprano (1600-1649)'
    elif año < 1700:
        return 'Barroco tardío (1650-1699)'
    elif año < 1750:
        return 'Pre-Ilustración (1700-1749)'
    else:
        return 'Ilustración (1750-1811)'

# Análisis por perfil social
print("=" * 100)
print("ANÁLISIS POR PERFIL SOCIAL")
print("=" * 100)
print()

perfiles = defaultdict(list)
for lib in todas:
    perfil = clasificar_perfil(lib['propietario'])
    perfiles[perfil].append(int(lib['num_obras']))

print(f"{'Perfil social':<35} {'N bibl.':<10} {'Total obras':<15} {'Media':<10} {'Mediana':<10}")
print("-" * 100)
for perfil in sorted(perfiles.keys()):
    obras_list = perfiles[perfil]
    n = len(obras_list)
    total = sum(obras_list)
    media = total / n
    mediana = statistics.median(obras_list)
    print(f"{perfil:<35} {n:<10} {total:<15,} {media:<10,.0f} {mediana:<10,.0f}")

print()
print("=" * 100)
print("ANÁLISIS POR PERÍODO CRONOLÓGICO")
print("=" * 100)
print()

periodos = defaultdict(list)
for lib in todas:
    año = extraer_año(lib['fecha'])
    periodo = clasificar_periodo(año)
    periodos[periodo].append(int(lib['num_obras']))

orden_periodos = [
    'Renacimiento (1518-1549)',
    'Siglo de Oro temprano (1550-1599)',
    'Barroco temprano (1600-1649)',
    'Barroco tardío (1650-1699)',
    'Pre-Ilustración (1700-1749)',
    'Ilustración (1750-1811)'
]

print(f"{'Período':<35} {'N bibl.':<10} {'Media obras':<15} {'Min':<10} {'Max':<10}")
print("-" * 100)
for periodo in orden_periodos:
    if periodo in periodos:
        obras_list = periodos[periodo]
        n = len(obras_list)
        media = sum(obras_list) / n
        minimo = min(obras_list)
        maximo = max(obras_list)
        print(f"{periodo:<35} {n:<10} {media:<15,.0f} {minimo:<10,} {maximo:<10,}")

print()
print("=" * 100)
print("ANÁLISIS DE BIBLIOTECAS FEMENINAS VS MASCULINAS")
print("=" * 100)
print()

femeninas = []
masculinas = []

for lib in todas:
    nombre = lib['propietario'].lower()
    if any(x in nombre for x in ['condesa', 'mencía', 'beatriz', 'felipa', 'ana de toledo']):
        femeninas.append(int(lib['num_obras']))
    else:
        masculinas.append(int(lib['num_obras']))

print(f"Bibliotecas femeninas: {len(femeninas)}")
print(f"  Media: {statistics.mean(femeninas):.0f} obras")
print(f"  Mediana: {statistics.median(femeninas):.0f} obras")
print(f"  Total: {sum(femeninas):,} obras")
print()
print(f"Bibliotecas masculinas: {len(masculinas)}")
print(f"  Media: {statistics.mean(masculinas):.0f} obras")
print(f"  Mediana: {statistics.median(masculinas):.0f} obras")
print(f"  Total: {sum(masculinas):,} obras")
print()
print(f"Ratio masculino/femenino: {statistics.mean(masculinas)/statistics.mean(femeninas):.2f}x")

print()
print("=" * 100)
print("ESTRATIFICACIÓN POR TAMAÑO (quintiles)")
print("=" * 100)
print()

obras_ordenadas = sorted([int(lib['num_obras']) for lib in todas])
n_total = len(obras_ordenadas)

quintiles = [
    ('Q1 (0-20%)', obras_ordenadas[:int(n_total*0.2)]),
    ('Q2 (20-40%)', obras_ordenadas[int(n_total*0.2):int(n_total*0.4)]),
    ('Q3 (40-60%)', obras_ordenadas[int(n_total*0.4):int(n_total*0.6)]),
    ('Q4 (60-80%)', obras_ordenadas[int(n_total*0.6):int(n_total*0.8)]),
    ('Q5 (80-100%)', obras_ordenadas[int(n_total*0.8):]),
]

for nombre_q, obras_q in quintiles:
    media = statistics.mean(obras_q)
    total = sum(obras_q)
    pct_total = (total / sum(obras_ordenadas)) * 100
    print(f"{nombre_q:<15} Media: {media:>8,.0f}   Total: {total:>10,} ({pct_total:>5.1f}% del corpus)")

print()
print("=" * 100)
print("ANÁLISIS DE CONCENTRACIÓN (Coeficiente de Gini)")
print("=" * 100)
print()

# Calcular índice de Gini
def gini_coefficient(values):
    sorted_values = sorted(values)
    n = len(sorted_values)
    cumsum = 0
    for i, val in enumerate(sorted_values):
        cumsum += (n - i) * val
    return (2 * cumsum) / (n * sum(sorted_values)) - (n + 1) / n

obras_values = [int(lib['num_obras']) for lib in todas]
gini = gini_coefficient(obras_values)

print(f"Coeficiente de Gini: {gini:.4f}")
print(f"Interpretación: {'Desigualdad extrema' if gini > 0.6 else 'Desigualdad alta' if gini > 0.4 else 'Desigualdad moderada'}")
print()
print(f"Para referencia:")
print(f"  Gini = 0: Igualdad perfecta (todas las bibliotecas del mismo tamaño)")
print(f"  Gini = 1: Desigualdad perfecta (una biblioteca tiene todo)")
print(f"  Gini típico en distribución de riqueza: 0.3-0.5")
print(f"  Nuestro Gini {gini:.4f}: Concentración extrema del capital librario")

print()
print("=" * 100)
print("TOP 10% vs BOTTOM 10%")
print("=" * 100)
print()

top_10pct = obras_ordenadas[-4:]  # 10% de 42 ≈ 4
bottom_10pct = obras_ordenadas[:4]

print(f"Top 10% (4 bibliotecas más grandes):")
print(f"  Total obras: {sum(top_10pct):,}")
print(f"  % del corpus: {(sum(top_10pct)/sum(obras_ordenadas))*100:.1f}%")
print(f"  Media: {statistics.mean(top_10pct):,.0f} obras")
print()
print(f"Bottom 10% (4 bibliotecas más pequeñas):")
print(f"  Total obras: {sum(bottom_10pct):,}")
print(f"  % del corpus: {(sum(bottom_10pct)/sum(obras_ordenadas))*100:.1f}%")
print(f"  Media: {statistics.mean(bottom_10pct):.0f} obras")
print()
print(f"Ratio Top/Bottom: {sum(top_10pct)/sum(bottom_10pct):.1f}x")
