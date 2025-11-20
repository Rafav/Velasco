#!/bin/bash

# Script ultra-optimizado para dividir páginas dobles de un PDF escaneado
# Usa pdftoppm + jpegtran (sin recompresión JPEG = más rápido y sin pérdida)
# Uso: ./split_pdf_fast.sh archivo.pdf [carpeta_salida] [dpi] [pagina_inicio] [pagina_fin]

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Uso: $0 archivo.pdf [carpeta_salida] [dpi] [pagina_inicio] [pagina_fin]"
    echo "Ejemplo: $0 manuscrito.pdf output 300"
    echo "Ejemplo: $0 manuscrito.pdf output 300 1 10  # Solo páginas 1-10"
    exit 1
fi

PDF_FILE="$1"
OUTPUT_DIR="${2:-output_images}"
DPI="${3:-300}"
START_PAGE="${4:-1}"
END_PAGE="${5:-99999}"

# Validaciones
if [ ! -f "$PDF_FILE" ]; then
    echo "Error: El archivo '$PDF_FILE' no existe." >&2
    exit 1
fi

# Verificar dependencias
for cmd in pdftoppm pdfinfo identify jpegtran; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: '$cmd' no está instalado." >&2
        case "$cmd" in
            pdftoppm|pdfinfo)
                echo "Instálalo con: sudo apt install poppler-utils"
                ;;
            identify)
                echo "Instálalo con: sudo apt install imagemagick"
                ;;
            jpegtran)
                echo "Instálalo con: sudo apt install libjpeg-turbo-progs"
                ;;
        esac
        exit 1
    fi
done

mkdir -p "$OUTPUT_DIR"

# Obtener número total de páginas
TOTAL_PAGES=$(pdfinfo "$PDF_FILE" 2>/dev/null | grep -i "Pages:" | awk '{print $2}')
if [ -z "$TOTAL_PAGES" ] || ! [[ "$TOTAL_PAGES" =~ ^[0-9]+$ ]]; then
    echo "Advertencia: No se pudo determinar el número total de páginas." >&2
    TOTAL_PAGES=999999
else
    echo "Total de páginas en PDF: $TOTAL_PAGES"
    if [ "$END_PAGE" -gt "$TOTAL_PAGES" ]; then
        END_PAGE="$TOTAL_PAGES"
    fi
fi

if [ "$START_PAGE" -gt "$END_PAGE" ]; then
    echo "Error: página de inicio ($START_PAGE) mayor que página final ($END_PAGE)." >&2
    exit 1
fi

echo "Procesando: $PDF_FILE"
echo "Páginas: $START_PAGE a $END_PAGE"
echo "DPI: $DPI"
echo "Carpeta de salida: $OUTPUT_DIR"
echo "----------------------------------------"

count=0

# Crear un archivo temporal base (sin extensión)
temp_base=$(mktemp --suffix=)
trap 'rm -f "${temp_base}"* 2>/dev/null' EXIT

for ((page=START_PAGE; page<=END_PAGE; page++)); do
    echo -n "Procesando página $page/$TOTAL_PAGES... "

    # pdftoppm genera: ${temp_base}-0001.jpg, ${temp_base}-0002.jpg, etc.
    if ! pdftoppm -f "$page" -l "$page" -r "$DPI" -jpeg "$PDF_FILE" "$temp_base" >/dev/null 2>&1; then
        echo "ERROR: pdftoppm falló al procesar la página $page."
        exit 1
    fi

    # Nombre real del archivo generado por pdftoppm (siempre -NNNN.jpg)
   # Buscar el único archivo .jpg que empiece con ${temp_base}-
jpeg_file=$(find "$(dirname "$temp_base")" -maxdepth 1 -name "$(basename "$temp_base")-*.jpg" | head -n1)

if [ -z "$jpeg_file" ] || [ ! -f "$jpeg_file" ]; then
    echo "ERROR: No se generó el archivo JPEG para la página $page."
    echo "Archivos temporales: $(ls -1 "${temp_base}"* 2>/dev/null || echo 'ninguno')"
    exit 1
fi

    # Obtener dimensiones
    width=$(identify -format "%w" "$jpeg_file" 2>/dev/null)
    height=$(identify -format "%h" "$jpeg_file" 2>/dev/null)
    if [ -z "$width" ] || [ -z "$height" ] || ! [[ "$width" =~ ^[0-9]+$ ]] || ! [[ "$height" =~ ^[0-9]+$ ]]; then
        echo "ERROR: No se pudieron leer las dimensiones de la imagen."
        exit 1
    fi

    # Asegurar división limpia (ancho par)
    if (( width % 2 != 0 )); then
        half_width=$(( (width - 1) / 2 ))
    else
        half_width=$(( width / 2 ))
    fi

    left_num=$(printf "%04d" $((page * 2 - 1)))
    right_num=$(printf "%04d" $((page * 2)))

    # Recortar SIN recompresión usando jpegtran
    #jpegtran -crop "${half_width}x${height}+0+0" -copy all -optimize "$jpeg_file" > "$OUTPUT_DIR/pagina_${left_num}.jpg"
    #jpegtran -crop "${half_width}x${height}+${half_width}+0" -copy all -optimize "$jpeg_file" > "$OUTPUT_DIR/pagina_${right_num}.jpg"

    jpegtran -crop "${half_width}x${height}+0+0" -copy none -progressive -optimize "$jpeg_file" > "$OUTPUT_DIR/pagina_${left_num}.jpg"
    jpegtran -crop "${half_width}x${height}+${half_width}+0" -copy none -progressive -optimize "$jpeg_file" > "$OUTPUT_DIR/pagina_${right_num}.jpg"

    # Eliminar el JPEG temporal de esta página (ahorra espacio en disco)
    rm -f "$jpeg_file"

    echo "✓ Generadas: pagina_${left_num}.jpg, pagina_${right_num}.jpg"
    ((count += 2))
done

echo "----------------------------------------"
echo "¡Completado! Se generaron $count imágenes en '$OUTPUT_DIR'"

if [ "$END_PAGE" -lt "$TOTAL_PAGES" ]; then
    echo ""
    echo "Puedes continuar desde la página $((END_PAGE + 1)) con:"
    echo "$0 \"$PDF_FILE\" \"$OUTPUT_DIR\" $DPI $((END_PAGE + 1)) $TOTAL_PAGES"
fi