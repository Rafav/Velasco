# Configuración del Viewer BNE Digital

Este documento explica cómo configurar el catálogo para mostrar las imágenes desde BNE Digital en lugar de archivos locales.

## 📋 Requisitos

1. URLs de BNE Digital para cada volumen del catálogo
2. Conocer el ID del viewer de BNE para cada volumen

## 🔧 Pasos de Configuración

### 1. Obtener los IDs de BNE Digital

Para cada volumen del catálogo, necesitas obtener el ID del viewer de BNE Digital:

1. Ve a BNE Digital: https://bnedigital.bne.es/
2. Busca tu documento/volumen
3. Abre el viewer
4. Copia la URL, que tiene este formato:
   ```
   https://bnedigital.bne.es/bd/es/viewer?id=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX&page=1
   ```
5. El ID es la parte después de `id=` y antes de `&page=`

**Ejemplo:**
- URL: `https://bnedigital.bne.es/bd/es/viewer?id=09e8892a-93da-4dda-8e03-190378c061dd&page=2`
- ID: `09e8892a-93da-4dda-8e03-190378c061dd`

### 2. Configurar los IDs en el HTML

Abre el archivo `catalogo_viewer_bne.html` y busca la sección de configuración (línea ~270):

```javascript
const BNE_CONFIG = {
    '1': {
        id: '09e8892a-93da-4dda-8e03-190378c061dd', // ← Reemplaza con el ID real del volumen 1
        pageOffset: 0  // Ajuste si la numeración de páginas no coincide
    },
    '2': {
        id: 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX', // ← Reemplaza con el ID real del volumen 2
        pageOffset: 0
    }
};
```

**Reemplaza** los IDs de ejemplo con los IDs reales de tus volúmenes.

### 3. Ajustar el offset de páginas (si es necesario)

Si la numeración de páginas en el CSV no coincide exactamente con la numeración en BNE Digital:

- Si en el CSV tienes `pagina_0010` pero en BNE corresponde a la página 10, usa `pageOffset: 0`
- Si en el CSV tienes `pagina_0010` pero en BNE corresponde a la página 12, usa `pageOffset: 2`
- Si en el CSV tienes `pagina_0010` pero en BNE corresponde a la página 8, usa `pageOffset: -2`

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

## 🔍 Verificación

Para verificar que la configuración es correcta:

1. Abre `catalogo_viewer_bne.html` en tu navegador
2. Si ves un aviso amarillo arriba, los IDs aún no están configurados
3. Una vez configurados correctamente, el aviso desaparecerá
4. Los botones "Ver en visor" y "Abrir en BNE" estarán disponibles para cada página

## 📝 Ejemplo Completo

Si tienes estos volúmenes en BNE:
- Volumen 1: `https://bnedigital.bne.es/bd/es/viewer?id=09e8892a-93da-4dda-8e03-190378c061dd`
- Volumen 2: `https://bnedigital.bne.es/bd/es/viewer?id=a1b2c3d4-e5f6-7890-abcd-ef1234567890`

Tu configuración sería:

```javascript
const BNE_CONFIG = {
    '1': {
        id: '09e8892a-93da-4dda-8e03-190378c061dd',
        pageOffset: 0
    },
    '2': {
        id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        pageOffset: 0
    }
};
```

## 🆘 Soporte

Si tienes problemas:
1. Verifica que los IDs sean correctos (formato UUID)
2. Comprueba que las URLs de BNE funcionen al abrirlas directamente
3. Revisa la consola del navegador (F12) para ver posibles errores
4. Asegúrate de que el archivo `catalogo.csv` esté en el mismo directorio que el HTML

## 📜 Licencia y Atribución

Los contenidos de BNE Digital están bajo licencia **CC BY 4.0**, que requiere atribución a la Biblioteca Nacional de España. El viewer automáticamente mantiene esta atribución cuando accedes al contenido.
