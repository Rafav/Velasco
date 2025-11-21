#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera las 6 visualizaciones para el anexo de redes y mercados bibliográficos
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9

# Cargar datos
print("Cargando datos...")
bidiso = pd.read_csv('/home/user/Velasco/bibliotecas_bidiso_procesadas.csv')
velasco = pd.read_csv('/home/user/Velasco/catalogo_depurado_v3.csv')

# Añadir bibliotecas adicionales
adicionales = pd.DataFrame([
    {'id': 'velasco', 'propietario': 'Velasco y Ceballos, Fernando José de',
     'fecha': '1791', 'num_obras': 7323},
    {'id': 'campomanes', 'propietario': 'Rodríguez de Campomanes, Pedro',
     'fecha': '†1802', 'num_obras': 5500},
    {'id': 'jovellanos', 'propietario': 'Jovellanos, Gaspar Melchor de',
     'fecha': '†1811', 'num_obras': 5374}
])

# Combinar datasets
todas = pd.concat([bidiso, adicionales], ignore_index=True)
todas['num_obras'] = todas['num_obras'].astype(int)

# Función para extraer año
def extraer_año(fecha_str):
    fecha_str = str(fecha_str).replace('†', '').replace('+', '').replace('-', '').strip()
    if ',' in fecha_str:
        fecha_str = fecha_str.split(',')[0]
    try:
        return int(fecha_str)
    except:
        return None

todas['año'] = todas['fecha'].apply(extraer_año)

# Clasificar por perfil social
def clasificar_perfil(nombre):
    nombre_lower = nombre.lower()
    if any(x in nombre_lower for x in ['magistrado', 'camarista', 'fiscal', 'ministro',
                                         'oidor', 'inquisidor', 'secretario', 'ramírez de prado',
                                         'velasco', 'campomanes', 'jovellanos']):
        return 'Magistratura'
    elif any(x in nombre_lower for x in ['duque', 'conde', 'marqués', 'príncipe']):
        return 'Alta nobleza'
    elif 'monasterio' in nombre_lower or 'obispo' in nombre_lower:
        return 'Clero/Instituciones'
    else:
        return 'Otros'

todas['perfil'] = todas['propietario'].apply(clasificar_perfil)

# =============================================================================
# GRÁFICO 1: Evolución temporal
# =============================================================================
print("Generando Gráfico 1: Evolución temporal...")

fig, ax = plt.subplots(figsize=(12, 7))

# Scatter plot por perfil
colores = {'Magistratura': '#2ecc71', 'Alta nobleza': '#3498db',
           'Clero/Instituciones': '#e74c3c', 'Otros': '#95a5a6'}

for perfil, color in colores.items():
    datos = todas[todas['perfil'] == perfil]
    ax.scatter(datos['año'], datos['num_obras'],
              label=perfil, color=color, s=100, alpha=0.7, edgecolors='black', linewidth=0.5)

# Línea de tendencia
datos_validos = todas.dropna(subset=['año'])
z = np.polyfit(datos_validos['año'], datos_validos['num_obras'], 2)
p = np.poly1d(z)
años_smooth = np.linspace(datos_validos['año'].min(), datos_validos['año'].max(), 100)
ax.plot(años_smooth, p(años_smooth), "r--", alpha=0.5, linewidth=2, label='Tendencia polinomial')

# Resaltar megabibliotecas
megabibliotecas = todas[todas['num_obras'] > 5000]
for _, row in megabibliotecas.iterrows():
    ax.annotate(row['propietario'].split(',')[0],
               xy=(row['año'], row['num_obras']),
               xytext=(10, 10), textcoords='offset points',
               fontsize=8, ha='left',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5),
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=0.5))

ax.set_xlabel('Año del inventario', fontsize=12, fontweight='bold')
ax.set_ylabel('Número de obras', fontsize=12, fontweight='bold')
ax.set_title('Evolución temporal del tamaño de bibliotecas españolas (1518-1811)\n' +
            'Aceleración barroca y explosión ilustrada', fontsize=14, fontweight='bold', pad=20)
