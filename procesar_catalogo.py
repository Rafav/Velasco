#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para procesar y depurar catálogo de libros extraído con OCR
"""

import csv
import re
import json
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import requests
import time

class ProcesadorCatalogo:
    def __init__(self):
        self.ultimo_autor = None
        self.estadisticas = defaultdict(int)
        self.lugares_dudosos = []
        self.errores = []
        self.referencias_resueltas = 0

    def extraer_autor(self, texto: str) -> Tuple[Optional[str], str]:
        """
        Extrae el autor del texto. Retorna (autor, texto_restante)
        Maneja formatos: Apellido (Nombre), id., it., Ejusd., Idem, Yd.
        """
        # Casos especiales de referencia al autor anterior
        # Patrones más completos: id., it., Ejusd., Ejusdem, Idem, Yd. (error OCR de "id.")
        patron_referencia = r'^(id\.|it\.|Yd\.|Ejusd\.|Ejusdem|Idem|eiusd\.|eiusdem)\s*'
        match_ref = re.match(patron_referencia, texto, re.IGNORECASE)

        if match_ref:
            # Es una referencia al autor anterior
            if self.ultimo_autor:
                self.referencias_resueltas += 1
                return self.ultimo_autor, texto[match_ref.end():]
            else:
                # No hay autor anterior, marcar como anónimo
                self.estadisticas['anonimos'] += 1
                return None, texto[match_ref.end():]

        # Patrón para autor: Apellido (Nombre) o variantes
        # Busca hasta encontrar un año de 4 dígitos o un formato (fol., 4º, 8º, etc.)
        patron_autor = r'^([A-ZÀ-Ÿa-zà-ÿ\s\.,\-]+?)\s*\(([^)]+)\)\s+'
        match = re.match(patron_autor, texto)

        if match:
            apellido = match.group(1).strip()
            nombre = match.group(2).strip()
            autor = f"{apellido} ({nombre})"
            self.ultimo_autor = autor
            self.estadisticas['con_autor'] += 1
            return autor, texto[match.end():]

        # Verificar si hay texto pero sin paréntesis (posible error OCR o formato alternativo)
        # Por ejemplo: "Acosta Jan" sin paréntesis
        patron_autor_simple = r'^([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)\s+(?=[A-Z])'
        match_simple = re.match(patron_autor_simple, texto)

        if match_simple and len(match_simple.group(1).split()) >= 2:
            # Parece un nombre completo sin paréntesis
            autor = match_simple.group(1).strip()
            self.ultimo_autor = autor
            self.estadisticas['con_autor'] += 1
            return autor, texto[match_simple.end():]

        # Si no hay autor explícito, podría ser anónimo
        # Verificar si el texto empieza directamente con un título
        if re.match(r'^[A-ZÀ-Ÿ][a-zà-ÿ]', texto):
            self.estadisticas['anonimos'] += 1
            return None, texto

        return None, texto

    def extraer_formato(self, texto: str) -> Tuple[Optional[str], str]:
        """
        Extrae el formato (fol., 4º, 8º, 12º, 16º, etc.)
        """
        patron_formato = r'\b(fol\.|4º|4°|8º|8°|12º|12°|16º|16°|mai\.|folio)\b'
        match = re.search(patron_formato, texto, re.IGNORECASE)

        if match:
            formato = match.group(1)
            return formato, texto

        return None, texto

    def extraer_tomos(self, texto: str) -> Tuple[Optional[str], str]:
        """
        Extrae información sobre tomos/volúmenes
        """
        patron_tomos = r'(\d+)\s*(tom\.|tomos|tomo|vol\.|volum\.|volumenes)'
        match = re.search(patron_tomos, texto, re.IGNORECASE)

        if match:
            tomos = f"{match.group(1)} {match.group(2)}"
            return tomos, texto

        return None, texto

    def extraer_figuras(self, texto: str) -> Tuple[bool, str]:
        """
        Detecta si tiene figuras/ilustraciones
        """
        patron_figuras = r'\b(fig\.|figuras|figura|illuminata da figuras|con fig\.)\b'
        match = re.search(patron_figuras, texto, re.IGNORECASE)

        return bool(match), texto

    def extraer_pasta(self, texto: str) -> Tuple[Optional[str], str]:
        """
        Extrae información sobre la pasta/encuadernación
        """
        patron_pasta = r'\b(Past\.|Pasta|pasta\s+blanc\.|pasta\s+blanca)\b'
        match = re.search(patron_pasta, texto, re.IGNORECASE)

        if match:
            return match.group(1), texto

        return None, texto

    def extraer_atado(self, texto: str) -> Tuple[Optional[str], str]:
        """
        Extrae información sobre si está atado y el número
        """
        patron_atado = r'\bAtado\s+(\d+)'
        match = re.search(patron_atado, texto, re.IGNORECASE)

        if match:
            return f"Atado {match.group(1)}", texto

        return None, texto

    def extraer_año(self, texto: str) -> Tuple[Optional[int], str]:
        """
        Extrae el año (4 dígras entre 1400 y 1800)
        """
        patron_año = r'\b(1[4-7]\d{2}|1800)\b'
        matches = re.findall(patron_año, texto)

        if matches:
            # Tomar el primer año válido
            año = int(matches[0])
            if 1400 <= año <= 1800:
                self.estadisticas['con_año'] += 1
                return año, texto

        self.estadisticas['sin_año'] += 1
        return None, texto

    def extraer_numero(self, texto: str) -> Tuple[Optional[str], str]:
        """
        Extrae el número de referencia (N.º, Nº, IN.º, etc.)
        """
        # Patrones comunes de número (incluyendo errores OCR como IN)
        patron_numero = r'\b(N\.?º|N°|IN\.?º|numero|número)\s*(\d+)'
        match = re.search(patron_numero, texto, re.IGNORECASE)

        if match:
            numero = match.group(2)
            return numero, texto

        return None, texto

    def extraer_precio(self, precio_csv: str, texto: str) -> Tuple[Optional[str], str]:
        """
        Extrae el precio. Puede venir del CSV o del texto
        Puede tener sufijos: r, c, s
        """
        if precio_csv and precio_csv.strip():
            # Limpiar el precio del CSV
            precio_limpio = re.sub(r'[^\d]', '', precio_csv)
            if precio_limpio:
                return precio_csv.strip(), texto

        # Buscar en el texto: un número al final, posiblemente con r, c, s
        patron_precio = r'\b(\d+)\s*([rcs])?\s*$'
        match = re.search(patron_precio, texto)

        if match:
            precio = match.group(1)
            if match.group(2):
                precio += match.group(2)
            return precio, texto

        return None, texto

    def extraer_lugar(self, texto: str) -> Tuple[Optional[str], str]:
        """
        Extrae el lugar de edición/publicación
        """
        # Lista de lugares comunes (en varios idiomas)
        lugares_conocidos = [
            'Madrid', 'Matriti', 'mad\.', 'Barcelona', 'Sevilla', 'Valencia',
            'Zaragoza', 'Lisboa', 'Paris', 'Parisiis', 'Rome', 'Roma', 'Romae',
            'London', 'Londres', 'Venetiis', 'Venecia', 'Venice', 'Lugduni',
            'Lyon', 'Basilea', 'Basileæ', 'Antuerpiæ', 'Amberes', 'Antwerp',
            'Coloniae', 'Colonia', 'Salamanca', 'Salmanticae', 'Salmant\.',
            'Hispani', 'Lugd\. Batav\.', 'Lugduni Batavorum', 'Leiden',
            'Firenze', 'Florence', 'Turino', 'Turin', 'Cadiz', 'Pamplona',
            'Burgos', 'Granada', 'Gramatae', 'Alcalá', 'Compluti',
            'La Haye', 'Argentorati', 'Strasbourg', 'Anverpie', 'Antuerpiae',
            'Malta', 'Lugo', 'Lecce', 'Ibid', 'Salmanitae', 'Smeting',
            'Hemsterdamii', 'Amsterdam', 'Rost\.', 'Soetingae', 'Gottingen',
            'Lutetis Parisiorum', 'Coloniae Allobrogum', 'Geneva', 'Ginebra',
            'Fudel', 'Paut\.', 'Hispani'
        ]

        # Crear patrón con todos los lugares
        patron_lugares = '|'.join(lugares_conocidos)
        patron = r'\b(' + patron_lugares + r')\b'

        match = re.search(patron, texto, re.IGNORECASE)

        if match:
            lugar = match.group(1)
            # Normalizar algunos nombres comunes
            normalizaciones = {
                'mad.': 'Madrid',
                'Matriti': 'Madrid',
                'Parisiis': 'Paris',
                'Romae': 'Roma',
                'Venetiis': 'Venecia',
                'Basileæ': 'Basilea',
                'Antuerpiæ': 'Amberes',
                'Salmanticae': 'Salamanca',
                'Salmant.': 'Salamanca',
                'Lugduni Batavorum': 'Leiden',
                'Lugd. Batav.': 'Leiden',
                'Coloniae Allobrogum': 'Ginebra',
                'Lutetis Parisiorum': 'Paris',
                'Anverpie': 'Amberes',
                'Antuerpiae': 'Amberes',
                'Hemsterdamii': 'Amsterdam',
                'Argentorati': 'Estrasburgo',
                'Compluti': 'Alcalá de Henares',
            }

            lugar_normalizado = normalizaciones.get(lugar, lugar)
            return lugar_normalizado, texto

        return None, texto

    def extraer_titulo(self, texto: str, autor: Optional[str]) -> str:
        """
        Extrae el título (todo lo que queda después del autor y antes de los metadatos)
        """
        # Eliminar referencias a autor anterior
        texto = re.sub(r'^(id\.|Ejusd\.|Idem|Ejusdem)\s*', '', texto, flags=re.IGNORECASE)

        # El título es generalmente todo hasta que encontramos:
        # - Un formato (fol., 4º, 8º, etc.)
        # - Un año de 4 dígitos
        # - Una ciudad conocida

        # Primero intentar encontrar el inicio de los metadatos
        patrones_fin_titulo = [
            r'\b(fol\.|4º|4°|8º|8°|12º|12°|16º|16°)\b',
            r'\b(1[4-7]\d{2}|1800)\b',
            r'\b(Madrid|Matriti|Paris|Roma|Londres|Sevilla)\b',
        ]

        posiciones = []
        for patron in patrones_fin_titulo:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                posiciones.append(match.start())

        if posiciones:
            fin_titulo = min(posiciones)
            titulo = texto[:fin_titulo].strip()
        else:
            # Si no encontramos metadatos claros, tomar una parte razonable
            titulo = texto[:200].strip()

        # Limpiar el título
        titulo = re.sub(r'\s+', ' ', titulo)
        titulo = titulo.strip('.,;: ')

        return titulo

    def procesar_entrada(self, fila: Dict) -> Dict:
        """
        Procesa una entrada completa del catálogo
        """
        transcripcion = fila.get('Transcripcion', '')
        precio_csv = fila.get('Precio', '')

        if not transcripcion or transcripcion.strip() == '':
            return None

        self.estadisticas['total_procesadas'] += 1

        # Crear registro de salida
        registro = {
            'volumen': fila.get('Volumen', ''),
            'pagina': fila.get('Filename', ''),
            'fila_original': fila.get('Fila', ''),
            'transcripcion_original': transcripcion,
        }

        # Procesar autor
        autor, texto_restante = self.extraer_autor(transcripcion)
        registro['autor'] = autor if autor else '[Anónimo]'

        # Extraer título
        titulo = self.extraer_titulo(texto_restante, autor)
        registro['titulo'] = titulo

        # Extraer formato
        formato, _ = self.extraer_formato(transcripcion)
        registro['formato'] = formato

        # Extraer tomos
        tomos, _ = self.extraer_tomos(transcripcion)
        registro['tomos'] = tomos

        # Extraer figuras
        tiene_figuras, _ = self.extraer_figuras(transcripcion)
        registro['figuras'] = 'Sí' if tiene_figuras else 'No'

        # Extraer pasta
        pasta, _ = self.extraer_pasta(transcripcion)
        registro['pasta'] = pasta if pasta else 'No especificado'

        # Extraer lugar
        lugar, _ = self.extraer_lugar(transcripcion)
        registro['lugar'] = lugar

        # Extraer año
        año, _ = self.extraer_año(transcripcion)
        registro['año'] = año

        # Extraer atado
        atado, _ = self.extraer_atado(transcripcion)
        registro['atado'] = atado

        # Extraer número
        numero, _ = self.extraer_numero(transcripcion)
        registro['numero'] = numero

        # Extraer precio
        precio, _ = self.extraer_precio(precio_csv, transcripcion)
        registro['precio'] = precio

        return registro

    def procesar_catalogo(self, archivo_entrada: str, archivo_salida: str):
        """
        Procesa todo el catálogo
        """
        registros_procesados = []

        print(f"Procesando catálogo: {archivo_entrada}")
        print("=" * 80)

        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for idx, fila in enumerate(reader, 1):
                if idx % 100 == 0:
                    print(f"Procesadas {idx} entradas...")

                registro = self.procesar_entrada(fila)
                if registro:
                    registros_procesados.append(registro)

        print(f"\nTotal de entradas procesadas: {len(registros_procesados)}")

        # Guardar resultados
        if registros_procesados:
            campos = [
                'volumen', 'pagina', 'fila_original', 'autor', 'titulo',
                'formato', 'tomos', 'figuras', 'pasta', 'lugar', 'año',
                'atado', 'numero', 'precio', 'transcripcion_original'
            ]

            with open(archivo_salida, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(registros_procesados)

            print(f"\nResultados guardados en: {archivo_salida}")

        return registros_procesados

    def generar_reporte_estadisticas(self, archivo_reporte: str):
        """
        Genera un reporte con estadísticas del procesamiento
        """
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE DE ANÁLISIS DEL CATÁLOGO DE LIBROS\n")
            f.write("=" * 80 + "\n\n")

            f.write("ESTADÍSTICAS GENERALES\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total de entradas procesadas: {self.estadisticas['total_procesadas']}\n")
            f.write(f"Entradas con autor identificado: {self.estadisticas['con_autor']}\n")
            f.write(f"Referencias resueltas (id., it., Ejusd., etc.): {self.referencias_resueltas}\n")
            f.write(f"Entradas anónimas: {self.estadisticas['anonimos']}\n")
            f.write(f"Entradas con año: {self.estadisticas['con_año']}\n")
            f.write(f"Entradas sin año: {self.estadisticas['sin_año']}\n\n")

            if self.lugares_dudosos:
                f.write("LUGARES DUDOSOS (requieren verificación en CERL)\n")
                f.write("-" * 80 + "\n")
                for lugar in set(self.lugares_dudosos):
                    f.write(f"  - {lugar}\n")
                f.write("\n")

            if self.errores:
                f.write("ERRORES Y ADVERTENCIAS\n")
                f.write("-" * 80 + "\n")
                for error in self.errores[:100]:  # Primeros 100 errores
                    f.write(f"  - {error}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("Fin del reporte\n")

        print(f"\nReporte de estadísticas guardado en: {archivo_reporte}")


def main():
    """
    Función principal
    """
    procesador = ProcesadorCatalogo()

    # Procesar el catálogo
    registros = procesador.procesar_catalogo(
        '/home/user/Velasco/catalogo.csv',
        '/home/user/Velasco/catalogo_depurado.csv'
    )

    # Generar reporte
    procesador.generar_reporte_estadisticas(
        '/home/user/Velasco/reporte_analisis.txt'
    )

    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)
    print(f"Archivo depurado: catalogo_depurado.csv")
    print(f"Reporte: reporte_analisis.txt")


if __name__ == '__main__':
    main()
