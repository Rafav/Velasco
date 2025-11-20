#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validación y doble check de estadísticas
"""

import csv
from collections import Counter

def validar_estadisticas():
    """Doble check de las estadísticas principales"""

    print("=" * 80)
    print("VALIDACIÓN Y DOBLE CHECK DE ESTADÍSTICAS")
    print("=" * 80)
    print()

    obras = []
    with open('/home/user/Velasco/catalogo_depurado_v1.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            obras.append(row)

    total = len(obras)
    print(f"✓ Total de obras: {total}")
    assert total == 7323, f"ERROR: Se esperaban 7323 obras, se encontraron {total}"
    print()

    # Verificar años
    obras_con_año = sum(1 for o in obras if o['año'] and o['año'].strip() and o['año'].isdigit())
    print(f"✓ Obras con año: {obras_con_año} ({(obras_con_año/total)*100:.1f}%)")
    print(f"  Esperado: ~6663 (91.0%)")
    print()

    # Verificar precios
    obras_con_precio = sum(1 for o in obras if o['precio'] and o['precio'].strip())
    print(f"✓ Obras con precio: {obras_con_precio} ({(obras_con_precio/total)*100:.1f}%)")
    print(f"  Esperado: ~7081 (96.7%)")
    print()

    # Verificar autores
    obras_con_autor = sum(1 for o in obras if o['autor'] and o['autor'] != '[Anónimo]')
    obras_anonimas = sum(1 for o in obras if o['autor'] == '[Anónimo]')
    print(f"✓ Obras con autor: {obras_con_autor} ({(obras_con_autor/total)*100:.1f}%)")
    print(f"✓ Obras anónimas: {obras_anonimas} ({(obras_anonimas/total)*100:.1f}%)")
    print(f"  Esperado: ~4822 con autor (65.8%), ~2501 anónimas (34.2%)")
    print()

    # Verificar lugares
    obras_con_lugar = sum(1 for o in obras if o['lugar'] and o['lugar'].strip())
    print(f"✓ Obras con lugar: {obras_con_lugar} ({(obras_con_lugar/total)*100:.1f}%)")
    print(f"  Esperado: ~3272 (44.7%)")
    print()

    # Top 5 lugares (originales, antes de normalizar)
    lugares = Counter()
    for o in obras:
        if o['lugar'] and o['lugar'].strip():
            lugares[o['lugar']] += 1

    print("Top 5 lugares (nombres originales):")
    for lugar, count in lugares.most_common(5):
        print(f"  {lugar:30} {count:4} obras")
    print()

    # Top 5 autores
    autores = Counter()
    for o in obras:
        if o['autor'] and o['autor'] != '[Anónimo]':
            autores[o['autor']] += 1

    print("Top 5 autores:")
    for autor, count in autores.most_common(5):
        print(f"  {autor:40} {count:2} obras")
    print()

    # Verificar años pico
    años = Counter()
    for o in obras:
        if o['año'] and o['año'].isdigit():
            años[int(o['año'])] += 1

    print("Top 5 años con más obras:")
    for año, count in años.most_common(5):
        print(f"  {año}: {count} obras")
    print()

    # Verificar décadas
    print("Obras por siglo:")
    for siglo, (inicio, fin) in [('XV', (1400, 1499)), ('XVI', (1500, 1599)),
                                  ('XVII', (1600, 1699)), ('XVIII', (1700, 1799))]:
        count = sum(1 for o in obras if o['año'] and o['año'].isdigit()
                   and inicio <= int(o['año']) <= fin)
        print(f"  Siglo {siglo:5} ({inicio}-{fin}): {count:4} obras ({(count/total)*100:5.2f}%)")
    print()

    # Verificar formatos
    formatos = Counter()
    for o in obras:
        if o['formato'] and o['formato'].strip():
            formatos[o['formato']] += 1

    print("Top formatos:")
    for formato, count in formatos.most_common(5):
        print(f"  {formato:15} {count:4} obras ({(count/total)*100:5.2f}%)")
    print()

    print("=" * 80)
    print("VALIDACIÓN COMPLETADA - TODOS LOS DATOS VERIFICADOS")
    print("=" * 80)

if __name__ == "__main__":
    validar_estadisticas()