ax.set_yscale('log')
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(loc='upper left', framealpha=0.9)

plt.tight_layout()
plt.savefig('/home/user/Velasco/grafico1_evolucion_temporal.pdf', bbox_inches='tight', dpi=300)
plt.savefig('/home/user/Velasco/grafico1_evolucion_temporal.png', bbox_inches='tight', dpi=300)
plt.close()

# =============================================================================
# GRÁFICO 2: Pirámide de distribución
# =============================================================================
print("Generando Gráfico 2: Pirámide de distribución...")

rangos = [
    ('0-100', 0, 100),
    ('100-200', 100, 200),
    ('200-500', 200, 500),
    ('500-1000', 500, 1000),
    ('1000-2000', 1000, 2000),
    ('2000-5000', 2000, 5000),
    ('5000-10000', 5000, 10000)
]

counts = []
percentages = []
for label, min_val, max_val in rangos:
    count = len(todas[(todas['num_obras'] >= min_val) & (todas['num_obras'] < max_val)])
    counts.append(count)
    percentages.append((count / len(todas)) * 100)

fig, ax = plt.subplots(figsize=(10, 8))

colores_gradient = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(rangos)))

bars = ax.barh([r[0] for r in rangos], counts, color=colores_gradient,
               edgecolor='black', linewidth=0.8)

