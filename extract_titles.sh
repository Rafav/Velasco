#!/bin/bash

# Script para extraer títulos de las páginas descargadas de BNE
# Procesa los 180 archivos .txt y extrae los títulos

INPUT_DIR="bne_pages"
OUTPUT_FILE="titulos_velasco.txt"

# Limpiar archivo de salida si existe
> "$OUTPUT_FILE"

echo "Extrayendo títulos de los archivos en $INPUT_DIR..."
echo ""

# Contador de títulos extraídos
total_titles=0

# Procesar cada archivo
for page_file in "$INPUT_DIR"/page_*.txt; do
    if [ ! -f "$page_file" ]; then
        continue
    fi

    page_num=$(basename "$page_file" .txt | sed 's/page_//')
    echo "Procesando: $page_file (página $page_num)"

    # Extraer el contenido del atributo title de los divs con class="search-item resource/"
    # Usar grep para encontrar las líneas, luego sed para extraer el título
    grep -o 'title="[^"]*" class="search-item resource/"' "$page_file" | \
    sed 's/title="//;s/" class="search-item resource\/"$//' | \
    while IFS= read -r title_content; do
        # Decodificar HTML entities y extraer el título entre <strong> y </strong>
        title=$(echo "$title_content" | \
            sed 's/&lt;/</g; s/&gt;/>/g; s/&quot;/"/g; s/&amp;/\&/g; s/&#039;/'\''/g' | \
            grep -oP '<strong>\K[^<]+' | head -1)

        if [ -n "$title" ]; then
            # Convertir caracteres UTF-8 mal codificados (Ã± → ñ, etc.)
            # Guardar el título en el archivo de salida
            echo "$title" >> "$OUTPUT_FILE"
            ((total_titles++))
        fi
    done
done

echo ""
echo "Extracción completada."
echo "Total de títulos extraídos: $total_titles"
echo "Archivo de salida: $OUTPUT_FILE"

# Mostrar los primeros 10 títulos como muestra
echo ""
echo "Primeros 10 títulos extraídos:"
head -10 "$OUTPUT_FILE"
