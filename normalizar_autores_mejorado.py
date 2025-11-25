#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script mejorado para normalizar nombres de autores
- Elimina todos los tratamientos
- Limpia comas en apellidos
- Convierte nombres latinos/franceses/griegos a castellano
"""

import re
import csv

INPUT_FILE = "autores_unicos_pre_IA.txt"
OUTPUT_FILE = "autores_unicos_post_IA.tsv"

# Diccionario de nombres latinos/griegos/franceses a castellano
NOMBRES_EQUIVALENTES = {
    # Nombres latinos clásicos
    'Petrus': 'Pedro',
    'Petri': 'Pedro',
    'Paulus': 'Pablo',
    'Pauli': 'Pablo',
    'Jacobus': 'Jacobo',
    'Jacobi': 'Jacobo',
    'Joannes': 'Juan',
    'Johannes': 'Juan',
    'Ioannes': 'Juan',
    'Io.': 'Juan',
    'Marcus': 'Marcos',
    'Marci': 'Marcos',
    'Lucas': 'Lucas',
    'Lucae': 'Lucas',
    'Matthaeus': 'Mateo',
    'Antonius': 'Antonio',
    'Antonii': 'Antonio',
    'Franciscus': 'Francisco',
    'Francisci': 'Francisco',
    'Carolus': 'Carlos',
    'Caroli': 'Carlos',
    'Ludovicus': 'Luis',
    'Ludovici': 'Luis',
    'Philippus': 'Felipe',
    'Philippi': 'Felipe',
    'Stephanus': 'Esteban',
    'Stephani': 'Esteban',
    'Thomas': 'Tomás',
    'Thomae': 'Tomás',
    'Augustinus': 'Agustín',
    'Augustini': 'Agustín',
    'Bernardus': 'Bernardo',
    'Bernardi': 'Bernardo',
    'Hieronymus': 'Jerónimo',
    'Hieronymi': 'Jerónimo',
    'Gregorius': 'Gregorio',
    'Gregorii': 'Gregorio',
    'Michael': 'Miguel',
    'Michaelis': 'Miguel',

    # Nombres franceses
    'Jacques': 'Jacobo',
    'Jean': 'Juan',
    'Pierre': 'Pedro',
    'François': 'Francisco',
    'Louis': 'Luis',
    'Charles': 'Carlos',
    'Henri': 'Enrique',
    'Philippe': 'Felipe',
    'Guillaume': 'Guillermo',
    'Étienne': 'Esteban',

    # Nombres griegos
    'Georgius': 'Jorge',
    'Georgii': 'Jorge',
    'Basilius': 'Basilio',
    'Basilii': 'Basilio',
    'Nicolaus': 'Nicolás',
    'Nicolai': 'Nicolás',
}

# Tratamientos a eliminar (más exhaustivo)
TRATAMIENTOS = [
    # Con punto
    r'\bM\.\s*r\b', r'\bP\.\b', r'\bFr\.\b', r'\bD\.\s*n\b', r'\bD\.\s*ª\b',
    r'\bD\.\b', r'\bSt\.\b', r'\bS\.\b', r'\bR\.\s*P\.\b', r'\bDr\.\b',
    r'\bMr\.\b', r'\bSr\.\b', r'\bSra\.\b', r'\bB\.\b', r'\bV\.\b',
    r'\bIlmo\.\b', r'\bExmo\.\b', r'\bRmo\.\b',

    # Sin punto (palabras completas)
    r'\bPadre\b', r'\bFray\b', r'\bDon\b', r'\bDoña\b', r'\bSanto\b',
    r'\bSanta\b', r'\bSan\b', r'\bDoctor\b', r'\bSeñor\b', r'\bSeñora\b',
    r'\bIlmo\b', r'\bExmo\b', r'\bRmo\b', r'\bIlustrísimo\b',
    r'\bExcelentísimo\b', r'\bReverendísimo\b',

    # Títulos nobiliarios
    r'\bPrincipe\b', r'\bPrincesa\b', r'\bRey\b', r'\bReina\b', r'\bReyna\b',
    r'\bCardenal\b', r'\bObispo\b', r'\bArzobispo\b', r'\bConde\b',
    r'\bCondesa\b', r'\bDuque\b', r'\bDuquesa\b', r'\bMarques\b',
    r'\bMarquesa\b', r'\bBarón\b', r'\bBaronesa\b', r'\bVizconde\b',
    r'\bVizcondesa\b',
]

def convertir_nombres_extranjeros(nombre):
    """
    Convierte nombres en latín, francés, griego a castellano
    """
    for extranjero, castellano in NOMBRES_EQUIVALENTES.items():
        # Reemplazar como palabra completa
        nombre = re.sub(r'\b' + re.escape(extranjero) + r'\b', castellano, nombre)

    return nombre

def normalizar_autor(autor_original):
    """
    Normaliza un nombre de autor con limpieza exhaustiva
    """
    autor = autor_original.strip()

    if not autor:
        return autor

    # 1. Convertir nombres extranjeros a castellano
    autor = convertir_nombres_extranjeros(autor)

    # 2. Eliminar todos los tratamientos
    for tratamiento in TRATAMIENTOS:
        autor = re.sub(tratamiento, '', autor, flags=re.IGNORECASE)

    # 3. Eliminar tratamientos sueltos en paréntesis
    autor = re.sub(r'\(\s*[DPF]r?\s+', '(', autor)
    autor = re.sub(r'\(\s*Don\s+', '(', autor)
    autor = re.sub(r'\(\s*Doña\s+', '(', autor)
    autor = re.sub(r'\(\s*Padre\s+', '(', autor)
    autor = re.sub(r'\(\s*Fray\s+', '(', autor)

    # 4. Eliminar letras sueltas D, P, Fr antes de nombres
    autor = re.sub(r'\b[DPF]\s+(?=[A-Z])', '', autor)
    autor = re.sub(r'\s+[DP]\s+', ' ', autor)

    # 5. Eliminar comas DENTRO de nombres (no entre apellido y nombre)
    # Si hay paréntesis, eliminar todas las comas
    if '(' in autor:
        autor = autor.replace(',', '')
    else:
        # Si no hay paréntesis, solo mantener una coma si separa claramente
        # partes del nombre (esto es conservador)
        partes = autor.split(',')
        if len(partes) == 2:
            # Formato "Apellido, Nombre" es válido
            autor = f"{partes[0].strip()}, {partes[1].strip()}"
        else:
            # Más de una coma o formato raro: eliminar todas
            autor = autor.replace(',', ' ')

    # 6. Eliminar puntos múltiples (...) y puntos sueltos
    autor = re.sub(r'\.{2,}', '', autor)
    autor = re.sub(r'\s+\.', '', autor)
    autor = re.sub(r'\.\s+', ' ', autor)

    # 7. Limpiar paréntesis
    autor = re.sub(r'\s*\(\s*', ' (', autor)
    autor = re.sub(r'\s*\)\s*', ') ', autor)
    autor = re.sub(r'\(\s*\)', '', autor)
    autor = re.sub(r'\(\s*de\s*\)', '', autor)
    autor = re.sub(r'\(\s*y\s*\)', '', autor)

    # 8. Normalizar espacios
    autor = re.sub(r'\s+', ' ', autor)
    autor = autor.strip()

    # 9. Eliminar puntos finales
    autor = re.sub(r'\.+$', '', autor)
    autor = autor.strip()

    return autor

def main():
    """
    Función principal
    """
    print(f"Leyendo autores de: {INPUT_FILE}")

    # Leer autores
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            autores_original = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {INPUT_FILE}")
        return

    print(f"  ✓ Cargados {len(autores_original)} autores")
    print()
    print("Normalizando nombres...")
    print("  - Eliminando tratamientos (D., Fr., Ilmo, Sr, etc.)")
    print("  - Limpiando comas en apellidos")
    print("  - Convirtiendo nombres latinos/franceses a castellano")
    print()

    # Normalizar autores
    autores_procesados = []
    cambios = 0
    nombres_convertidos = 0

    for autor_orig in autores_original:
        autor_norm = normalizar_autor(autor_orig)
        autores_procesados.append({
            'original': autor_orig,
            'normalizado': autor_norm
        })

        if autor_orig != autor_norm:
            cambios += 1
            # Detectar si se convirtió algún nombre extranjero
            for extranjero in NOMBRES_EQUIVALENTES.keys():
                if extranjero in autor_orig and extranjero not in autor_norm:
                    nombres_convertidos += 1
                    break

    print(f"  ✓ Normalizados {len(autores_procesados)} autores")
    print(f"  ✓ {cambios} autores modificados ({cambios/len(autores_procesados)*100:.1f}%)")
    print(f"  ✓ {nombres_convertidos} nombres convertidos a castellano")
    print()

    # Guardar resultados
    print(f"Guardando resultados en: {OUTPUT_FILE}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['autor_original', 'autor_normalizado'])

        for autor in autores_procesados:
            writer.writerow([autor['original'], autor['normalizado']])

    print(f"  ✓ Archivo guardado")
    print()

    # Mostrar ejemplos
    print("Ejemplos de normalizaciones (primeros 25 con cambios):")
    ejemplos = [a for a in autores_procesados if a['original'] != a['normalizado']][:25]

    for ejemplo in ejemplos:
        print(f"  {ejemplo['original']}")
        print(f"    → {ejemplo['normalizado']}")

    print()

    # Mostrar ejemplos de conversiones de nombres
    print("Ejemplos de conversiones de nombres extranjeros:")
    conversiones = []
    for autor in autores_procesados[:500]:  # Revisar primeros 500
        if autor['original'] != autor['normalizado']:
            for extranjero, castellano in NOMBRES_EQUIVALENTES.items():
                if extranjero in autor['original'] and castellano in autor['normalizado']:
                    conversiones.append(autor)
                    break
        if len(conversiones) >= 10:
            break

    for conv in conversiones:
        print(f"  {conv['original']}")
        print(f"    → {conv['normalizado']}")

    print()

if __name__ == "__main__":
    main()
