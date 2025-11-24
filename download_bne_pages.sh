#!/bin/bash

# Script para descargar páginas de la colección BNE de Fernando José de Velasco
# URL base: https://datos.bne.es/fondos/Fernando%20Jos%C3%A9%20de%20Velasco%20y%20Ceballos%20(1707-1788)/XX859170/

BASE_URL="https://datos.bne.es/fondos/Fernando%20Jos%C3%A9%20de%20Velasco%20y%20Ceballos%20(1707-1788)/XX859170"
OUTPUT_DIR="bne_pages"

# Crear directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"

echo "Iniciando descarga de 180 páginas..."
echo "Directorio de salida: $OUTPUT_DIR"
echo ""

# Iterar desde página 1 hasta 180
for page in {1..180}; do
    output_file="$OUTPUT_DIR/page_$(printf "%03d" $page).txt"
    url="$BASE_URL/$page"

    echo "[$page/180] Descargando: $url"

    # Descargar la página
    curl -s "$url" > "$output_file"

    # Verificar si la descarga fue exitosa
    if [ $? -eq 0 ]; then
        file_size=$(wc -c < "$output_file")
        echo "  ✓ Guardado en: $output_file (${file_size} bytes)"
    else
        echo "  ✗ Error al descargar la página $page"
    fi

    # Esperar 3 segundos antes de la siguiente descarga (excepto en la última)
    if [ $page -lt 180 ]; then
        sleep 3
    fi

    echo ""
done

echo "Descarga completada. Total de páginas: 180"
echo "Archivos guardados en: $OUTPUT_DIR/"
