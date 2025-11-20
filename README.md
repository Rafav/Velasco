# Velasco - Sistema de Digitalización de Catálogos Históricos

Sistema automatizado para la digitalización y procesamiento de inventarios históricos de catálogos bibliográficos mediante OCR con IA (Qwen-VL) y procesamiento estructurado de datos.

## Descripción General

Este proyecto procesa imágenes de catálogos antiguos de inventarios de libros (autores, títulos, precios, fechas, lugares de edición, etc.) y las convierte en datos estructurados utilizando modelos de visión multimodal y técnicas avanzadas de procesamiento de datos.

## Características Principales

- **OCR con IA**: Utiliza Qwen3-VL-Plus para extracción inteligente de texto desde imágenes
- **Procesamiento Reanudable**: Sistema de checkpoints para procesar grandes volúmenes de imágenes
- **Extracción Estructurada**: Convierte JSON anidados en CSV planos con todas las columnas
- **Mapeo Inteligente**: Fusiona columnas similares (autor/author, precio/price, etc.)
- **Cálculo de Tokens**: Optimización de costos mediante cálculo preciso de tokens de imagen
- **Reportes Detallados**: Generación automática de reportes de completitud y estadísticas

## Flujo de Trabajo

```
Imágenes JPG → OCR (reanudable.py) → JSON bruto →
→ Extracción (extraer_todo_crudo.py) → CSV crudo →
→ Mapeo (reprocesar_con_mapeo.py) → CSV procesado
```

## Archivos del Proyecto

### 1. Scripts de OCR

#### `reanudable.py`
Script principal de procesamiento OCR con sistema de progreso reanudable.

**Características:**
- Procesa imágenes en orden (`pagina_0001.jpg`, `pagina_0002.jpg`, etc.)
- Guarda progreso en `progreso.json` para reanudar en caso de interrupción
- Genera respuestas completas y OCR extraído para cada página
- Registro de errores en `errores.log`

**Uso:**
```bash
python reanudable.py
```

**Configuración:**
```python
CARPETA_IMAGENES = "/ruta/a/imagenes/"
CARPETA_SALIDA = "salida_ocr"
```

**Salida:**
- `salida_ocr/pagina_XXXX.json` - OCR extraído
- `salida_ocr/pagina_XXXX.full_response.json` - Respuesta completa de la API
- `progreso.json` - Estado del procesamiento
- `errores.log` - Registro de errores

#### `ocr.py`
Script básico de prueba de OCR para una sola imagen.

**Uso:**
```bash
python ocr.py
```

#### `calculo-tokens.py`
Calculadora de tokens para imágenes según el modelo Qwen-VL.

**Características:**
- Calcula dimensiones escaladas según restricciones del modelo
- Estima número de tokens (importante para costos)
- Soporta límites de 4 a 1280 tokens por imagen

**Uso:**
```bash
python calculo-tokens.py
```

### 2. Scripts de Procesamiento de Datos

#### `extraer_todo_crudo.py`
Extractor robusto que procesa archivos JSON de OCR y genera CSV con todas las columnas detectadas.

**Características:**
- Extrae TODOS los datos sin normalización
- Aplana estructuras JSON anidadas (notación punto: `obra.titulo`)
- Genera reporte de frecuencia de columnas
- Preserva valores originales tal cual

**Uso:**
```bash
python extraer_todo_crudo.py /ruta/a/archivos/json/
```

**Salida:**
- `output_crudo/datos_crudos.csv` - Todos los datos extraídos
- `output_crudo/reporte_columnas.txt` - Frecuencia de cada columna

**Columnas generadas:**
- `id_fila`: Identificador secuencial
- `archivo_origen`: Nombre del archivo JSON
- `numero_pagina`: Número de página extraído
- `array_origen`: Array JSON del que proviene el item
- + Todas las columnas encontradas en los JSON

#### `reprocesar_con_mapeo.py`
Procesador avanzado que aplica mapeo de columnas para consolidar datos dispersos.

**Características:**
- Fusiona columnas sinónimas según prioridad definida
- Mantiene valores originales sin normalización
- Genera campo `transcripcion` con todos los datos concatenados
- Genera campo `notas` con datos no mapeados
- Reportes de completitud y estadísticas

**Uso:**
```bash
python reprocesar_con_mapeo.py
```

**Mapeo de Columnas:**
```python
'autor': ['autor', 'author', 'autores']
'titulo': ['titulo', 'title', 'obra', 'obra.titulo']
'precio': ['precio', 'price', 'precio_total', 'obra.precio']
'anio': ['anio', 'año', 'year', 'fecha']
'lugar': ['lugar_edicion', 'lugar', 'place']
# ... y más
```

**Salida:**
- `output_final/catalogo_procesado.csv` - Datos consolidados
- `output_final/reporte_procesamiento.txt` - Mapeo aplicado y completitud
- `output_final/estadisticas.txt` - Estadísticas básicas y top autores

#### `Qwen_python_20251013_wf0bu4ynl.py` y `qwen-precio.py`
Conversores simples de JSON a CSV con extracción de valores.

**Características:**
- Extracción recursiva de valores primitivos
- Búsqueda de campos de precio
- Manejo de formatos numéricos variados

**Uso:**
```bash
python qwen-precio.py /ruta/directorio/json/
```

**Salida:**
- `output_simple.csv` con columnas: `filename`, `fila`, `price`, `transcripcion`

## Requisitos

### Dependencias Python

```bash
pip install dashscope pillow
```

### Variables de Entorno

```bash
export DASHSCOPE_API_KEY="tu-api-key"
```

### Estructura de Directorios Recomendada

