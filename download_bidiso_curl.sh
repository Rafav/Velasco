#!/bin/bash
# Script optimizado para descargar bibliotecas BIDISO con curl

URLS=(
    "afdddc0000" "bbmdal0000" "bdccad0000" "bddsac0000" "bdlrdp0000"
    "bdltad0000" "bdodla0000" "bidela0000" "cajldl0000" "ceobdc0000"
    "crjuim0000" "ddvymr0000" "dhdmic0000" "edrfim0000" "elgrec0000"
    "fadybi0000" "fpdodc0000" "gdsrid0000" "idldrc0000" "ingade0000"
    "inmede0000" "lbdadb0000" "lbdmdp0000" "ldfjid0000" "mbd1410000"
    "moarde0000" "modesa0000" "oavmda0000" "oavmda0001" "qufrde0000"
    "rdltfs0000" "rdsymi0000" "rgdspd0000" "rvaiyb0000" "siabpe0000"
    "sjccds0000" "velazq0000" "vifede0000" "vjadr10000"
)

mkdir -p bidiso_data
cd bidiso_data

echo "Descargando ${#URLS[@]} bibliotecas BIDISO..."
echo "Inicio: $(date)"
echo ""

for i in "${!URLS[@]}"; do
    id="${URLS[$i]}"
    num=$((i + 1))

    echo "[$num/${#URLS[@]}] Descargando: $id"

    curl -s "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=$id" \
         -o "${id}.html" \
         -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

    if [ $? -eq 0 ]; then
        size=$(wc -c < "${id}.html")
        if [ $size -gt 1000 ]; then
            echo "  ✓ OK (${size} bytes)"
        else
            echo "  ✗ ERROR (archivo muy pequeño)"
        fi
    else
        echo "  ✗ ERROR de descarga"
    fi

    # Timeout anti-DDOS (excepto última iteración)
    if [ $num -lt ${#URLS[@]} ]; then
        sleep 3
    fi
done

echo ""
echo "Descarga completada: $(date)"
echo "Archivos en: $(pwd)"
ls -lh *.html 2>/dev/null | wc -l