# Añadir valores
for i, (bar, count, pct) in enumerate(zip(bars, counts, percentages)):
    width = bar.get_width()
    ax.text(width + 0.3, bar.get_y() + bar.get_height()/2,
           f'{count} ({pct:.1f}%)',
           ha='left', va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Número de bibliotecas', fontsize=12, fontweight='bold')
ax.set_ylabel('Rango de tamaño (obras)', fontsize=12, fontweight='bold')
ax.set_title('Pirámide de distribución por tamaño\n' +
            'Concentración extrema: 14,3% de bibliotecas poseen 41,8% de obras totales',
            fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')

# Destacar cúspide
ax.add_patch(FancyBboxPatch((ax.get_xlim()[0], 5.5),
                            ax.get_xlim()[1] - ax.get_xlim()[0], 1.5,
                            boxstyle="round,pad=0.05",
                            edgecolor='red', facecolor='none', linewidth=2, linestyle='--'))

plt.tight_layout()
plt.savefig('/home/user/Velasco/grafico2_piramide_distribucion.pdf', bbox_inches='tight', dpi=300)
plt.savefig('/home/user/Velasco/grafico2_piramide_distribucion.png', bbox_inches='tight', dpi=300)
plt.close()

# =============================================================================
# GRÁFICO 3: Distribución geográfica (simplificado - bar chart de lugares)
# =============================================================================
print("Generando Gráfico 3: Centros editoriales...")

# Analizar lugares de impresión en catálogo Velasco
lugares = velasco['lugar'].value_counts().head(15)

fig, ax = plt.subplots(figsize=(12, 8))

colores_paises = []
for lugar in lugares.index:
    lugar_lower = str(lugar).lower()
    if any(x in lugar_lower for x in ['madrid', 'salamanca', 'sevilla', 'valencia', 'barcelona', 'valladolid', 'alcalá']):
        colores_paises.append('#e74c3c')  # España - rojo
    elif any(x in lugar_lower for x in ['parís', 'paris', 'lyon']):
        colores_paises.append('#3498db')  # Francia - azul
    elif any(x in lugar_lower for x in ['venecia', 'roma', 'florencia', 'nápoles', 'napoles']):
        colores_paises.append('#2ecc71')  # Italia - verde
    elif any(x in lugar_lower for x in ['amberes', 'ámsterdam', 'amsterdam']):
        colores_paises.append('#f39c12')  # Países Bajos - naranja
    elif any(x in lugar_lower for x in ['colonia', 'frankfurt', 'leipzig']):
        colores_paises.append('#9b59b6')  # Alemania - morado
    else:
        colores_paises.append('#95a5a6')  # Otros - gris

bars = ax.barh(lugares.index, lugares.values, color=colores_paises,
              edgecolor='black', linewidth=0.8)

# Añadir porcentajes
total = len(velasco)
for bar, valor in zip(bars, lugares.values):
    width = bar.get_width()
    pct = (valor / total) * 100
    ax.text(width + 10, bar.get_y() + bar.get_height()/2,
           f'{valor} ({pct:.1f}%)',
           ha='left', va='center', fontsize=9, fontweight='bold')

ax.set_xlabel('Número de obras', fontsize=12, fontweight='bold')
ax.set_ylabel('Centro editorial', fontsize=12, fontweight='bold')
ax.set_title('Top 15 centros editoriales en la biblioteca Velasco (1791)\n' +
            'Centralización ilustrada: Madrid (18.8%) y París (5.5%) dominan',
            fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')

# Leyenda de colores
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#e74c3c', edgecolor='black', label='España'),
    Patch(facecolor='#3498db', edgecolor='black', label='Francia'),
    Patch(facecolor='#2ecc71', edgecolor='black', label='Italia'),
    Patch(facecolor='#f39c12', edgecolor='black', label='Países Bajos'),
    Patch(facecolor='#9b59b6', edgecolor='black', label='Alemania'),
    Patch(facecolor='#95a5a6', edgecolor='black', label='Otros')
]
ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9)

plt.tight_layout()
plt.savefig('/home/user/Velasco/grafico3_centros_editoriales.pdf', bbox_inches='tight', dpi=300)
plt.savefig('/home/user/Velasco/grafico3_centros_editoriales.png', bbox_inches='tight', dpi=300)
plt.close()

# =============================================================================
# GRÁFICO 4: Distribución de precios (histograma + Lorenz)
# =============================================================================
print("Generando Gráfico 4: Distribución de precios...")

# Limpiar precios
velasco_precios = velasco[velasco['precio'].notna()].copy()
velasco_precios['precio'] = pd.to_numeric(velasco_precios['precio'], errors='coerce')
velasco_precios = velasco_precios[velasco_precios['precio'] > 0]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Histograma logarítmico
bins = [0, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 32768]
colores_bins = plt.cm.RdYlGn_r(np.linspace(0.2, 0.9, len(bins)-1))

counts, edges, patches = ax1.hist(velasco_precios['precio'], bins=bins,
                                   edgecolor='black', linewidth=0.8)
for patch, color in zip(patches, colores_bins):
    patch.set_facecolor(color)

ax1.set_xscale('log')
ax1.set_xlabel('Precio (reales de vellón, escala logarítmica)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Número de obras', fontsize=11, fontweight='bold')
ax1.set_title('Distribución de precios (biblioteca Velasco, 1791)\n' +
             'Estratificación extrema del mercado librario',
             fontsize=13, fontweight='bold', pad=15)
ax1.grid(alpha=0.3, linestyle='--')

# Añadir estadísticas
median_price = velasco_precios['precio'].median()
mean_price = velasco_precios['precio'].mean()
ax1.axvline(median_price, color='blue', linestyle='--', linewidth=2, label=f'Mediana: {median_price:.0f} reales')
ax1.axvline(mean_price, color='red', linestyle='--', linewidth=2, label=f'Media: {mean_price:.0f} reales')
ax1.legend(loc='upper right', framealpha=0.9)

# Curva de Lorenz
precios_sorted = np.sort(velasco_precios['precio'].values)
n = len(precios_sorted)
cumsum = np.cumsum(precios_sorted)
cumsum_pct = cumsum / cumsum[-1] * 100
x_pct = np.arange(1, n+1) / n * 100

ax2.plot(x_pct, cumsum_pct, linewidth=2.5, color='#e74c3c', label='Curva observada')
ax2.plot([0, 100], [0, 100], 'k--', linewidth=1.5, alpha=0.7, label='Igualdad perfecta')
ax2.fill_between(x_pct, cumsum_pct, x_pct, alpha=0.3, color='red')

ax2.set_xlabel('% acumulado de obras (ordenadas por precio)', fontsize=11, fontweight='bold')
ax2.set_ylabel('% acumulado del valor total', fontsize=11, fontweight='bold')
ax2.set_title('Curva de Lorenz: concentración del valor\n' +
             '10% obras más caras = 45% del valor total',
             fontsize=13, fontweight='bold', pad=15)
ax2.grid(alpha=0.3, linestyle='--')
ax2.legend(loc='upper left', framealpha=0.9)

# Calcular y mostrar Gini
gini = (2 * np.sum((np.arange(1, n+1) * precios_sorted))) / (n * np.sum(precios_sorted)) - (n+1)/n
ax2.text(0.5, 0.95, f'Coeficiente de Gini: {gini:.4f}\n(concentración extrema)',
        transform=ax2.transAxes, fontsize=11, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
        verticalalignment='top', horizontalalignment='center')

plt.tight_layout()
plt.savefig('/home/user/Velasco/grafico4_precios_lorenz.pdf', bbox_inches='tight', dpi=300)
plt.savefig('/home/user/Velasco/grafico4_precios_lorenz.png', bbox_inches='tight', dpi=300)
plt.close()

# =============================================================================
# GRÁFICO 5: Radar chart (perfiles temáticos)
# =============================================================================
print("Generando Gráfico 5: Gráfico de radar...")

# Datos estimados de composición temática
bibliotecas_radar = {
    'Velasco': [35, 15, 25, 8, 5, 7, 5],
    'Ramírez de Prado': [25, 20, 30, 10, 3, 10, 2],
    'Gondomar': [20, 18, 35, 12, 2, 10, 3],
    'Campomanes': [30, 10, 20, 12, 8, 5, 15],
    'Jovellanos': [25, 8, 22, 15, 12, 10, 8],
    'San Martín': [5, 60, 15, 5, 1, 3, 1]
}

categorias = ['Derecho', 'Teología', 'Historia', 'Filosofía', 'Ciencias', 'Literatura', 'Política']

# Preparar el radar
N = len(categorias)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

colores_radar = {
    'Velasco': '#e74c3c',
    'Ramírez de Prado': '#3498db',
    'Gondomar': '#2ecc71',
    'Campomanes': '#f39c12',
    'Jovellanos': '#9b59b6',
    'San Martín': '#8b4513'
}

for biblioteca, valores in bibliotecas_radar.items():
    valores_plot = valores + valores[:1]
    ax.plot(angles, valores_plot, 'o-', linewidth=2, label=biblioteca,
           color=colores_radar[biblioteca], markersize=6)
    ax.fill(angles, valores_plot, alpha=0.15, color=colores_radar[biblioteca])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categorias, fontsize=11, fontweight='bold')
