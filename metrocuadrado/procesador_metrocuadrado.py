#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador de Datos Inmobiliarios - Metrocuadrado
Script para procesar JSON de Metrocuadrado y generar archivos estandarizados para análisis de mercado.
"""

import json
import pandas as pd
import time
import logging
from typing import Dict, List, Tuple
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procesador_metrocuadrado.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ProcesadorMetrocuadrado:
    """Clase principal para procesar datos inmobiliarios de Metrocuadrado."""

    def __init__(self, nombre_plataforma: str = "metrocuadrado"):
        self.nombre_plataforma = nombre_plataforma

    def cargar_json_original(self, ruta_archivo: str) -> Dict:
        """Cargar el archivo JSON original de Metrocuadrado."""
        try:
            logger.info(f"Cargando archivo JSON: {ruta_archivo}")
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)

            logger.info(f"JSON cargado exitosamente. Tamaño: {len(str(datos))} caracteres")
            return datos
        except Exception as e:
            logger.error(f"Error al cargar JSON: {e}")
            raise

    def extraer_lista_inmuebles(self, datos: Dict) -> List[Dict]:
        """Extraer solo la lista de inmuebles del JSON de Metrocuadrado."""
        try:
            propiedades = (
                datos.get('data', {})
                .get('result', {})
                .get('propertiesByFiltersQuery', {})
                .get('properties', [])
            )
            if isinstance(propiedades, list):
                return [p for p in propiedades if isinstance(p, dict)]
            return []
        except Exception as e:
            logger.warning(f"No se pudo extraer la lista de inmuebles: {e}")
            return []

    def mapear_campos_inmueble(self, inmueble: Dict) -> Dict:
        """Mapear campos del inmueble a la estructura estandarizada usada en el proyecto."""
        inmueble_estandarizado = {
            'id_inmueble': '',
            'plataforma': self.nombre_plataforma,
            'url_anuncio': '',
            'pais': '',
            'departamento': '',
            'ciudad': '',
            'barrio1': '',
            'direccion': '',
            'latitud': '',
            'longitud': '',
            'tipo_propiedad': '',
            'area_total_m2': '',
            'num_habitaciones': '',
            'num_banos': '',
            'num_parqueaderos': '',
            'estrato': '',
            'estado': '',
            'antiguedad_construccion': '',
            'remodelado': False,
            'precio_venta': '',
            'precio_administracion': '',
            'fecha_publicacion': '',
            'fecha_actualizacion': '',
            'fecha_ingreso': '',
            'nombre_contacto': '',
        }

        if not isinstance(inmueble, dict):
            return inmueble_estandarizado

        # Identificación y URL
        inmueble_estandarizado['id_inmueble'] = str(inmueble.get('id', ''))
        inmueble_estandarizado['url_anuncio'] = f"https://www.metrocuadrado.com.co{inmueble.get('url', '')}"

        # Ubicación
        country = inmueble.get('country', {})
        region = inmueble.get('region', {})
        city = inmueble.get('city', {})
        neighborhood = inmueble.get('neighborhood', {})
        zone = inmueble.get('zone', {})

        if isinstance(country, dict):
            inmueble_estandarizado['pais'] = country.get('name', '')
        if isinstance(region, dict):
            inmueble_estandarizado['departamento'] = region.get('name', '')
        if isinstance(city, dict):
            inmueble_estandarizado['ciudad'] = city.get('name', '')
        if isinstance(neighborhood, dict):
            inmueble_estandarizado['barrio1'] = neighborhood.get('name', '')

        # Coordenadas
        location = inmueble.get('location', {})
        if isinstance(location, dict):
            inmueble_estandarizado['latitud'] = location.get('lat', '')
            inmueble_estandarizado['longitud'] = location.get('lon', '')

        # Características
        property_type = inmueble.get('propertyType', {})
        if isinstance(property_type, dict):
            inmueble_estandarizado['tipo_propiedad'] = property_type.get('name', '')

        inmueble_estandarizado['area_total_m2'] = inmueble.get('area', '')
        inmueble_estandarizado['num_habitaciones'] = inmueble.get('roomsNumber', '')
        inmueble_estandarizado['num_banos'] = inmueble.get('bathroomsNumber', '')
        inmueble_estandarizado['num_parqueaderos'] = inmueble.get('parkingNumber', '')
        inmueble_estandarizado['estrato'] = inmueble.get('stratum', '')
        inmueble_estandarizado['estado'] = inmueble.get('status', '')

        built_time = inmueble.get('builtTime', {})
        if isinstance(built_time, dict):
            inmueble_estandarizado['antiguedad_construccion'] = built_time.get('name', '')

        # Precios
        inmueble_estandarizado['precio_venta'] = inmueble.get('salePrice', '')
        inmueble_estandarizado['precio_administracion'] = inmueble.get('adminPrice', '')

        # Fechas
        inmueble_estandarizado['fecha_publicacion'] = inmueble.get('publishedDate', '')
        inmueble_estandarizado['fecha_actualizacion'] = inmueble.get('updatedDate', '')
        inmueble_estandarizado['fecha_ingreso'] = inmueble.get('checkInDate', '')

        # Contacto (si existiese)
        advertiser = inmueble.get('advertiser', {})
        seller = inmueble.get('seller', {})
        if isinstance(advertiser, dict) and advertiser.get('name'):
            inmueble_estandarizado['nombre_contacto'] = advertiser.get('name', '')
        elif isinstance(seller, dict) and seller.get('name'):
            inmueble_estandarizado['nombre_contacto'] = seller.get('name', '')

        # Detección de remodelado por título/descripción/listas
        try:
            textos: List[str] = []
            for clave in ('comments'): 
                valor = inmueble.get(clave)
                if isinstance(valor, str):
                    textos.append(valor)

            texto = ' '.join(textos).lower()
            for a, b in (('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u')):
                texto = texto.replace(a, b)

            palabras = [
                'remodelado', 'remodelada', 'remodelacion', 'renovado', 'renovada',
                'reformado', 'reformada', 'actualizado', 'actualizada', 'modernizado', 'modernizada',
                'cocina remodelada', 'banos remodelados', 'baño remodelado', 'bano remodelado'
            ]
            inmueble_estandarizado['remodelado'] = any(p in texto for p in palabras)
        except Exception:
            inmueble_estandarizado['remodelado'] = False

        return inmueble_estandarizado

    def procesar_inmuebles(self, lista_inmuebles: List[Dict]) -> List[Dict]:
        """Procesar todos los inmuebles y aplicar mapeo de campos."""
        logger.info(f"Iniciando procesamiento de {len(lista_inmuebles)} inmuebles...")

        inmuebles_procesados = []
        total = len(lista_inmuebles)

        for i, inmueble in enumerate(lista_inmuebles, 1):
            if i % 100 == 0:
                logger.info(f"Procesando inmueble {i}/{total} ({(i/total)*100:.1f}%)")

            inmueble_procesado = self.mapear_campos_inmueble(inmueble)
            inmuebles_procesados.append(inmueble_procesado)

        logger.info(f"Procesamiento completado: {len(inmuebles_procesados)} inmuebles procesados")
        return inmuebles_procesados

    def generar_json_procesado(self, inmuebles_procesados: List[Dict]) -> str:
        """Generar archivo JSON procesado."""
        nombre_archivo = f"{self.nombre_plataforma}_json_procesado.json"

        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(inmuebles_procesados, archivo, ensure_ascii=False, indent=2)

            logger.info(f"JSON procesado guardado: {nombre_archivo}")
            return nombre_archivo
        except Exception as e:
            logger.error(f"Error al guardar JSON procesado: {e}")
            raise

    def generar_csv_estandarizado(self, inmuebles_procesados: List[Dict]) -> str:
        """Generar archivo CSV estandarizado."""
        nombre_archivo = f"{self.nombre_plataforma}_csv_procesado.csv"

        try:
            # Crear DataFrame
            df = pd.DataFrame(inmuebles_procesados)

            # Definir orden de columnas según especificación (alineado con Finca Raíz actualizado)
            columnas_ordenadas = [
                'id_inmueble', 'plataforma', 'url_anuncio',
                'pais', 'departamento', 'ciudad', 'barrio1', 'direccion',
                'latitud', 'longitud',
                'tipo_propiedad', 'area_total_m2', 'num_habitaciones', 'num_banos', 'num_parqueaderos',
                'estrato', 'estado', 'antiguedad_construccion', 'remodelado',
                'precio_venta', 'precio_administracion',
                'fecha_publicacion', 'fecha_actualizacion', 'fecha_ingreso',
                'nombre_contacto'
            ]

            # Reordenar columnas y llenar las faltantes con valores vacíos
            for col in columnas_ordenadas:
                if col not in df.columns:
                    df[col] = ''

            df = df[columnas_ordenadas]

            # Guardar CSV
            df.to_csv(nombre_archivo, index=False, encoding='utf-8')

            logger.info(f"CSV estandarizado guardado: {nombre_archivo}")
            return nombre_archivo
        except Exception as e:
            logger.error(f"Error al generar CSV: {e}")
            raise

    def mostrar_estadisticas(self, inmuebles_procesados: List[Dict], nombre_csv: str):
        """Mostrar estadísticas del procesamiento."""
        logger.info("=" * 60)
        logger.info("ESTADÍSTICAS DEL PROCESAMIENTO")
        logger.info("=" * 60)

        # Estadísticas generales
        total_inmuebles = len(inmuebles_procesados)
        logger.info(f"Total de inmuebles procesados: {total_inmuebles}")

        # (Geocodificación desactivada por ahora)
        # geocodificados = sum(1 for inm in inmuebles_procesados if inm['pais_geocodificado'])
        # logger.info(f"Inmuebles geocodificados exitosamente: {geocodificados} ({(geocodificados/total_inmuebles)*100:.1f}%)")

        # Dimensiones del CSV
        df = pd.DataFrame(inmuebles_procesados)
        logger.info(f"Dimensiones del CSV: {df.shape[0]} filas x {df.shape[1]} columnas")

        # Muestra de las primeras filas
        logger.info("\nPrimeras 3 filas del CSV:")
        logger.info(df.head(3).to_string())

        # Información del archivo
        logger.info(f"\nArchivo CSV generado: {nombre_csv}")
        logger.info("=" * 60)

    def procesar_completo(self, ruta_json: str):
        """Ejecutar el procesamiento completo."""
        try:
            # 1. Cargar JSON original
            datos_originales = self.cargar_json_original(ruta_json)

            # 2. Extraer lista de inmuebles
            lista_inmuebles = self.extraer_lista_inmuebles(datos_originales)

            # 3. Procesar inmuebles
            inmuebles_procesados = self.procesar_inmuebles(lista_inmuebles)

            # 4. Generar archivos
            json_procesado = self.generar_json_procesado(inmuebles_procesados)
            csv_estandarizado = self.generar_csv_estandarizado(inmuebles_procesados)

            # 5. Mostrar estadísticas
            self.mostrar_estadisticas(inmuebles_procesados, csv_estandarizado)

            logger.info("PROCESAMIENTO COMPLETADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"Error en el procesamiento: {e}")
            raise


def main():
    """Función principal del script."""
    try:
        # Crear instancia del procesador
        procesador = ProcesadorMetrocuadrado()

        # Ejecutar procesamiento completo
        procesador.procesar_completo('metrocuadrado.json')

    except Exception as e:
        logger.error(f"Error fatal en la ejecución: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


