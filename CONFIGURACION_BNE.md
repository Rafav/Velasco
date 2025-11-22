# Configuración del Viewer BNE Digital

Este documento explica cómo está configurado el catálogo para mostrar las imágenes desde BNE Digital.

## ✅ Configuración Actual

El viewer ya está **completamente configurado** para trabajar con BNE Digital. No necesitas hacer ningún cambio.

### Configuración del documento BNE

Ambos volúmenes del catálogo están contenidos en un único documento de BNE Digital:

- **ID de BNE**: `09e8892a-93da-4dda-8e03-190378c061dd`
- **Páginas del Volumen 1 en BNE**: 174 páginas
- **Volumen 2**: Comienza en la página 175 de BNE

### Algoritmo de cálculo de páginas

El viewer utiliza el siguiente algoritmo para convertir las páginas del catálogo a páginas de BNE:

```
Página BNE = ((Volumen - 1) × 174) + (Página Catálogo ÷ 2)
```

**Ejemplos:**
- Volumen 1, Página 10 del catálogo → `(1-1)×174 + 10÷2 = 0 + 5 =` **Página 5 de BNE**
- Volumen 2, Página 6 del catálogo → `(2-1)×174 + 6÷2 = 174 + 3 =` **Página 177 de BNE**

## 🔧 Si necesitas modificar la configuración

Solo si cambias de documento o necesitas ajustar el cálculo, edita en `catalogo_viewer_bne.html` (línea ~386):

```javascript
const BNE_CONFIG = {
    id: '09e8892a-93da-4dda-8e03-190378c061dd',
    pagesPerVolume: 174  // Páginas del volumen 1 en BNE
};
```

## 🎨 Características del Viewer

Una vez configurado correctamente, el viewer ofrece:

### ✅ Dos formas de ver las imágenes:

1. **Ver en visor embebido** (🖼️): Muestra el viewer de BNE en un iframe dentro de la página
2. **Abrir en BNE** (🔗): Abre el viewer de BNE en una nueva pestaña

### ⚠️ Limitaciones del iframe

La BNE puede tener políticas de seguridad (X-Frame-Options o CSP) que impidan mostrar el viewer en un iframe. En ese caso:

- El visor embebido mostrará un mensaje de error
- Podrás usar el botón "Abrir en BNE Digital" para ver la imagen en una nueva pestaña
- Esto es normal y es una medida de seguridad del sitio web de BNE

### 📊 Ventajas vs. Imágenes Locales

**Ventajas:**
- No necesitas descargar ni almacenar las imágenes localmente
- Siempre accedes a las imágenes originales en alta calidad
- El viewer de BNE tiene funciones avanzadas (zoom, descarga, etc.)
- Cumples con las licencias y atribuciones de la BNE automáticamente

**Desventajas:**
- Requiere conexión a internet
- Depende de la disponibilidad del servicio de BNE
- Puede haber restricciones en el iframe (dependiendo de las políticas de BNE)

## 🔍 Uso del Viewer

1. Abre `catalogo_viewer_bne.html` en tu navegador
2. Los botones "Ver en visor" y "Abrir en BNE" estarán disponibles para cada página
3. Haz clic en cualquier botón para ver la imagen correspondiente en BNE Digital

## 🆘 Solución de Problemas

Si tienes problemas:
1. Verifica que el archivo `catalogo.csv` esté en el mismo directorio que el HTML
2. Comprueba tu conexión a internet (necesaria para acceder a BNE)
3. Revisa la consola del navegador (F12) para ver posibles errores
4. Verifica que las URLs de BNE funcionen al abrirlas directamente

## 📜 Licencia y Atribución

Los contenidos de BNE Digital están bajo licencia **CC BY 4.0**, que requiere atribución a la Biblioteca Nacional de España. El viewer automáticamente mantiene esta atribución cuando accedes al contenido.