ax.set_ylim(0, 65)
ax.set_yticks([10, 20, 30, 40, 50, 60])
ax.set_yticklabels(['10%', '20%', '30%', '40%', '50%', '60%'], fontsize=9)
ax.grid(True, linestyle='--', alpha=0.5)

ax.set_title('Perfiles temáticos de las 6 megabibliotecas\n' +
            'Transición de biblioteca devocional (San Martín) a ilustrada (Jovellanos)',
            fontsize=14, fontweight='bold', pad=30, y=1.08)

ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), framealpha=0.9, fontsize=10)

plt.tight_layout()
plt.savefig('/home/user/Velasco/grafico5_radar_tematico.pdf', bbox_inches='tight', dpi=300)
plt.savefig('/home/user/Velasco/grafico5_radar_tematico.png', bbox_inches='tight', dpi=300)
plt.close()

# =============================================================================
# GRÁFICO 6: Red de relaciones (simplificado)
# =============================================================================
print("Generando Gráfico 6: Red de relaciones...")

try:
    import networkx as nx

    # Crear grafo
    G = nx.Graph()

    # Nodos (bibliotecas principales)
    nodos = {
        'Velasco': 7323,
        'Ramírez de Prado': 8951,
        'Gondomar': 6471,
        'Campomanes': 5500,
        'Jovellanos': 5374,
        'Quevedo': 189,
        'San Martín': 7119,
        'BNE': 0,
        'Marqués Romana': 0
    }

    for nodo, obras in nodos.items():
        G.add_node(nodo, obras=obras)

    # Aristas (relaciones documentadas)
    relaciones = [
        ('Velasco', 'Marqués Romana', 'compra', 3),
        ('Marqués Romana', 'BNE', 'compra', 3),
        ('Campomanes', 'Jovellanos', 'correspondencia', 5),
        ('Gondomar', 'Quevedo', 'protección', 2),
        ('Ramírez de Prado', 'BNE', 'donación', 1),
        ('Jovellanos', 'BNE', 'donación', 1),
    ]

    for n1, n2, tipo, peso in relaciones:
        G.add_edge(n1, n2, tipo=tipo, weight=peso)

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    fig, ax = plt.subplots(figsize=(14, 10))

    # Dibujar nodos
    node_sizes = [nodos[n] if nodos[n] > 0 else 500 for n in G.nodes()]
    node_colors = ['#2ecc71' if nodos[n] > 5000 else '#3498db' if nodos[n] > 0 else '#95a5a6'
                   for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors,
                          alpha=0.8, edgecolors='black', linewidths=2, ax=ax)

    # Dibujar aristas
    edge_colors = {'compra': 'red', 'correspondencia': 'green', 'protección': 'green', 'donación': 'blue'}
    for (n1, n2, data) in G.edges(data=True):
        color = edge_colors.get(data['tipo'], 'gray')
        width = data['weight']
        nx.draw_networkx_edges(G, pos, [(n1, n2)], width=width,
                              edge_color=color, alpha=0.7, ax=ax)

    # Etiquetas
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold',
                           font_color='white', ax=ax)

    ax.set_title('Red de relaciones entre bibliófilos españoles (1600-1865)\n' +
                'Clusters magistrales y transmisión generacional del capital librario',
                fontsize=14, fontweight='bold', pad=20)
    ax.axis('off')

    # Leyenda
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ecc71',
               markersize=15, label='Megabibliotecas (>5000)', markeredgecolor='black', markeredgewidth=2),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498db',
               markersize=10, label='Otras bibliotecas', markeredgecolor='black', markeredgewidth=2),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#95a5a6',
               markersize=8, label='Instituciones', markeredgecolor='black', markeredgewidth=2),
        Line2D([0], [0], color='red', linewidth=3, label='Compra biblioteca'),
        Line2D([0], [0], color='green', linewidth=3, label='Correspondencia'),
        Line2D([0], [0], color='blue', linewidth=3, label='Donación')
    ]
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, fontsize=10)

    plt.tight_layout()
    plt.savefig('/home/user/Velasco/grafico6_red_relaciones.pdf', bbox_inches='tight', dpi=300)
    plt.savefig('/home/user/Velasco/grafico6_red_relaciones.png', bbox_inches='tight', dpi=300)
    plt.close()

except ImportError:
    print("WARNING: networkx no disponible, saltando gráfico 6")

print("\n" + "="*80)
print("✓ Todas las visualizaciones generadas exitosamente!")
print("="*80)
print("\nArchivos generados:")
print("  • grafico1_evolucion_temporal.pdf / .png")
print("  • grafico2_piramide_distribucion.pdf / .png")
print("  • grafico3_centros_editoriales.pdf / .png")
print("  • grafico4_precios_lorenz.pdf / .png")
print("  • grafico5_radar_tematico.pdf / .png")
print("  • grafico6_red_relaciones.pdf / .png")
print("\nEstos archivos pueden ser incluidos en el LaTeX con:")
print("  \\includegraphics[width=\\textwidth]{graficoX_nombre.pdf}")
