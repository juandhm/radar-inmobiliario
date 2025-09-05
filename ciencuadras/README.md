# Procesador de Datos Inmobiliarios - Ciencuadras

Script para procesar datos inmobiliarios de la plataforma Ciencuadras y generar archivos estandarizados para análisis de mercado.

## Características

- Procesa archivos JSON de Ciencuadras
- Genera CSV estandarizado con 31 columnas
- Implementa geocodificación inversa usando Nominatim
- Maneja errores y timeouts de API
- Genera estadísticas del procesamiento

## Instalación

Instala las dependencias desde la raíz del proyecto:
```bash
pip install -r ../requirements.txt
```

## Uso

1. Asegúrate de tener el archivo `ciencuadras.json` en el directorio
2. Ejecuta el script:
```bash
python procesador_ciencuadras.py
```

## Archivos Generados

- `ciencuadras_json_procesado.json`: JSON limpio con solo inmuebles
- `ciencuadras_csv_procesado.csv`: CSV estandarizado con 31 columnas

## Estructura del CSV

El CSV incluye las siguientes columnas estandarizadas:

### Identificación
- id_inmueble, id_plataforma, url_anuncio

### Ubicación Original
- pais_original, region_departamento_original, ciudad_original, barrio_original

### Ubicación Geocodificada
- pais_geocodificado, region_geocodificada, ciudad_geocodificada, barrio_geocodificado

### Características del Inmueble
- sector, zona_ciudad, latitud, longitud, tipo_propiedad
- area_total_m2, area_construida_m2, num_habitaciones, num_banos, num_parqueaderos
- estrato, estado, antiguedad_construccion

### Información Económica
- precio_venta, precio_alquiler, precio_administracion, tipo_negocio

### Fechas
- fecha_publicacion, fecha_actualizacion, fecha_ingreso

## Notas

- La geocodificación se realiza con pausas cada 10 inmuebles para respetar límites de API
- El script maneja automáticamente campos nulos y valores faltantes
- Compatible con estándares de Metrocuadrado para futuras integraciones
