#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis REFINADO de libros heréticos, prohibidos y controvertidos
Versión mejorada con menor tasa de falsos positivos
"""

import csv
import re
from collections import defaultdict, Counter

# ==============================================================================
# AUTORES VERIFICADOS EN ÍNDICES DE LIBROS PROHIBIDOS
# ==============================================================================

def es_autor_prohibido(autor, titulo):
    """
    Verifica si una obra es de un autor prohibido
    Retorna: (es_prohibido, razon, gravedad, categoria)
    """

    autor_lower = autor.lower()
    titulo_lower = titulo.lower()

    # =========================================================================
    # ERASMO DE ROTTERDAM - Obras expurgadas desde Índice de Valdés (1559)
    # =========================================================================
    if 'erasmus' in autor_lower or (('erasmo' in autor_lower or 'rotterdam' in autor_lower) and 'erasmus' in titulo_lower):
        # Verificar que no sea falso positivo (lugar "Rotterdam")
        if autor_lower == '[anónimo]' and 'rotterdam' in titulo_lower and 'erasmus' not in titulo_lower:
            return False, None, None, None
        return True, 'Desiderius Erasmus Roterodamus - Obras expurgadas (Índice 1559)', 'ALTA', 'Humanistas expurgados'

    # =========================================================================
    # REFORMADORES PROTESTANTES - Prohibición absoluta
    # =========================================================================

    # Martín Lutero
    if ('luther' in autor_lower or 'lutero' in autor_lower) and '[anónimo]' not in autor_lower:
        return True, 'Martin Luther - Reformador protestante (prohibición total)', 'MÁXIMA', 'Herejes protestantes'

    # Obras CONTRA Lutero (permitidas)
    if 'adversus luther' in titulo_lower or 'contra luther' in titulo_lower:
        return False, None, None, None

    # Juan Calvino
    if ('calvin' in autor_lower or 'calvino' in autor_lower or 'calvinus' in autor_lower) and '[anónimo]' not in autor_lower:
        # Evitar "Calvino (Cesar)" que puede ser un nombre español
        if 'cesar' not in autor_lower and 'd.' not in autor_lower:
            return True, 'Jean Calvin - Reformador protestante (prohibición total)', 'MÁXIMA', 'Herejes protestantes'

    # Obras CONTRA Calvino (permitidas)
    if 'adversus calvin' in titulo_lower or 'contra calvin' in titulo_lower:
        return False, None, None, None

    # =========================================================================
    # ILUSTRADOS DEL SIGLO XVIII - Índice de 1747-1790
    # =========================================================================

    # Voltaire
    if 'voltaire' in autor_lower:
        return True, 'Voltaire (François-Marie Arouet) - Filósofo ilustrado prohibido', 'ALTA', 'Ilustrados prohibidos'

    # Rousseau
    if 'rousseau' in autor_lower:
        return True, 'Jean-Jacques Rousseau - Filósofo ilustrado prohibido (Émile, Contrato Social)', 'ALTA', 'Ilustrados prohibidos'

    # Montesquieu
    if 'montesquieu' in autor_lower:
        return True, 'Montesquieu - Espíritu de las Leyes (prohibido 1756)', 'ALTA', 'Ilustrados prohibidos'

    # Diderot y D'Alembert
    if 'diderot' in autor_lower or "d'alembert" in autor_lower:
        return True, 'Enciclopedista - Encyclopédie prohibida', 'ALTA', 'Ilustrados prohibidos'

    # Thomas Hobbes
    if 'hobbes' in autor_lower and 'thomas' in autor_lower:
        return True, 'Thomas Hobbes - Leviatán (prohibido)', 'ALTA', 'Filósofos prohibidos'

    # Spinoza
    if 'spinoza' in autor_lower:
        return True, 'Baruch Spinoza - Tractatus Theologico-Politicus (prohibido)', 'MÁXIMA', 'Filósofos prohibidos'

    # =========================================================================
    # JANSENISTAS - Condenados por Bula Unigenitus (1713)
    # =========================================================================

    # Pasquier Quesnel
    if 'quesnel' in autor_lower and 'pasquier' in titulo_lower:
        return True, 'Pasquier Quesnel - Jansenista (Bula Unigenitus)', 'ALTA', 'Jansenistas'

    # Antoine Arnauld
    if 'arnauld' in autor_lower or 'arnaldo' in autor_lower:
        # Evitar otros "Arnaldo"
        if 'antoine' in titulo_lower or 'antonio' in titulo_lower:
            return True, 'Antoine Arnauld - Jansenista de Port-Royal', 'MEDIA', 'Jansenistas'

    # =========================================================================
    # QUIETISTAS - Condenados por Inocencio XI (1687)
    # =========================================================================

    # Miguel de Molinos
    if 'molinos' in autor_lower and 'miguel' in autor_lower:
        return True, 'Miguel de Molinos - Guía Espiritual (quietismo, condenado 1687)', 'ALTA', 'Quietistas'

    # =========================================================================
    # OTROS AUTORES PROHIBIDOS
    # =========================================================================

    # Maquiavelo
    if 'machiavel' in autor_lower or 'maquiavelo' in autor_lower:
        return True, 'Nicolás Maquiavelo - El Príncipe (prohibido desde 1559)', 'ALTA', 'Política prohibida'

    # Paolo Sarpi
    if 'sarpi' in autor_lower and 'paolo' in titulo_lower:
        return True, 'Paolo Sarpi - Historia del Concilio de Trento (anti-papal)', 'ALTA', 'Anti-papales'

    # Bernardino Ochino
    if 'ochino' in autor_lower:
        return True, 'Bernardino Ochino - Reformador italiano (prohibición total)', 'MÁXIMA', 'Herejes protestantes'

    return False, None, None, None


def analizar_temas_prohibidos(titulo, transcripcion=''):
    """
    Analiza si el contenido trata temas prohibidos o sensibles
    Retorna: [(razon, gravedad, categoria), ...]
    """

    resultados = []
    titulo_lower = titulo.lower()
    texto = f'{titulo_lower} {transcripcion.lower()}'

    # =========================================================================
    # MAGIA, BRUJERÍA Y SUPERSTICIONES - Prohibido
    # =========================================================================

    # Magia y nigromancia
    if re.search(r'\bmagi[ac]\b|\bnigromanci', titulo_lower):
        if 'reyes magos' not in titulo_lower:  # Evitar falso positivo
            resultados.append(('Tema: Magia o nigromancia', 'MEDIA', 'Magia y superstición'))

    # Brujería
    if re.search(r'\bbrujer|\bhechic|\bsortilegi', titulo_lower):
        resultados.append(('Tema: Brujería o sortilegios', 'ALTA', 'Magia y superstición'))

    # Astrología judicial (prohibida, no la astronomía)
    if re.search(r'\bastrolog[ií]a\b', titulo_lower):
        if 'astronom' not in titulo_lower:  # La astronomía está permitida
            resultados.append(('Tema: Astrología judicial', 'MEDIA', 'Ciencias ocultas'))

    # Alquimia
    if re.search(r'\balquimi', titulo_lower):
        resultados.append(('Tema: Alquimia', 'BAJA', 'Ciencias ocultas'))

    # =========================================================================
    # INQUISICIÓN Y CENSURA - No prohibido, pero sensible
    # =========================================================================

    if re.search(r'\binquisici[oó]n\b|\bsanto oficio\b', titulo_lower):
        resultados.append(('Tema: Inquisición (registro institucional)', 'INFORMATIVA', 'Institucional'))

    if re.search(r'\b[ií]ndice.*prohib|\bexpurgat', titulo_lower):
        resultados.append(('Tema: Índice de libros prohibidos', 'INFORMATIVA', 'Censura'))

    # =========================================================================
    # HEREJÍAS Y PROTESTANTISMO
    # =========================================================================

    if re.search(r'\bherej[ií]a\b|\bher[ée]tic', titulo_lower):
        # Verificar si es CONTRA herejías (permitido)
        if re.search(r'contra.*herej|adversus.*haereti', titulo_lower):
            resultados.append(('Obra anti-herética (apologética)', 'PERMITIDA', 'Apologética'))
        else:
            resultados.append(('Tema: Herejía', 'ALTA', 'Herejías'))

    if re.search(r'\bprotestant', titulo_lower):
        if re.search(r'contra.*protestant|adversus.*protestant|historia.*variacion', titulo_lower):
            resultados.append(('Obra anti-protestante (apologética)', 'PERMITIDA', 'Apologética'))
        else:
            resultados.append(('Tema: Protestantismo', 'MEDIA', 'Protestantismo'))

    if re.search(r'\bluteran|\bcalvinist', titulo_lower):
        if 'adversus' in titulo_lower or 'contra' in titulo_lower:
            resultados.append(('Obra anti-luterana/calvinista (apologética)', 'PERMITIDA', 'Apologética'))
        else:
            resultados.append(('Tema: Luteranismo/Calvinismo', 'MEDIA', 'Protestantismo'))

    return resultados


def analizar_catalogo_refinado():
    """Análisis refinado del catálogo"""

    obras = []
    with open('/home/user/Velasco/catalogo_depurado_v3.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            obras.append(row)

    # Clasificación refinada
    prohibidas = defaultdict(list)
    stats = Counter()
    autores_prohibidos = Counter()

    for obra in obras:
        autor = obra.get('autor', '')
        titulo = obra.get('titulo', '')
        transcripcion = obra.get('transcripcion_original', '')

        # 1. Verificar autor prohibido
        es_prohibido, razon, gravedad, categoria = es_autor_prohibido(autor, titulo)

        if es_prohibido:
            prohibidas[categoria].append({
                'obra': obra,
                'razon': razon,
                'gravedad': gravedad,
            })
            stats[categoria] += 1
            # Extraer nombre del autor para estadísticas
            nombre_autor = razon.split('-')[0].strip()
            autores_prohibidos[nombre_autor] += 1
            continue  # No analizar temas si ya es autor prohibido

        # 2. Analizar temas
        temas = analizar_temas_prohibidos(titulo, transcripcion)
        for razon, gravedad, categoria in temas:
            prohibidas[categoria].append({
                'obra': obra,
                'razon': razon,
                'gravedad': gravedad,
            })
            stats[categoria] += 1

    return prohibidas, stats, autores_prohibidos, len(obras)


def generar_reporte_refinado(prohibidas, stats, autores_prohibidos, total_obras):
    """Genera reporte refinado"""

    print("=" * 100)
    print("ANÁLISIS EXHAUSTIVO DE LIBROS HERÉTICOS, PROHIBIDOS Y CONTROVERTIDOS")
    print("Catálogo Velasco (1427-1799) - Versión Refinada")
    print("=" * 100)
    print()
    print(f"Total obras en catálogo: {total_obras}")

    # Contar solo gravedad ALTA y MÁXIMA
    obras_prohibidas = sum(len([o for o in obras_cat if o['gravedad'] in ['ALTA', 'MÁXIMA']])
                          for obras_cat in prohibidas.values())
    obras_sospechosas = sum(len([o for o in obras_cat if o['gravedad'] == 'MEDIA'])
                           for obras_cat in prohibidas.values())
    obras_informativas = sum(len([o for o in obras_cat if o['gravedad'] in ['BAJA', 'INFORMATIVA', 'PERMITIDA']])
                             for obras_cat in prohibidas.values())

    print(f"Obras PROHIBIDAS (gravedad ALTA/MÁXIMA): {obras_prohibidas} ({(obras_prohibidas/total_obras)*100:.2f}%)")
    print(f"Obras SOSPECHOSAS (gravedad MEDIA): {obras_sospechosas} ({(obras_sospechosas/total_obras)*100:.2f}%)")
    print(f"Obras informativas/permitidas: {obras_informativas}")
    print()

    print("=" * 100)
    print("RESUMEN POR CATEGORÍAS")
    print("=" * 100)
    print()
    for categoria in sorted(stats.keys(), key=lambda x: stats[x], reverse=True):
        print(f"  {categoria:40} {stats[categoria]:4} obras")
    print()

    if autores_prohibidos:
        print("=" * 100)
        print("AUTORES PROHIBIDOS ENCONTRADOS (confirmados)")
        print("=" * 100)
        print()
        for autor, count in autores_prohibidos.most_common(30):
            print(f"  {autor:50} {count:3} obra(s)")
        print()

    # Detalles por categoría (solo gravedad ALTA y MÁXIMA)
    categorias_ordenadas = sorted(prohibidas.keys(),
                                  key=lambda x: len([o for o in prohibidas[x] if o['gravedad'] in ['ALTA', 'MÁXIMA']]),
                                  reverse=True)

    for categoria in categorias_ordenadas:
        obras_cat = prohibidas[categoria]
        obras_graves = [o for o in obras_cat if o['gravedad'] in ['ALTA', 'MÁXIMA']]

        if not obras_graves:
            continue

        print()
        print("=" * 100)
        print(f"{categoria.upper()} ({len(obras_graves)} obras prohibidas)")
        print("=" * 100)
        print()

        for i, item in enumerate(sorted(obras_graves, key=lambda x: x['gravedad'], reverse=True), 1):
            obra = item['obra']
            print(f"{i}. [{item['gravedad']}] {item['razon']}")
            print(f"   Autor: {obra['autor']}")
            print(f"   Título: {obra['titulo'][:120]}")
            print(f"   Lugar: {obra['lugar']} | Año: {obra['año']}")
            print()

if __name__ == "__main__":
    prohibidas, stats, autores_prohibidos, total_obras = analizar_catalogo_refinado()
    generar_reporte_refinado(prohibidas, stats, autores_prohibidos, total_obras)
