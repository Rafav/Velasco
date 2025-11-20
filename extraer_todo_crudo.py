#!/usr/bin/env python3
"""
Extractor de datos CRUDO - Sin procesamiento ni mapeo
Extrae TODO tal cual está en los JSONs para análisis posterior
"""

import json
import csv
import sys
import re
from pathlib import Path
from collections import OrderedDict

# Arrays donde buscar items (todos los detectados en el análisis)
ARRAYS_PRINCIPALES = [
    'inventario',
    'entries', 
    'inventory_entries',
    'catalog_entries',
    'entradas',
    'contenido',
    'items',
    'content',
]

def limpiar_para_csv(valor):
    """
    Limpieza MÍNIMA solo para que el CSV funcione.
    NO normaliza datos (años, precios, etc.)
    """
    if valor is None:
        return ''
    
    # Convertir a string
    texto = str(valor)
    
    # Eliminar caracteres de control que rompen CSV
    texto = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', texto)
    
    # Reemplazar saltos de línea por espacio
    texto = texto.replace('\n', ' ').replace('\r', ' ')
    
    # Reemplazar múltiples espacios por uno solo
    texto = re.sub(r'\s+', ' ', texto)
    
    # Strip espacios al inicio/fin
    texto = texto.strip()
    
    return texto

def aplanar_diccionario(obj, prefijo='', separador='.'):
    """
    Aplana un diccionario anidado usando notación de punto.
    
    Entrada: {"totales": {"suma_final": 100, "suma_inicial": 50}}
    Salida:  {"totales.suma_final": 100, "totales.suma_inicial": 50}
    """
    items = {}
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            nueva_key = f"{prefijo}{separador}{key}" if prefijo else key
            
            if isinstance(value, dict):
                # Recursión para diccionarios anidados
                items.update(aplanar_diccionario(value, nueva_key, separador))
            elif isinstance(value, list):
                # Listas se convierten a JSON string
                items[nueva_key] = json.dumps(value, ensure_ascii=False)
            else:
                items[nueva_key] = value
    else:
        items[prefijo] = obj
    
    return items

