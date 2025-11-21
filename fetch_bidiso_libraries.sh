#!/bin/bash
# Script para descargar información de bibliotecas BIDISO con timeout anti-DDOS

URLS=(
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=afdddc0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=bbmdal0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=bdccad0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=bddsac0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=bdlrdp0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=bdltad0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=bdodla0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=bidela0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=cajldl0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=ceobdc0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=crjuim0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=ddvymr0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=dhdmic0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=edrfim0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=elgrec0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=fadybi0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=fpdodc0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=gdsrid0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=idldrc0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=ingade0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=inmede0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=lbdadb0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=lbdmdp0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=ldfjid0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=mbd1410000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=moarde0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=modesa0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=oavmda0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=oavmda0001"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=qufrde0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=rdltfs0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=rdsymi0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=rgdspd0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=rvaiyb0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=siabpe0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=sjccds0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=velazq0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=vifede0000"
    "https://www.bidiso.es/IBSO/BuscarEntradasPorTitulo.do?id=vjadr10000"
)

echo "Iniciando descarga de ${#URLS[@]} bibliotecas BIDISO..."
echo "Timeout entre consultas: 3 segundos"
echo ""

count=1
for url in "${URLS[@]}"; do
    id=$(echo "$url" | grep -oP 'id=\K[^&]*')
    echo "[$count/${#URLS[@]}] Consultando: $id"

    curl -s "$url" -o "bidiso_${id}.html" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "  ✓ Descargado"
    else
        echo "  ✗ Error"
    fi

    # Timeout anti-DDOS
    if [ $count -lt ${#URLS[@]} ]; then
        sleep 3
    fi

    count=$((count + 1))
done

echo ""
echo "Descarga completada. Archivos guardados en bidiso_*.html"
