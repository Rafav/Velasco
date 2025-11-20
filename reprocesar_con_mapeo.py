#!/usr/bin/env python3
"""
Reprocesamiento con mapeo definido por el usuario
Lee datos_crudos.csv y aplica fusión de columnas según especificaciones
"""

import csv
import sys
from pathlib import Path
from collections import OrderedDict

# ============================================================================
# CONFIGURACIÓN DE MAPEO - DEFINIDO POR EL USUARIO
# ============================================================================

# Mapeo de columnas: columna_final ← [lista de columnas a fusionar en orden de prioridad]
MAPEO_COLUMNAS = {
    # CAMPOS PRINCIPALES
    'autor': [
        'autor', 'author', 'autores'
    ],
    
    'traductor': [
        'traductor', 'translator', 'translators', 'traducido_por'
    ],
    
    'titulo': [
        'titulo', 'title', 'obra', 'obra.titulo', 'work', 'item', 
        'descripcion', 'description'
    ],
    
    'precio': [
        'precio', 'price', 'precio_total', 'obra.precio', 'total_price', 
        'total', 'suma_total', 'suma_pagina', 'precio_total_seccion'
    ],
    
    'anio': [
        'anio', 'año', 'ano', 'anio_edicion', 'year', 'years', 
        'fecha', 'date', 'edad', 'age', 'rango_anios', 
        'fecha_inicio', 'fecha_fin', 'anio_reimpresion'
    ],
    
    'lugar': [
        'lugar_edicion', 'lugar', 'ubicacion', 'place', 'ubicacion_edicion',
        'place_year', 'place_and_year', 'ubicacion_fecha', 'lugar_fecha',
        'location_year'
    ],
    
    'formato': [
        'formato', 'format', 'folio', 'size'
    ],
    
    'numero_catalogo': [
        'numero', 'numero_catalogo', 'catalog_number', 'number', 
        'referencia', 'reference', 'item_number', 'id', 'codigo'
    ],
    
    'edicion': [
        'edicion', 'obra.edicion', 'edition', 'edition_note', 'editions',
        'publication_details', 'publication_info', 'publicacion'
    ],
    
    # CAMPOS SECUNDARIOS
    'volumen': [
        'volumen', 'volumenes', 'volume', 'volumes', 'tomo', 'volume_info',
        'parte', 'part', 'partes'
    ],
    
    'paginas': [
        'pagina', 'numero_paginas', 'pages', 'paginas', 'numero_hoja',
        'rango_paginas', 'numeros_paginas', 'page_reference', 'numeros',
        'numbers'
    ],
    
    'editorial': [
        'editorial'
    ],
    
    'editor': [
        'editor'
    ],
    
    'traduccion': [
        'traduccion', 'translation'
    ],
    
    'subtitulo': [
        'subtitulo', 'subtitle'
    ],
    
    'idioma': [
        'idioma', 'language'
    ],
    
    # CAMPOS RAROS (columnas separadas según especificación)
    'curador': [
        'curador'
    ],
    
    'dedicado_a': [
        'dedicado_a'
    ],
    
    'seccion': [
        'seccion', 'section', 'serie'
    ],
    
    'figura': [
        'figura', 'figuras', 'illustration'
    ],
    
    'estado': [
        'estado'
    ],
    
    'tipo': [
        'tipo'
    ],
    
    'encuadernacion': [
        'tipo_encuadernacion'
    ],
    
    'cantidad': [
        'cantidad'
    ],
    
    'monogram': [
        'monogram', 'contentmonogram'
    ],
    
    'source': [
        'source'
    ],
    
    'obras': [
        'obras'
    ],
    
    'contenido': [
        'contenido'
    ],
    
    'items': [
        'items'
    ],
    
    'subentries': [
        'subentries'
    ],
    
    'entries': [
        'entries'
    ],
    
    'references': [
        'references'
    ],
}

# Columnas de metadata que NO se fusionan
COLUMNAS_METADATA = ['id_fila', 'archivo_origen', 'numero_pagina', 'array_origen']

# Columnas que se excluyen de NOTAS (las que ya están mapeadas + metadata)
EXCLUIR_DE_NOTAS = set()
for columnas in MAPEO_COLUMNAS.values():
    EXCLUIR_DE_NOTAS.update(columnas)
