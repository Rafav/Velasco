#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis exhaustivo de libros heréticos, prohibidos y controvertidos
en el catálogo Velasco (1427-1799)

Basado en los Índices de libros prohibidos de la Inquisición española
"""

import csv
import re
from collections import defaultdict, Counter

# ==============================================================================
# AUTORES EN LOS ÍNDICES DE LIBROS PROHIBIDOS
# ==============================================================================

# Índice de Valdés (1559) y posteriores
AUTORES_HEREJES_PROTESTANTES = {
    'Erasmo': 'Desiderius Erasmus (Rotterdam) - Humanista, obras expurgadas',
    'Erasmus': 'Desiderius Erasmus (Rotterdam) - Humanista, obras expurgadas',
    'Rotterdam': 'Desiderius Erasmus de Rotterdam',
    'Lutero': 'Martín Lutero - Reformador protestante',
    'Luther': 'Martin Luther - Reformador protestante',
    'Luthero': 'Martín Lutero',
    'Calvino': 'Juan Calvino - Reformador protestante',
    'Calvin': 'Jean Calvin - Reformador protestante',
    'Calvinus': 'Johannes Calvinus',
    'Melanchthon': 'Philip Melanchthon - Reformador protestante',
    'Zwinglio': 'Ulrico Zwinglio - Reformador protestante',
    'Beza': 'Théodore de Bèze - Teólogo calvinista',
}

# Ilustrados prohibidos (siglo XVIII)
AUTORES_ILUSTRADOS_PROHIBIDOS = {
    'Voltaire': 'François-Marie Arouet (Voltaire) - Filósofo ilustrado',
    'Rousseau': 'Jean-Jacques Rousseau - Filósofo ilustrado',
    'Diderot': 'Denis Diderot - Enciclopedista',
    "D'Alembert": "Jean Le Rond d'Alembert - Enciclopedista",
    'Montesquieu': 'Charles de Montesquieu - Filósofo político',
    'Bayle': 'Pierre Bayle - Filósofo, Diccionario histórico-crítico',
    'Spinoza': 'Baruch Spinoza - Filósofo racionalista',
    'Hobbes': 'Thomas Hobbes - Filósofo político',
    'Locke': 'John Locke - Filósofo empirista',
}

# Otros autores prohibidos
AUTORES_OTROS_PROHIBIDOS = {
    'Maquiavelo': 'Nicolás Maquiavelo - El Príncipe (prohibido)',
    'Machiavel': 'Niccolò Machiavelli',
    'Ochino': 'Bernardino Ochino - Reformador italiano',
    'Sarpi': 'Paolo Sarpi - Historiador anti-papal',
    'Acontius': 'Jacobus Acontius - Teólogo liberal',
    'Castellio': 'Sebastián Castellio - Teólogo liberal',
}

# Jansenistas y Quietistas
AUTORES_JANSENISTAS_QUIETISTAS = {
    'Jansenio': 'Cornelius Jansen - Jansenismo',
    'Quesnel': 'Pasquier Quesnel - Jansenista',
    'Arnauld': 'Antoine Arnauld - Jansenista de Port-Royal',
    'Pascal': 'Blaise Pascal - Provinciales (jansenista)',
    'Molinos': 'Miguel de Molinos - Quietismo',
    'Madame Guyon': 'Jeanne-Marie Guyon - Quietista',
    'Fénelon': 'François Fénelon - Quietismo moderado',
}

# ==============================================================================
# TEMAS Y MATERIAS PROHIBIDAS
# ==============================================================================

TEMAS_HEREJIA = [
    'herej', 'heretic', 'heresy',
    'luteran', 'lutheran',
    'calvinist',
    'protestant',
    'reforma', 'reformation',
    'cisma', 'schism',
]

TEMAS_INQUISICION = [
    'inquisición', 'inquisicion', 'inquisitio',
    'santo oficio',
    'tribunal', 'censura',
    'expurgatorio', 'expurgat',
    'índice', 'index librorum',
    'prohib',
]

TEMAS_MAGIA_SUPERSTICION = [
    'magia', 'magic',
    'brujer', 'witchcraft',
    'hechic', 'sorcery',
    'nigromancia', 'necromancy',
    'alquim', 'alchemy',
    'astrolog', 'astrology',  # Astrología judicial prohibida
    'cabala', 'kabbalah',
    'sortilegio',
    'demonio', 'diablo',
]

TEMAS_JANSENISMO_QUIETISMO = [
    'janseni', 'janséni',
    'quietis', 'quietism',
    'molinist',
    'port-royal',
    'gracia', 'predestinación',
]

TEMAS_FILOSOFIA_PELIGROSA = [
    'ateísmo', 'atheism',
    'materialismo', 'materialism',
    'deísmo', 'deism',
    'libre pensamiento', 'free thinking',
    'epicureísmo', 'epicureanism',
]

# ==============================================================================
# OBRAS ESPECÍFICAS CONOCIDAS COMO PROHIBIDAS
# ==============================================================================

TITULOS_PROHIBIDOS = {
    'elogio de la locura': 'Erasmo - Encomium Moriae',
    'encomium moriae': 'Erasmo - Elogio de la locura',
    'coloquios': 'Erasmo - Colloquia',
    'adagios': 'Erasmo - Adagia (expurgado)',
    'el príncipe': 'Maquiavelo - Il Principe',
    'de principatibus': 'Maquiavelo - El Príncipe',
    'cándido': 'Voltaire - Candide',
    'cartas filosóficas': 'Voltaire - Lettres philosophiques',
    'diccionario filosófico': 'Voltaire - Dictionnaire philosophique',
    'emilio': 'Rousseau - Émile',
    'contrato social': 'Rousseau - Du contrat social',
    'nueva eloísa': 'Rousseau - La Nouvelle Héloïse',
    'espíritu de las leyes': 'Montesquieu - De l\'esprit des lois',
    'cartas persas': 'Montesquieu - Lettres persanes',
    'ensayo sobre el entendimiento': 'Locke - Essay Concerning Human Understanding',
    'leviatán': 'Hobbes - Leviathan',
    'pensamientos': 'Pascal - Pensées',
    'provinciales': 'Pascal - Lettres provinciales',
    'diccionario histórico': 'Bayle - Dictionnaire historique et critique',
    'enciclopedia': 'Diderot - Encyclopédie',
    'tractatus theologico-politicus': 'Spinoza',
    'guía espiritual': 'Molinos - Guía espiritual (quietismo)',
}

def analizar_catalogo():
    """Analiza el catálogo completo buscando obras prohibidas"""

    obras = []
    with open('/home/user/Velasco/catalogo_depurado_v3.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            obras.append(row)

    # Clasificación de obras prohibidas
    prohibidas = {
        'Herejes Protestantes': [],
        'Ilustrados prohibidos': [],
        'Jansenistas/Quietistas': [],
        'Otros autores prohibidos': [],
        'Magia y superstición': [],
        'Sobre la Inquisición': [],
        'Filosofía peligrosa': [],
        'Censura y expurgación': [],
        'Temas heréticos': [],
    }

    # Estadísticas
    stats = Counter()
    autores_encontrados = Counter()

    for obra in obras:
        autor_original = obra.get('autor', '')
        autor = autor_original.lower()
        titulo = obra.get('titulo', '').lower()
        texto = f'{autor} {titulo}'

        clasificada = False

        # 1. Autores herejes protestantes
        for nombre, descripcion in AUTORES_HEREJES_PROTESTANTES.items():
            if nombre.lower() in texto:
                prohibidas['Herejes Protestantes'].append({
                    'obra': obra,
                    'razon': descripcion,
                    'gravedad': 'ALTA',
                })
                stats['Herejes Protestantes'] += 1
                autores_encontrados[nombre] += 1
                clasificada = True
                break

        if clasificada:
            continue

        # 2. Ilustrados prohibidos
        for nombre, descripcion in AUTORES_ILUSTRADOS_PROHIBIDOS.items():
            if nombre.lower() in texto:
                prohibidas['Ilustrados prohibidos'].append({
                    'obra': obra,
                    'razon': descripcion,
                    'gravedad': 'ALTA',
                })
                stats['Ilustrados prohibidos'] += 1
                autores_encontrados[nombre] += 1
                clasificada = True
                break

        if clasificada:
            continue

        # 3. Jansenistas/Quietistas
        for nombre, descripcion in AUTORES_JANSENISTAS_QUIETISTAS.items():
            if nombre.lower() in texto:
                prohibidas['Jansenistas/Quietistas'].append({
                    'obra': obra,
                    'razon': descripcion,
                    'gravedad': 'MEDIA',
                })
                stats['Jansenistas/Quietistas'] += 1
                autores_encontrados[nombre] += 1
                clasificada = True
                break

        if clasificada:
            continue

        # 4. Otros autores prohibidos
        for nombre, descripcion in AUTORES_OTROS_PROHIBIDOS.items():
            if nombre.lower() in texto:
                prohibidas['Otros autores prohibidos'].append({
                    'obra': obra,
                    'razon': descripcion,
                    'gravedad': 'ALTA',
                })
                stats['Otros autores prohibidos'] += 1
                autores_encontrados[nombre] += 1
                clasificada = True
                break

        if clasificada:
            continue

        # 5. Títulos específicos prohibidos
        for titulo_prohibido, descripcion in TITULOS_PROHIBIDOS.items():
            if titulo_prohibido in titulo:
                cat = 'Ilustrados prohibidos' if any(x in descripcion for x in ['Voltaire', 'Rousseau', 'Montesquieu']) else 'Otros autores prohibidos'
                prohibidas[cat].append({
                    'obra': obra,
                    'razon': f'Título prohibido: {descripcion}',
                    'gravedad': 'ALTA',
                })
                stats[cat] += 1
                clasificada = True
                break

        if clasificada:
            continue

        # 6. Magia y superstición
        for tema in TEMAS_MAGIA_SUPERSTICION:
            if tema in texto:
                prohibidas['Magia y superstición'].append({
                    'obra': obra,
                    'razon': f'Materia prohibida: {tema}',
                    'gravedad': 'MEDIA',
                })
                stats['Magia y superstición'] += 1
                clasificada = True
                break

        if clasificada:
            continue

        # 7. Sobre la Inquisición
        for tema in TEMAS_INQUISICION:
            if tema in texto:
                prohibidas['Sobre la Inquisición'].append({
                    'obra': obra,
                    'razon': f'Tema: {tema}',
                    'gravedad': 'BAJA',  # No necesariamente prohibido, pero sensible
                })
                stats['Sobre la Inquisición'] += 1
                clasificada = True
                break

        if clasificada:
            continue

        # 8. Temas heréticos
        for tema in TEMAS_HEREJIA:
            if tema in texto:
                prohibidas['Temas heréticos'].append({
                    'obra': obra,
                    'razon': f'Tema herético: {tema}',
                    'gravedad': 'MEDIA',
                })
                stats['Temas heréticos'] += 1
                clasificada = True
                break

    return prohibidas, stats, autores_encontrados, len(obras)

def generar_reporte(prohibidas, stats, autores_encontrados, total_obras):
    """Genera reporte exhaustivo en texto"""

    print("=" * 100)
    print("ANÁLISIS EXHAUSTIVO DE LIBROS HERÉTICOS, PROHIBIDOS Y CONTROVERTIDOS")
    print("Catálogo Velasco (1427-1799)")
    print("=" * 100)
    print()
    print(f"Total obras en catálogo: {total_obras}")
    print(f"Total obras problemáticas identificadas: {sum(stats.values())}")
    print(f"Porcentaje: {(sum(stats.values())/total_obras)*100:.2f}%")
    print()

    print("=" * 100)
    print("RESUMEN POR CATEGORÍAS")
    print("=" * 100)
    print()
    for categoria in sorted(stats.keys(), key=lambda x: stats[x], reverse=True):
        print(f"  {categoria:40} {stats[categoria]:4} obras")
    print()

    print("=" * 100)
    print("AUTORES PROHIBIDOS ENCONTRADOS")
    print("=" * 100)
    print()
    for autor, count in autores_encontrados.most_common(20):
        print(f"  {autor:30} {count:3} obras")
    print()

    # Detalles por categoría
    for categoria, obras_cat in prohibidas.items():
        if not obras_cat:
            continue

        print()
        print("=" * 100)
        print(f"{categoria.upper()} ({len(obras_cat)} obras)")
        print("=" * 100)
        print()

        for i, item in enumerate(sorted(obras_cat, key=lambda x: x['gravedad'], reverse=True), 1):
            obra = item['obra']
            print(f"{i}. [{item['gravedad']}] {item['razon']}")
            print(f"   Autor: {obra['autor']}")
            print(f"   Título: {obra['titulo'][:120]}")
            print(f"   Lugar: {obra['lugar']} | Año: {obra['año']}")
            print()

if __name__ == "__main__":
    prohibidas, stats, autores_encontrados, total_obras = analizar_catalogo()
    generar_reporte(prohibidas, stats, autores_encontrados, total_obras)
