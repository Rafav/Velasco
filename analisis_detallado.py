#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis detallado del catálogo depurado
"""

import csv
import re
from collections import defaultdict, Counter
import json

def analizar_catalogo(archivo_csv):
    """
    Analiza el catálogo depurado y genera estadísticas detalladas
    """

    # Contadores y estadísticas
    stats = {
        'total_entradas': 0,
        'con_autor': 0,
        'anonimos': 0,
        'con_año': 0,
        'sin_año': 0,
        'con_lugar': 0,
        'sin_lugar': 0,
        'con_formato': 0,
        'con_tomos': 0,
        'con_figuras': 0,
        'con_pasta': 0,
        'con_atado': 0,
        'con_numero': 0,
        'con_precio': 0,
    }

    # Distribuciones
    autores = Counter()
    años = Counter()
    lugares = Counter()
    formatos = Counter()
    precios = []
    idiomas = Counter()

    # Listas para análisis
    entradas_sin_año = []
    entradas_sin_lugar = []
    entradas_sin_autor_identificado = []

    print("Analizando catálogo depurado...")
    print("=" * 80)

    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for fila in reader:
            stats['total_entradas'] += 1

            # Analizar autor
            autor = fila.get('autor', '')
            if autor and autor != '[Anónimo]':
                stats['con_autor'] += 1
                autores[autor] += 1
            else:
                stats['anonimos'] += 1
                entradas_sin_autor_identificado.append({
                    'titulo': fila.get('titulo', ''),
                    'año': fila.get('año', ''),
                    'lugar': fila.get('lugar', ''),
                    'transcripcion': fila.get('transcripcion_original', '')[:100]
                })

            # Analizar año
            año = fila.get('año', '')
            if año:
                stats['con_año'] += 1
                try:
                    años[int(año)] += 1
                except:
                    pass
            else:
                stats['sin_año'] += 1
                entradas_sin_año.append({
                    'autor': autor,
                    'titulo': fila.get('titulo', ''),
                    'transcripcion': fila.get('transcripcion_original', '')[:100]
                })

            # Analizar lugar
            lugar = fila.get('lugar', '')
            if lugar:
                stats['con_lugar'] += 1
                lugares[lugar] += 1
            else:
                stats['sin_lugar'] += 1
                entradas_sin_lugar.append({
                    'autor': autor,
                    'titulo': fila.get('titulo', ''),
                    'año': año,
                    'transcripcion': fila.get('transcripcion_original', '')[:100]
                })

            # Analizar formato
            formato = fila.get('formato', '')
            if formato:
                stats['con_formato'] += 1
                formatos[formato] += 1

            # Analizar tomos
            tomos = fila.get('tomos', '')
            if tomos:
                stats['con_tomos'] += 1

            # Analizar figuras
            figuras = fila.get('figuras', '')
            if figuras == 'Sí':
                stats['con_figuras'] += 1

            # Analizar pasta
            pasta = fila.get('pasta', '')
            if pasta and pasta != 'No especificado':
                stats['con_pasta'] += 1

            # Analizar atado
            atado = fila.get('atado', '')
            if atado:
                stats['con_atado'] += 1

            # Analizar número
            numero = fila.get('numero', '')
            if numero:
                stats['con_numero'] += 1

            # Analizar precio
            precio = fila.get('precio', '')
            if precio:
                stats['con_precio'] += 1
                try:
                    precio_num = int(re.sub(r'[^\d]', '', precio))
                    if precio_num > 0:
                        precios.append(precio_num)
                except:
                    pass

            # Detectar idioma por título
            titulo = fila.get('titulo', '').lower()
            if any(palabra in titulo for palabra in ['de', 'del', 'la', 'el', 'los', 'las', 'por', 'para']):
                idiomas['Español'] += 1
            elif any(palabra in titulo for palabra in ['de la', 'du', 'des', 'le', 'les', 'sur']):
                idiomas['Francés'] += 1
            elif any(palabra in titulo for palabra in ['della', 'degli', 'delle', 'per', 'alla']):
                idiomas['Italiano'] += 1
            elif any(palabra in titulo for palabra in ['ad', 'de', 'et', 'cum', 'ex', 'in']):
                idiomas['Latín'] += 1

    return stats, autores, años, lugares, formatos, precios, idiomas, \
           entradas_sin_año, entradas_sin_lugar, entradas_sin_autor_identificado


def generar_reporte_completo(archivo_salida, stats, autores, años, lugares,
                             formatos, precios, idiomas, entradas_sin_año,
                             entradas_sin_lugar, entradas_sin_autor_identificado):
    """
    Genera un reporte completo con todas las estadísticas
    """

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ANÁLISIS EXHAUSTIVO DEL CATÁLOGO DE LIBROS ANTIGUOS\n")
        f.write("Catálogo extraído con OCR - Período 1400-1800\n")
        f.write("=" * 80 + "\n\n")

        # ESTADÍSTICAS GENERALES
        f.write("1. ESTADÍSTICAS GENERALES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de entradas procesadas: {stats['total_entradas']}\n\n")

        f.write("Distribución de datos:\n")
        f.write(f"  • Entradas con autor identificado: {stats['con_autor']} ({stats['con_autor']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas anónimas: {stats['anonimos']} ({stats['anonimos']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas con año: {stats['con_año']} ({stats['con_año']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas sin año: {stats['sin_año']} ({stats['sin_año']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas con lugar: {stats['con_lugar']} ({stats['con_lugar']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas sin lugar: {stats['sin_lugar']} ({stats['sin_lugar']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas con formato: {stats['con_formato']} ({stats['con_formato']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas con tomos múltiples: {stats['con_tomos']} ({stats['con_tomos']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas con figuras: {stats['con_figuras']} ({stats['con_figuras']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas con pasta: {stats['con_pasta']} ({stats['con_pasta']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas atadas: {stats['con_atado']} ({stats['con_atado']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas con número de catálogo: {stats['con_numero']} ({stats['con_numero']/stats['total_entradas']*100:.1f}%)\n")
        f.write(f"  • Entradas con precio: {stats['con_precio']} ({stats['con_precio']/stats['total_entradas']*100:.1f}%)\n")
        f.write("\n")

        # AUTORES MÁS FRECUENTES
        f.write("2. AUTORES MÁS FRECUENTES (Top 30)\n")
        f.write("-" * 80 + "\n")
        for idx, (autor, cantidad) in enumerate(autores.most_common(30), 1):
            f.write(f"{idx:2}. {autor}: {cantidad} obras\n")
        f.write("\n")

        # DISTRIBUCIÓN TEMPORAL
        f.write("3. DISTRIBUCIÓN TEMPORAL (Por décadas)\n")
        f.write("-" * 80 + "\n")

        if años:
            decadas = defaultdict(int)
            for año, cantidad in años.items():
                decada = (año // 10) * 10
                decadas[decada] += cantidad

            for decada in sorted(decadas.keys()):
                cantidad = decadas[decada]
                barra = "█" * (cantidad // 10) + "▌" * ((cantidad % 10) // 5)
                f.write(f"{decada}s: {barra} ({cantidad} obras)\n")

            # Años con más publicaciones
            f.write(f"\nAños con más publicaciones (Top 20):\n")
            for año, cantidad in sorted(años.items(), key=lambda x: x[1], reverse=True)[:20]:
                f.write(f"  {año}: {cantidad} obras\n")
        f.write("\n")

        # LUGARES DE EDICIÓN
        f.write("4. LUGARES DE EDICIÓN MÁS FRECUENTES (Top 30)\n")
        f.write("-" * 80 + "\n")
        for idx, (lugar, cantidad) in enumerate(lugares.most_common(30), 1):
            porcentaje = cantidad / stats['total_entradas'] * 100
            f.write(f"{idx:2}. {lugar}: {cantidad} obras ({porcentaje:.1f}%)\n")
        f.write("\n")

        # FORMATOS
        f.write("5. DISTRIBUCIÓN DE FORMATOS\n")
        f.write("-" * 80 + "\n")
        for formato, cantidad in formatos.most_common():
            porcentaje = cantidad / stats['total_entradas'] * 100
            barra = "█" * (cantidad // 50) + "▌" * ((cantidad % 50) // 25)
            f.write(f"{formato:10}: {barra} {cantidad} ({porcentaje:.1f}%)\n")
        f.write("\n")

        # ANÁLISIS DE PRECIOS
        f.write("6. ANÁLISIS DE PRECIOS\n")
        f.write("-" * 80 + "\n")
        if precios:
            precios_ordenados = sorted(precios)
            f.write(f"Total de obras con precio: {len(precios)}\n")
            f.write(f"Precio mínimo: {min(precios)}\n")
            f.write(f"Precio máximo: {max(precios)}\n")
            f.write(f"Precio promedio: {sum(precios)/len(precios):.2f}\n")
            f.write(f"Precio mediano: {precios_ordenados[len(precios)//2]}\n")

            # Distribución por rangos
            f.write(f"\nDistribución por rangos de precio:\n")
            rangos = [(0, 10), (10, 25), (25, 50), (50, 100), (100, 200), (200, 500), (500, 10000)]
            for min_p, max_p in rangos:
                cantidad = sum(1 for p in precios if min_p <= p < max_p)
                if cantidad > 0:
                    porcentaje = cantidad / len(precios) * 100
                    f.write(f"  {min_p:4}-{max_p:4}: {cantidad:4} obras ({porcentaje:.1f}%)\n")
        f.write("\n")

        # IDIOMAS
        f.write("7. DISTRIBUCIÓN DE IDIOMAS (estimación basada en títulos)\n")
        f.write("-" * 80 + "\n")
        for idioma, cantidad in idiomas.most_common():
            porcentaje = cantidad / stats['total_entradas'] * 100
            f.write(f"{idioma:15}: {cantidad:5} obras ({porcentaje:.1f}%)\n")
        f.write("\n")

        # ENTRADAS SIN AÑO
        f.write("8. MUESTRA DE ENTRADAS SIN AÑO IDENTIFICADO (Primeras 20)\n")
        f.write("-" * 80 + "\n")
        for idx, entrada in enumerate(entradas_sin_año[:20], 1):
            f.write(f"{idx}. Autor: {entrada['autor']}\n")
            f.write(f"   Título: {entrada['titulo']}\n")
            f.write(f"   Transcripción: {entrada['transcripcion']}...\n\n")
        f.write("\n")

        # ENTRADAS SIN LUGAR
        f.write("9. MUESTRA DE ENTRADAS SIN LUGAR IDENTIFICADO (Primeras 20)\n")
        f.write("-" * 80 + "\n")
        for idx, entrada in enumerate(entradas_sin_lugar[:20], 1):
            f.write(f"{idx}. Autor: {entrada['autor']}\n")
            f.write(f"   Título: {entrada['titulo']}\n")
            f.write(f"   Año: {entrada['año']}\n")
            f.write(f"   Transcripción: {entrada['transcripcion']}...\n\n")
        f.write("\n")

        # OBRAS ANÓNIMAS
        f.write("10. MUESTRA DE OBRAS ANÓNIMAS (Primeras 30)\n")
        f.write("-" * 80 + "\n")
        for idx, entrada in enumerate(entradas_sin_autor_identificado[:30], 1):
            f.write(f"{idx}. Título: {entrada['titulo']}\n")
            f.write(f"   Lugar: {entrada['lugar']}, Año: {entrada['año']}\n")
            f.write(f"   Transcripción: {entrada['transcripcion']}...\n\n")
        f.write("\n")

        # RESUMEN DE CALIDAD
        f.write("11. EVALUACIÓN DE CALIDAD DE LOS DATOS\n")
        f.write("-" * 80 + "\n")

        completitud_autor = stats['con_autor'] / stats['total_entradas'] * 100
        completitud_año = stats['con_año'] / stats['total_entradas'] * 100
        completitud_lugar = stats['con_lugar'] / stats['total_entradas'] * 100
        completitud_precio = stats['con_precio'] / stats['total_entradas'] * 100

        completitud_promedio = (completitud_autor + completitud_año +
                               completitud_lugar + completitud_precio) / 4

        f.write(f"Completitud de campos esenciales:\n")
        f.write(f"  • Autor: {completitud_autor:.1f}%\n")
        f.write(f"  • Año: {completitud_año:.1f}%\n")
        f.write(f"  • Lugar: {completitud_lugar:.1f}%\n")
        f.write(f"  • Precio: {completitud_precio:.1f}%\n")
        f.write(f"\nCompletitud promedio: {completitud_promedio:.1f}%\n")

        if completitud_promedio >= 80:
            calidad = "EXCELENTE"
        elif completitud_promedio >= 70:
            calidad = "BUENA"
        elif completitud_promedio >= 60:
            calidad = "ACEPTABLE"
        else:
            calidad = "NECESITA MEJORA"

        f.write(f"Calidad general de los datos: {calidad}\n")
        f.write("\n")

        # PIE DE PÁGINA
        f.write("=" * 80 + "\n")
        f.write("Fin del análisis\n")
        f.write("=" * 80 + "\n")

    print(f"\nReporte completo generado: {archivo_salida}")


def main():
    """
    Función principal
    """
    print("Iniciando análisis exhaustivo del catálogo...")
    print()

    # Analizar catálogo
    stats, autores, años, lugares, formatos, precios, idiomas, \
    entradas_sin_año, entradas_sin_lugar, entradas_sin_autor_identificado = \
        analizar_catalogo('/home/user/Velasco/catalogo_depurado.csv')

    # Generar reporte completo
    generar_reporte_completo(
        '/home/user/Velasco/analisis_completo.txt',
        stats, autores, años, lugares, formatos, precios, idiomas,
        entradas_sin_año, entradas_sin_lugar, entradas_sin_autor_identificado
    )

    print("\n" + "=" * 80)
    print("ANÁLISIS COMPLETADO")
    print("=" * 80)
    print("\nResumen rápido:")
    print(f"  Total de entradas: {stats['total_entradas']}")
    print(f"  Autores identificados: {len(autores)}")
    print(f"  Obras anónimas: {stats['anonimos']}")
    print(f"  Rango temporal: {min(años.keys()) if años else 'N/A'} - {max(años.keys()) if años else 'N/A'}")
    print(f"  Lugares diferentes: {len(lugares)}")
    print(f"  Precio promedio: {sum(precios)/len(precios):.2f}" if precios else "  Sin datos de precios")
    print("\nArchivos generados:")
    print("  • analisis_completo.txt - Reporte detallado completo")


if __name__ == '__main__':
    main()