EXCLUIR_DE_NOTAS.update(COLUMNAS_METADATA)

def obtener_valor_con_prioridad(fila, lista_columnas):
    """
    Busca el primer valor no-vacío en la lista de columnas según prioridad.
    NO normaliza - retorna el valor original tal cual está.
    """
    for columna in lista_columnas:
        valor = fila.get(columna, '').strip()
        if valor:
            return valor
    return ''

def fusionar_valores_multiples(fila, lista_columnas):
    """
    Recolecta TODOS los valores no-vacíos de múltiples columnas.
    Útil para campos donde puede haber múltiples fuentes complementarias.
    """
    valores = []
    for columna in lista_columnas:
        valor = fila.get(columna, '').strip()
        if valor and valor not in valores:
            valores.append(valor)
    
    return ' | '.join(valores) if valores else ''

def construir_transcripcion(fila):
    """
    Construye transcripción con TODOS los valores en bruto concatenados.
    Útil para búsqueda de texto completo y verificación manual.
    """
    valores = []
    
    for columna, valor in fila.items():
        # Saltar metadata (no son parte del contenido del libro)
        if columna in COLUMNAS_METADATA:
            continue
        
        # Añadir todos los valores no-vacíos
        valor = valor.strip()
        if valor:
            valores.append(valor)
    
    # Concatenar todo con espacios
    return ' '.join(valores) if valores else ''

def construir_notas(fila, columnas_usadas):
    """
    Construye campo de notas con TODO lo que no se usó en otros campos.
    Opción C del usuario: Incluir TODO lo que no esté en otros campos.
    """
    notas_partes = []
    
    for columna, valor in fila.items():
        # Saltar metadata
        if columna in COLUMNAS_METADATA:
            continue
        
        # Saltar columnas ya mapeadas
        if columna in EXCLUIR_DE_NOTAS:
            continue
        
        # Añadir si tiene valor
        valor = valor.strip()
        if valor:
            # Formato: campo=valor
            notas_partes.append(f"{columna}={valor}")
    
    return ' | '.join(notas_partes) if notas_partes else ''

def procesar_fila(fila_cruda):
    """
    Procesa una fila del CSV crudo aplicando el mapeo definido.
    Mantiene valores ORIGINALES sin normalización.
    Añade campo transcripcion con todos los datos concatenados.
    """
    fila_procesada = OrderedDict()
    
    # 1. Copiar metadata tal cual
    for col in COLUMNAS_METADATA:
        fila_procesada[col] = fila_cruda.get(col, '')
    
    # 2. Aplicar mapeo de columnas (valores originales, sin normalización)
    for columna_final, columnas_origen in MAPEO_COLUMNAS.items():
        fila_procesada[columna_final] = obtener_valor_con_prioridad(fila_cruda, columnas_origen)
    
    # 3. Añadir transcripción completa (todos los valores concatenados)
    fila_procesada['transcripcion'] = construir_transcripcion(fila_cruda)
    
    # 4. Construir campo de notas con TODO lo demás
    columnas_usadas = set(COLUMNAS_METADATA)
    for columnas in MAPEO_COLUMNAS.values():
        columnas_usadas.update(columnas)
    
    fila_procesada['notas'] = construir_notas(fila_cruda, columnas_usadas)
    
    return fila_procesada

def leer_csv_crudo(archivo_csv):
    """Lee el CSV de datos crudos"""
    print(f"\n📂 Leyendo: {archivo_csv}")
    
    filas = []
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        filas = list(reader)
    
    print(f"  ✓ {len(filas)} filas leídas")
    print(f"  ✓ {len(filas[0].keys()) if filas else 0} columnas en datos crudos")
    
    return filas

