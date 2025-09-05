# Procesador de Datos Inmobiliarios - Finca Raíz

Script para procesar datos inmobiliarios de Finca Raíz y generar archivos estandarizados para análisis de mercado.

## Características

- **Procesamiento JSON**: Extrae y limpia datos inmobiliarios del JSON original
- **Geocodificación (opcional)**: Soporte con Nominatim; desactivada por defecto
- **Estandarización**: Genera CSV con 26 columnas estandarizadas
- **Logging**: Sistema completo de logging para seguimiento del proceso

## Estructura del CSV Estandarizado

### Identificación
- `id_inmueble` - Identificador único del inmueble
- `id_plataforma` - ID de la plataforma origen
- `url_anuncio` - URL del anuncio

### Ubicación
- `pais` - País según datos de la plataforma
- `departamento` - Departamento/estado según plataforma
- `ciudad` - Ciudad según plataforma
- `barrios` - Lista concatenada de barrios/neighbourhoods
- `direccion` - Dirección reportada

### Características del Inmueble
- `direccion` - Dirección específica
- `zona_ciudad` - Zona de la ciudad
- `latitud` - Coordenada latitud
- `longitud` - Coordenada longitud
- `tipo_propiedad` - Tipo de propiedad
- `area_total_m2` - Área total en metros cuadrados
- `num_habitaciones` - Número de habitaciones
- `num_banos` - Número de baños
- `num_parqueaderos` - Número de parqueaderos
- `estrato` - Estrato socioeconómico
- `estado` - Estado (Usado, Nuevo, etc.)
- `antiguedad_construccion` - Antigüedad de construcción

### Información Económica
- `precio_venta` - Precio de venta
- `precio_administracion` - Valor de administración (si aplica)

### Contacto
- `nombre_contacto` - Nombre del anunciante/inmobiliaria

### Fechas
- `fecha_publicacion` - Fecha de publicación
- `fecha_actualizacion` - Fecha de actualización
- `fecha_ingreso` - Fecha de ingreso

## Instalación

Instala las dependencias desde la raíz del proyecto:
```bash
pip install -r ../requirements.txt
```

## Uso

### 1. Análisis Rápido de Estructura
```bash
python analizar_estructura.py
```

### 2. Procesamiento Completo
```bash
python procesador_fincaraiz.py
```

## Archivos Generados

- `fincaraiz_json_procesado.json` - JSON limpio con solo inmuebles
- `fincaraiz_csv_procesado.csv` - CSV estandarizado con 26 columnas
- `procesador_fincaraiz.log` - Log completo del procesamiento

## Configuración

### API de Geocodificación (opcional)
- Actualmente desactivada por defecto. Para habilitarla, descomentar la sección de geocodificación inversa en `mapear_campos_inmueble`.
- Si se activa: Pausa de 2 segundos cada 10 geocodificaciones y timeout de 10 segundos por consulta

### Logging
- **Nivel**: INFO
- **Salida**: Archivo + Consola
- **Formato**: Timestamp + Nivel + Mensaje

## Manejo de Errores

- **Timeouts**: Manejo automático de timeouts de geocodificación
- **Valores Nulos**: Campos vacíos para datos faltantes
- **Estructuras Variables**: Adaptación automática a diferentes formatos JSON
- **Logging**: Registro detallado de errores y advertencias

## Performance

- **Procesamiento**: Por lotes de 100 inmuebles
- **Geocodificación**: Pausas inteligentes para respetar límites de API
- **Memoria**: Procesamiento secuencial para archivos grandes

## Compatibilidad

- **Python**: 3.7+
- **Sistemas**: Windows, macOS, Linux
- **Encoding**: UTF-8

## Notas Importantes

- El script está diseñado para ser compatible con futuras integraciones multi-fuente
- La geocodificación puede tomar tiempo dependiendo del número de inmuebles
- Se recomienda ejecutar en horarios de baja demanda para mejor performance de la API
- Los archivos generados mantienen la compatibilidad con análisis de mercado colombiano

## Soporte

Para reportar problemas o solicitar mejoras, revisar el archivo de log generado durante la ejecución.


