#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valida lugares de edición contra el Tesauro CERL
"""

import csv
import requests
import time
from collections import defaultdict

def consultar_cerl(lugar):
    """
    Consulta el tesauro CERL para validar un lugar de edición
    """
    try:
        # API del tesauro CERL
        url = f"https://data.cerl.org/thesaurus/_search?query={lugar}&size=5&pretty=false"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'hits' in data and 'hits' in data['hits']:
                hits = data['hits']['hits']
                if hits:
                    resultados = []
                    for hit in hits[:3]:  # Top 3 resultados
                        source = hit.get('_source', {})
                        nombre = source.get('heading', 'N/A')
                        tipo = source.get('type', 'N/A')
                        variantes = source.get('variant_names', [])

                        resultados.append({
                            'nombre': nombre,
                            'tipo': tipo,
                            'variantes': variantes[:5]  # Primeras 5 variantes
                        })
                    return resultados

        return None

    except Exception as e:
        print(f"Error consultando CERL para '{lugar}': {e}")
        return None


def validar_lugares_catalogo(archivo_csv):
    """
    Valida todos los lugares únicos del catálogo contra CERL
    """

    lugares_unicos = defaultdict(int)

    # Leer todos los lugares
    print("Leyendo lugares del catálogo...")
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            lugar = fila.get('lugar', '').strip()
            if lugar:
                lugares_unicos[lugar] += 1

    print(f"Total de lugares únicos: {len(lugares_unicos)}")

    # Lugares dudosos (poco comunes o con nombres inusuales)
    lugares_dudosos = [
        'Ibid', 'ibid', 'Fudel', 'Smeting', 'Antucap', 'Gramatae',
        'Salmanitae', 'Soetingae', 'Lugduni', 'Coloniae', 'Hispani',
        'Paut.', 'Turino', 'Rost.', 'Anverpie', 'Hemsterdamii'
    ]

    resultados_validacion = {}

    print("\nValidando lugares dudosos contra CERL...")
    print("=" * 80)

    for lugar in lugares_dudosos:
        if lugar in lugares_unicos:
            print(f"\nConsultando: {lugar} ({lugares_unicos[lugar]} obras)")
            print("-" * 80)

            resultados = consultar_cerl(lugar)

            if resultados:
                print(f"Resultados encontrados en CERL:")
                for idx, res in enumerate(resultados, 1):
                    print(f"\n  {idx}. {res['nombre']} [{res['tipo']}]")
                    if res['variantes']:
                        print(f"     Variantes: {', '.join(res['variantes'][:3])}")

                resultados_validacion[lugar] = resultados
            else:
                print(f"  No se encontraron resultados en CERL")
                resultados_validacion[lugar] = None

            # Pausa para no sobrecargar el servidor
            time.sleep(1)

    return resultados_validacion, lugares_unicos


def generar_reporte_lugares(archivo_salida, validacion, lugares_unicos):
    """
    Genera un reporte con los lugares validados
    """

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("VALIDACIÓN DE LUGARES DE EDICIÓN CONTRA TESAURO CERL\n")
        f.write("=" * 80 + "\n\n")

        f.write("LUGARES VALIDADOS\n")
        f.write("-" * 80 + "\n\n")

        for lugar, resultados in validacion.items():
            f.write(f"Lugar: {lugar} ({lugares_unicos[lugar]} obras en el catálogo)\n")

            if resultados:
                for idx, res in enumerate(resultados, 1):
                    f.write(f"  {idx}. CERL: {res['nombre']} [{res['tipo']}]\n")
                    if res['variantes']:
                        f.write(f"     Variantes: {', '.join(res['variantes'][:5])}\n")
            else:
                f.write(f"  Estado: No encontrado en CERL (posible error OCR o lugar poco común)\n")

            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("RESUMEN DE TODOS LOS LUGARES (ordenados por frecuencia)\n")
        f.write("=" * 80 + "\n\n")

        for lugar, cantidad in sorted(lugares_unicos.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{lugar:30} : {cantidad:4} obras\n")

        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("Fin del reporte\n")

    print(f"\nReporte de validación guardado en: {archivo_salida}")


def main():
    """
    Función principal
    """
    print("Iniciando validación de lugares contra tesauro CERL...")
    print()

    validacion, lugares_unicos = validar_lugares_catalogo(
        '/home/user/Velasco/catalogo_depurado.csv'
    )

    generar_reporte_lugares(
        '/home/user/Velasco/validacion_lugares_cerl.txt',
        validacion,
        lugares_unicos
    )

    print("\n" + "=" * 80)
    print("VALIDACIÓN COMPLETADA")
    print("=" * 80)


if __name__ == '__main__':
    main()