def extraer_numero_pagina(json_obj, nombre_archivo):
    """
    Intenta extraer el número de página del JSON o del nombre del archivo
    """
    # Buscar en el JSON
    campos_pagina = [
        'numero_pagina', 'page_number', 'pagina', 'pagina_actual',
        'numero_inventario', 'datos_adicionales.numero_pagina'
    ]
    
    for campo in campos_pagina:
        if '.' in campo:
            # Campo anidado
            partes = campo.split('.')
            temp = json_obj
            try:
                for parte in partes:
                    temp = temp[parte]
                if temp:
                    return str(temp)
            except (KeyError, TypeError):
                continue
        else:
            if campo in json_obj and json_obj[campo]:
                return str(json_obj[campo])
    
    # Buscar en el nombre del archivo
    match = re.search(r'(?:pagina|page)[_-]?(\d+)', nombre_archivo, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return ''

def extraer_items_de_json(json_obj, archivo_origen, numero_pagina):
    """
    Extrae TODOS los items de TODOS los arrays del JSON sin procesamiento
    """
    items = []
    
    for array_name in ARRAYS_PRINCIPALES:
        if array_name not in json_obj:
            continue
        
        array_items = json_obj[array_name]
        if not isinstance(array_items, list):
            continue
        
        for item_original in array_items:
            if not isinstance(item_original, dict):
                continue
            
            # Aplanar el item (convierte objetos anidados a notación punto)
            item_aplanado = aplanar_diccionario(item_original)
            
            # Añadir metadata
            item_con_metadata = {
                'id_fila': '',  # Se asignará después
                'archivo_origen': archivo_origen,
                'numero_pagina': numero_pagina,
                'array_origen': array_name,
            }
            
            # Añadir todos los datos del item
            item_con_metadata.update(item_aplanado)
            
            items.append(item_con_metadata)
    
    return items

def extraer_json_de_texto(texto):
    """Extrae y parsea JSON que puede estar escapado"""
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass
    
    # Si está dentro de una cadena escapada
    match = re.search(r'"text":\s*"(.+?)"(?=\s*[,}])', texto, re.DOTALL)
    if match:
        json_str = match.group(1)
        json_str = json_str.encode().decode('unicode_escape')
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    return None

def procesar_archivo_json(ruta_archivo):
    """Procesa un archivo JSON y extrae todos los items crudos"""
    items = []
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        nombre_archivo = ruta_archivo.name
        
        # Intentar como JSON único
        json_obj = extraer_json_de_texto(contenido)
        if json_obj:
            numero_pagina = extraer_numero_pagina(json_obj, nombre_archivo)
            return extraer_items_de_json(json_obj, nombre_archivo, numero_pagina)
        
        # Buscar múltiples JSONs en el contenido
        secciones = re.split(
            r'(?:Procesando pagina_\d+\.\.\.|✅ pagina_\d+ procesado con éxito|🖼️\s+Procesando pagina_\d+\.\.\.)',
            contenido
        )
        
        for seccion in secciones:
            if not seccion or len(seccion.strip()) < 10:
                continue
            
            json_obj = extraer_json_de_texto(seccion)
            if json_obj:
                numero_pagina = extraer_numero_pagina(json_obj, nombre_archivo)
                items_nuevos = extraer_items_de_json(json_obj, nombre_archivo, numero_pagina)
                items.extend(items_nuevos)
        
        return items
        
    except Exception as e:
        print(f"  ⚠️  Error en {ruta_archivo.name}: {e}")
        return []

def procesar_directorio(ruta_dir):
    """Procesa todos los archivos JSON en un directorio"""
    path = Path(ruta_dir)
    
    if not path.exists():
        print(f"❌ No existe: {ruta_dir}")
        sys.exit(1)
    
    archivos_json = sorted(path.glob('*.json'))
    
    if not archivos_json:
        print(f"❌ No hay archivos JSON en: {ruta_dir}")
        sys.exit(1)
    
    print(f"\n📂 Directorio: {path.absolute()}")
    print(f"📄 Archivos encontrados: {len(archivos_json)}")
    print(f"\n⏳ Extrayendo datos crudos...")
    
    todos_items = []
    archivos_procesados = 0
    errores = 0
    
    for i, archivo in enumerate(archivos_json, 1):
        try:
            items = procesar_archivo_json(archivo)
            todos_items.extend(items)
            archivos_procesados += 1
            
            if i % 100 == 0:
                print(f"  📄 Progreso: {i}/{len(archivos_json)} archivos ({len(todos_items)} items extraídos)")
        
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"  ⚠️  Error en {archivo.name}: {e}")
    
    print(f"\n  ✅ {archivos_procesados} archivos procesados")
    print(f"  📊 {len(todos_items)} items extraídos")
    if errores > 0:
        print(f"  ⚠️  {errores} archivos con errores")
    
    return todos_items

def recolectar_todas_columnas(items):
    """
    Recolecta TODAS las columnas únicas que aparecen en cualquier item.
    Preserva el orden: metadata primero, luego el resto alfabéticamente.
    """
    # Columnas de metadata en orden fijo
    columnas_metadata = ['id_fila', 'archivo_origen', 'numero_pagina', 'array_origen']
    
    # Recolectar todas las demás columnas
    columnas_datos = set()
    for item in items:
        for key in item.keys():
            if key not in columnas_metadata:
                columnas_datos.add(key)
    
    # Ordenar alfabéticamente
    columnas_datos = sorted(columnas_datos)
    
    # Metadata + datos
    return columnas_metadata + columnas_datos

def escribir_csv(items, archivo_salida):
    """Escribe todos los items a CSV con TODAS las columnas encontradas"""
    
    if not items:
        print("❌ No hay items para escribir")
        return
    
    print(f"\n📊 Recolectando columnas...")
    todas_columnas = recolectar_todas_columnas(items)
    print(f"  ✓ {len(todas_columnas)} columnas únicas encontradas")
    print(f"    - {todas_columnas[:4]} (metadata)")
    print(f"    - {len(todas_columnas) - 4} columnas de datos")
    
    print(f"\n💾 Escribiendo CSV...")
    
    # Asignar IDs secuenciales
    for i, item in enumerate(items, 1):
        item['id_fila'] = i
    
    with open(archivo_salida, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=todas_columnas, extrasaction='ignore')
        
        # Escribir encabezado
        writer.writeheader()
        
        # Escribir filas
        for i, item in enumerate(items, 1):
            # Limpiar todos los valores
            item_limpio = {}
            for key in todas_columnas:
                valor = item.get(key, '')
                item_limpio[key] = limpiar_para_csv(valor)
            
            writer.writerow(item_limpio)
            
            if i % 1000 == 0:
                print(f"  📝 Escritas {i}/{len(items)} filas...")
    
    print(f"  ✅ CSV completado: {len(items)} filas × {len(todas_columnas)} columnas")