```
proyecto/
├── a_jpg_afinado/           # Imágenes JPG de entrada
│   ├── pagina_0001.jpg
│   ├── pagina_0002.jpg
│   └── ...
├── salida_ocr/              # JSONs generados por OCR
├── output_crudo/            # CSV crudo y reportes
├── output_final/            # CSV procesado final
├── progreso.json            # Estado del procesamiento
└── errores.log              # Log de errores
```

## Guía de Uso Paso a Paso

### Paso 1: Preparar Imágenes

Asegúrate de que las imágenes estén nombradas secuencialmente:
```
pagina_0001.jpg
pagina_0002.jpg
pagina_0003.jpg
...
```

### Paso 2: Ejecutar OCR

```bash
# Configurar API key
export DASHSCOPE_API_KEY="tu-api-key"

# Ejecutar procesamiento OCR (reanudable)
python reanudable.py
```

El script procesará todas las imágenes y guardará el progreso. Si se interrumpe, se puede reanudar desde donde quedó.

### Paso 3: Extraer Datos Crudos

```bash
python extraer_todo_crudo.py salida_ocr/
```

Esto genera:
- `output_crudo/datos_crudos.csv` - Todos los datos sin procesar
- `output_crudo/reporte_columnas.txt` - Análisis de columnas

### Paso 4: Revisar y Ajustar Mapeo

1. Abre `output_crudo/datos_crudos.csv` en Excel/LibreOffice
2. Revisa `output_crudo/reporte_columnas.txt` para ver todas las columnas
3. Si necesitas ajustar el mapeo, edita `MAPEO_COLUMNAS` en `reprocesar_con_mapeo.py`

### Paso 5: Procesar con Mapeo

```bash
python reprocesar_con_mapeo.py
```

Esto genera:
- `output_final/catalogo_procesado.csv` - Datos consolidados
- `output_final/reporte_procesamiento.txt` - Reporte de mapeo
- `output_final/estadisticas.txt` - Estadísticas del catálogo

## Estructura de Datos

### CSV Crudo (`datos_crudos.csv`)

Columnas principales:
- `id_fila`: ID único
- `archivo_origen`: Archivo JSON fuente
- `numero_pagina`: Número de página
- `array_origen`: Array JSON de origen
- Todas las columnas detectadas en formato plano

### CSV Procesado (`catalogo_procesado.csv`)

Columnas estándar:
- **Metadata**: `id_fila`, `archivo_origen`, `numero_pagina`, `array_origen`
- **Campos principales**: `autor`, `traductor`, `titulo`, `precio`, `anio`, `lugar`, `formato`
- **Campos secundarios**: `volumen`, `paginas`, `editorial`, `editor`, `idioma`, `edicion`
- **Campos especiales**: `transcripcion` (todos los datos concatenados), `notas` (datos no mapeados)

## Configuración del Modelo Qwen-VL

### Parámetros de Imagen

```python
min_pixels = 65536           # Mínimo de píxeles
max_pixels = 28 * 28 * 8192  # Máximo de píxeles
```

### Prompt de OCR

```
"ocr a json. Es un inventario de catálogo de autores, libros, datos, precios, y sumas.
Respeta el castellano y latín. Mantén los datos de precios y números, también los de páginas"
```

### Cálculo de Costos

Para calcular el costo estimado:

```bash
python calculo-tokens.py
```

Fórmula: `tokens = (alto_escalado × ancho_escalado) / (32 × 32) + 2`

## Arrays JSON Soportados

El sistema busca automáticamente los siguientes arrays en los JSON:

- `inventario`
- `entries`
- `inventory_entries`
- `catalog_entries`
- `entradas`
- `contenido`
- `items`
- `content`

## Manejo de Errores

### Errores de OCR
Los errores se registran en `errores.log` con formato:
```
pagina_0042: API error - status=400
pagina_0103: OCR parsing failed - KeyError
```

### Recuperación de Errores
El sistema guarda `full_response.json` para cada página, permitiendo depuración manual.

### Reintentar Páginas Fallidas
Elimina la entrada correspondiente en `progreso.json` y vuelve a ejecutar `reanudable.py`.

## Optimizaciones

### Rendimiento
- Procesamiento secuencial con sleep de 0.5s entre llamadas
- Checkpoints automáticos después de cada página
- Escritura incremental cada 100/500/1000 filas

### Memoria
- Lectura streaming de archivos grandes
- Liberación de memoria después de cada página
- Límite de caracteres por línea: 2000

## Casos de Uso

1. **Digitalización de catálogos históricos**
2. **Extracción de inventarios bibliográficos**
3. **Análisis de precios históricos de libros**
4. **Investigación de autores y ediciones antiguas**
5. **Creación de bases de datos bibliográficas**

## Limitaciones Conocidas

- Solo procesa imágenes JPG
- Requiere conexión a internet (API Dashscope)
- Los costos dependen del número de tokens procesados
- El OCR puede fallar en imágenes de baja calidad
- Nombres de archivos deben seguir el patrón `pagina_XXXX.jpg`

## Contribuciones

Para mejorar el mapeo de columnas, edita el diccionario `MAPEO_COLUMNAS` en `reprocesar_con_mapeo.py` según las necesidades específicas de tu catálogo.

## Soporte

Para reportar problemas:
1. Revisa `errores.log`
2. Examina los archivos `*.full_response.json` de las páginas problemáticas
3. Verifica la calidad de las imágenes originales

## Licencia

Proyecto desarrollado para la digitalización del catálogo Velasco.

## Notas Técnicas

- **Región**: Configurado para Dashscope Internacional (Singapur)
- **Modelo**: qwen3-vl-plus
- **Encoding**: UTF-8 en todos los archivos
- **Formato CSV**: RFC 4180 compatible
- **Sistema de archivos**: Rutas absolutas recomendadas