def escribir_csv_procesado(filas, archivo_salida):
    """Escribe el CSV procesado con columnas fusionadas"""
    
    if not filas:
        print("❌ No hay filas para escribir")
        return
    
    print(f"\n💾 Escribiendo resultado procesado...")
    
    # Obtener columnas del primer registro
    columnas = list(filas[0].keys())
    
    with open(archivo_salida, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        
        for i, fila in enumerate(filas, 1):
            writer.writerow(fila)
            
            if i % 500 == 0:
                print(f"  📝 Escritas {i}/{len(filas)} filas...")
    
    print(f"  ✅ Completado: {len(filas)} filas × {len(columnas)} columnas")
    print(f"  📁 Archivo: {archivo_salida}")

def generar_reporte_procesamiento(filas_crudas, filas_procesadas, archivo_reporte):
    """Genera reporte del procesamiento realizado"""
    
    print(f"\n📊 Generando reporte de procesamiento...")
    
    # Estadísticas
    total_filas = len(filas_procesadas)
    
    # Contar completitud de cada campo
    completitud = {}
    for columna in filas_procesadas[0].keys():
        if columna in COLUMNAS_METADATA:
            continue
        count = sum(1 for fila in filas_procesadas if fila.get(columna, '').strip())
        completitud[columna] = (count, count / total_filas * 100)
    
    # Ordenar por completitud
    completitud_ordenada = sorted(completitud.items(), key=lambda x: x[1][0], reverse=True)
    
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("REPORTE DE PROCESAMIENTO - DATOS FUSIONADOS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total de items procesados: {total_filas}\n")
        f.write(f"Columnas originales (crudas): {len(filas_crudas[0].keys())}\n")
        f.write(f"Columnas finales (procesadas): {len(filas_procesadas[0].keys())}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("COMPLETITUD DE CAMPOS (ordenado por cantidad)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'Campo':<30} {'Items':<10} {'%':<10}\n")
        f.write("-" * 80 + "\n")
        
        for columna, (count, pct) in completitud_ordenada:
            if count > 0:  # Solo mostrar columnas con datos
                f.write(f"{columna:<30} {count:<10} {pct:>6.1f}%\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("COLUMNAS VACÍAS (sin datos después del procesamiento)\n")
        f.write("=" * 80 + "\n\n")
        
        columnas_vacias = [col for col, (count, _) in completitud_ordenada if count == 0]
        
        if columnas_vacias:
            for col in columnas_vacias:
                f.write(f"  • {col}\n")
        else:
            f.write("  (Todas las columnas procesadas tienen al menos un dato)\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("MAPEO APLICADO\n")
        f.write("=" * 80 + "\n\n")
        
        for columna_final, columnas_origen in MAPEO_COLUMNAS.items():
            count, pct = completitud.get(columna_final, (0, 0))
            if count > 0:
                f.write(f"\n{columna_final} ({count} items, {pct:.1f}%):\n")
                f.write(f"  ← {', '.join(columnas_origen)}\n")
    
    print(f"  ✅ Reporte guardado: {archivo_reporte}")

def generar_estadisticas_basicas(filas, archivo_stats):
    """Genera estadísticas básicas del catálogo procesado"""
    
    print(f"\n📈 Generando estadísticas básicas...")
    
    total = len(filas)
    
    # Contar completitud de campos principales
    stats = {
        'Total items': total,
        'Con autor': sum(1 for f in filas if f.get('autor', '').strip()),
        'Con traductor': sum(1 for f in filas if f.get('traductor', '').strip()),
        'Con título': sum(1 for f in filas if f.get('titulo', '').strip()),
        'Con precio': sum(1 for f in filas if f.get('precio', '').strip()),
        'Con año': sum(1 for f in filas if f.get('anio', '').strip()),
        'Con lugar': sum(1 for f in filas if f.get('lugar', '').strip()),
        'Con formato': sum(1 for f in filas if f.get('formato', '').strip()),
        'Con edición': sum(1 for f in filas if f.get('edicion', '').strip()),
        'Con volumen': sum(1 for f in filas if f.get('volumen', '').strip()),
    }
    
    # Top 15 autores
    autores = {}
    for fila in filas:
        autor = fila.get('autor', '').strip()
        if autor:
            autores[autor] = autores.get(autor, 0) + 1
    top_autores = sorted(autores.items(), key=lambda x: x[1], reverse=True)[:15]
    
    with open(archivo_stats, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ESTADÍSTICAS BÁSICAS DEL CATÁLOGO\n")
        f.write("=" * 80 + "\n\n")
        
        for label, value in stats.items():
            pct = (value / total * 100) if total > 0 else 0
            f.write(f"{label:<20} {value:>6} ({pct:>5.1f}%)\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("TOP 15 AUTORES MÁS FRECUENTES\n")
        f.write("=" * 80 + "\n\n")
        
        for i, (autor, count) in enumerate(top_autores, 1):
            f.write(f"{i:2}. {autor:<50} ({count} obras)\n")
    
    print(f"  ✅ Estadísticas guardadas: {archivo_stats}")

def main():
    print("=" * 80)
    print("  REPROCESAMIENTO CON MAPEO DEFINIDO")
    print("  Fusiona columnas según especificaciones del usuario")
    print("=" * 80)
    
    # Buscar datos_crudos.csv
    archivo_crudo = Path('output_crudo/datos_crudos.csv')
    
    if not archivo_crudo.exists():
        print(f"\n❌ No se encuentra: {archivo_crudo}")
        print("\nAsegúrate de haber ejecutado primero:")
        print("  python extraer_todo_crudo.py /ruta/archivos/")
        sys.exit(1)
    
    # Leer datos crudos
    filas_crudas = leer_csv_crudo(archivo_crudo)
    
    if not filas_crudas:
        print("\n❌ El archivo de datos crudos está vacío")
        sys.exit(1)
    
    # Procesar filas aplicando mapeo
    print(f"\n⚙️  Procesando {len(filas_crudas)} filas...")
    print(f"   • Fusionando columnas según mapeo definido")
    print(f"   • Manteniendo valores ORIGINALES (sin normalización)")
    print(f"   • Construyendo campo notas con TODO lo no mapeado")
    
    filas_procesadas = []
    for i, fila_cruda in enumerate(filas_crudas, 1):
        fila_procesada = procesar_fila(fila_cruda)
        filas_procesadas.append(fila_procesada)
        
        if i % 500 == 0:
            print(f"   📊 Procesadas {i}/{len(filas_crudas)} filas...")
    
    print(f"   ✅ {len(filas_procesadas)} filas procesadas")
    
    # Crear carpeta de salida
    carpeta_salida = Path('output_final')
    carpeta_salida.mkdir(exist_ok=True)
    
    # Escribir CSV procesado
    archivo_procesado = carpeta_salida / 'catalogo_procesado.csv'
    escribir_csv_procesado(filas_procesadas, archivo_procesado)
    
    # Generar reportes
    archivo_reporte = carpeta_salida / 'reporte_procesamiento.txt'
    generar_reporte_procesamiento(filas_crudas, filas_procesadas, archivo_reporte)
    
    archivo_stats = carpeta_salida / 'estadisticas.txt'
    generar_estadisticas_basicas(filas_procesadas, archivo_stats)
    
    print("\n" + "=" * 80)
    print("  ✅ PROCESAMIENTO COMPLETADO")
    print("=" * 80)
    
    print(f"\n📁 Archivos generados en: {carpeta_salida.absolute()}")
    print(f"\n  1. catalogo_procesado.csv")
    print(f"     → {len(filas_procesadas)} items")
    print(f"     → {len(filas_procesadas[0].keys())} columnas finales")
    print(f"     → Valores originales mantenidos")
    print(f"     → Campo 'transcripcion' con todos los datos concatenados")
    print(f"     → Campo 'notas' con todo lo no mapeado")
    
    print(f"\n  2. reporte_procesamiento.txt")
    print(f"     → Completitud de cada campo")
    print(f"     → Mapeo aplicado")
    print(f"     → Columnas vacías")
    
    print(f"\n  3. estadisticas.txt")
    print(f"     → Resumen del catálogo")
    print(f"     → Top 15 autores")
    
    # Mostrar completitud de campos principales
    print(f"\n📊 Completitud de campos principales:")
    campos_principales = ['autor', 'traductor', 'titulo', 'precio', 'anio', 'lugar', 'formato']
    for campo in campos_principales:
        count = sum(1 for f in filas_procesadas if f.get(campo, '').strip())
        pct = count / len(filas_procesadas) * 100
        print(f"   • {campo:<15} {count:>4} / {len(filas_procesadas)} ({pct:>5.1f}%)")
    
    print(f"\n💡 Siguiente paso:")
    print(f"   1. Abre: {archivo_procesado}")
    print(f"   2. Revisa los datos fusionados")
    print(f"   3. Lee: reporte_procesamiento.txt para ver el mapeo")
    print(f"   4. Si quieres cambiar algo, modifica el mapeo y re-ejecuta")
    print()

if __name__ == "__main__":
    main()