def generar_reporte_columnas(items, archivo_reporte):
    """Genera un reporte de qué columnas tienen datos y cuántos"""
    
    print(f"\n📋 Generando reporte de columnas...")
    
    todas_columnas = recolectar_todas_columnas(items)
    
    # Contar cuántos items tienen cada columna no-vacía
    conteos = {}
    for columna in todas_columnas:
        if columna in ['id_fila', 'archivo_origen', 'numero_pagina', 'array_origen']:
            continue  # Skip metadata
        
        count = sum(1 for item in items if item.get(columna, '') != '')
        if count > 0:
            conteos[columna] = count
    
    # Ordenar por frecuencia
    conteos_ordenados = sorted(conteos.items(), key=lambda x: x[1], reverse=True)
    
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("REPORTE DE COLUMNAS - DATOS CRUDOS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total de items: {len(items)}\n")
        f.write(f"Total de columnas: {len(todas_columnas)}\n")
        f.write(f"Columnas con datos: {len(conteos)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("COLUMNAS ORDENADAS POR FRECUENCIA\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'Columna':<50} {'Items':<10} {'%':<10}\n")
        f.write("-" * 80 + "\n")
        
        for columna, count in conteos_ordenados:
            porcentaje = (count / len(items)) * 100
            f.write(f"{columna:<50} {count:<10} {porcentaje:>6.1f}%\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("COLUMNAS VACÍAS (sin datos en ningún item)\n")
        f.write("=" * 80 + "\n\n")
        
        columnas_vacias = [col for col in todas_columnas 
                          if col not in conteos and col not in 
                          ['id_fila', 'archivo_origen', 'numero_pagina', 'array_origen']]
        
        if columnas_vacias:
            for col in sorted(columnas_vacias):
                f.write(f"  • {col}\n")
        else:
            f.write("  (Todas las columnas tienen al menos un dato)\n")
    
    print(f"  ✅ Reporte guardado: {archivo_reporte}")

def main():
    print("=" * 80)
    print("  EXTRACTOR DE DATOS CRUDOS")
    print("  Sin procesamiento ni mapeo - Todo tal cual está")
    print("=" * 80)
    
    if len(sys.argv) < 2:
        print("\n❌ Uso: python extraer_todo_crudo.py <directorio>")
        print("\nEjemplo:")
        print("  python extraer_todo_crudo.py /home/rafa/Descargas/Velasco/")
        sys.exit(1)
    
    ruta_entrada = sys.argv[1]
    
    # Procesar archivos
    items = procesar_directorio(ruta_entrada)
    
    if not items:
        print("\n❌ No se extrajeron items")
        sys.exit(1)
    
    # Crear carpeta de salida
    carpeta_salida = Path('output_crudo')
    carpeta_salida.mkdir(exist_ok=True)
    
    # Escribir CSV
    archivo_csv = carpeta_salida / 'datos_crudos.csv'
    escribir_csv(items, archivo_csv)
    
    # Generar reporte
    archivo_reporte = carpeta_salida / 'reporte_columnas.txt'
    generar_reporte_columnas(items, archivo_reporte)
    
    print("\n" + "=" * 80)
    print("  ✅ EXTRACCIÓN COMPLETADA")
    print("=" * 80)
    print(f"\n📁 Archivos generados en: {carpeta_salida.absolute()}")
    print(f"\n  1. datos_crudos.csv")
    print(f"     → {len(items)} filas (items)")
    print(f"     → ~{len(recolectar_todas_columnas(items))} columnas")
    print(f"     → Tamaño: ~{archivo_csv.stat().st_size / (1024*1024):.1f} MB")
    print(f"\n  2. reporte_columnas.txt")
    print(f"     → Lista de todas las columnas")
    print(f"     → Frecuencia de cada una")
    print(f"     → Ayuda para decidir qué fusionar")
    
    print(f"\n💡 Siguiente paso:")
    print(f"   1. Abre datos_crudos.csv en Excel/LibreOffice")
    print(f"   2. Revisa qué columnas tienen datos")
    print(f"   3. Lee reporte_columnas.txt para ver frecuencias")
    print(f"   4. Decide qué columnas fusionar (ej: autor + author)")
    print(f"   5. Dime el mapeo para crear script de reprocesamiento\n")

if __name__ == "__main__":
    main()
