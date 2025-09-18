#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador de Datos Inmobiliarios - Finca Raíz
Script para procesar JSON de Finca Raíz y generar archivos estandarizados para análisis de mercado.
"""

import json
import pandas as pd
import requests
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import logging
from typing import Dict, List, Optional, Tuple
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procesador_fincaraiz.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProcesadorFincaRaiz:
    """Clase principal para procesar datos inmobiliarios de Finca Raíz."""
    
    def __init__(self, nombre_plataforma: str = "fincaraiz"):
        self.nombre_plataforma = nombre_plataforma
        self.geolocator = Nominatim(user_agent="analisis_inmobiliario_fincaraiz")
        self.contador_geocodificacion = 0
        
    def cargar_json_original(self, ruta_archivo: str) -> Dict:
        """Cargar el archivo JSON original de Finca Raíz."""
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
        """Extraer solo la lista de inmuebles del JSON."""
        inmuebles: List[Dict] = []

        # Caso principal: estructura Elasticsearch como en sample_fincaraiz.json
        if isinstance(datos, dict):
            hits = datos.get('hits')
            if isinstance(hits, dict):
                hits_list = hits.get('hits', [])
                for hit in hits_list:
                    if not isinstance(hit, dict):
                        continue
                    source = hit.get('_source')
                    if isinstance(source, dict):
                        listing = source.get('listing', source)
                        if isinstance(listing, dict):
                            inmuebles.append(listing)
                return inmuebles
    
    def geocodificar_inverso(self, lat: float, lon: float) -> Tuple[str, str, str, str]:
        """Realizar geocodificación inversa usando coordenadas lat/lon."""
        try:
            # Pausa cada 10 geocodificaciones para respetar límites de API
            if self.contador_geocodificacion % 10 == 0 and self.contador_geocodificacion > 0:
                logger.info("Pausa de 2 segundos para respetar límites de API...")
                time.sleep(2)
            
            location = self.geolocator.reverse(f"{lat}, {lon}", timeout=10)
            self.contador_geocodificacion += 1
            
            if location and location.raw.get('address'):
                address = location.raw['address']
                
                # Extraer información de ubicación
                pais = address.get('country', '')
                region = address.get('state', address.get('province', ''))
                ciudad = address.get('city', address.get('town', address.get('village', '')))
                barrio = address.get('suburb', address.get('neighbourhood', ''))
                
                return pais, region, ciudad, barrio
            else:
                return '', '', '', ''
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.warning(f"Timeout en geocodificación para ({lat}, {lon}): {e}")
            return '', '', '', ''
        except Exception as e:
            logger.warning(f"Error en geocodificación para ({lat}, {lon}): {e}")
            return '', '', '', ''
    
    def mapear_campos_inmueble(self, inmueble: Dict) -> Dict:
        """Mapear campos del inmueble a la estructura estandarizada."""
        # Inicializar con valores por defecto
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
            #'pais_geocodificado': '',
            #'region_geocodificada': '',
            #'ciudad_geocodificada': '',
            #'barrio_geocodificado': '',
            'tipo_propiedad': '',
            'area_total_m2': '',
            #'area_construida_m2': '',
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
        
        # Mapear campos según la estructura real de Finca Raíz
        if isinstance(inmueble, dict):
            
            # ID del inmueble
            inmueble_estandarizado['id_inmueble'] = str(inmueble.get('id', ''))
            
            # URL del anuncio - usar el campo 'link' que sí existe
            inmueble_estandarizado['url_anuncio'] = f"https://www.fincaraiz.com.co{inmueble.get('link', '')}"
            
            # Ubicación original - extraer del campo locations
            locations = inmueble.get('locations', {})
            if isinstance(locations, dict):
                # País
                if 'country' in locations and isinstance(locations['country'], list) and len(locations['country']) > 0:
                    inmueble_estandarizado['pais'] = locations['country'][0].get('name', '')
                
                # Región/Departamento
                if 'state' in locations and isinstance(locations['state'], list) and len(locations['state']) > 0:
                    inmueble_estandarizado['departamento'] = locations['state'][0].get('name', '')
                
                # Ciudad
                if 'city' in locations and isinstance(locations['city'], list) and len(locations['city']) > 0:
                    inmueble_estandarizado['ciudad'] = locations['city'][0].get('name', '')
                
                # Barrio
                if 'neighbourhood' in locations and isinstance(locations['neighbourhood'], list) and len(locations['neighbourhood']) > 0:
                    for i, neighbourhood in enumerate(locations['neighbourhood']):
                        # estandarizar el nombre del barrio pasando a minusculas y eliminando acentos
                        barrio = neighbourhood.get('name', '').lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                        inmueble_estandarizado[f'barrio{i+1}'] = barrio
            
            # Coordenadas
            inmueble_estandarizado['latitud'] = inmueble.get('latitude', '')
            inmueble_estandarizado['longitud'] = inmueble.get('longitude', '')
            
            # Geocodificación inversa si hay coordenadas
            # if inmueble_estandarizado['latitud'] and inmueble_estandarizado['longitud']:
            #     try:
            #         lat = float(inmueble_estandarizado['latitud'])
            #         lon = float(inmueble_estandarizado['longitud'])
            #         pais, region, ciudad, barrio = self.geocodificar_inverso(lat, lon)
            #         inmueble_estandarizado['pais_geocodificado'] = pais
            #         inmueble_estandarizado['region_geocodificada'] = region
            #         inmueble_estandarizado['ciudad_geocodificada'] = ciudad
            #         inmueble_estandarizado['barrio_geocodificado'] = barrio
            #     except (ValueError, TypeError):
            #         pass
            
            # Características del inmueble - usar campos reales disponibles
            # Tipo de propiedad - extraer del campo property_type
            property_type_data = inmueble.get('property_type', {})
            if isinstance(property_type_data, dict) and 'name' in property_type_data:
                inmueble_estandarizado['tipo_propiedad'] = property_type_data['name']
            
            inmueble_estandarizado['area_total_m2'] = inmueble.get('m2', '')
            #inmueble_estandarizado['area_construida_m2'] = inmueble.get('m2Built', '')
            inmueble_estandarizado['num_habitaciones'] = inmueble.get('bedrooms', '')
            inmueble_estandarizado['num_banos'] = inmueble.get('bathrooms', '')
            inmueble_estandarizado['num_parqueaderos'] = inmueble.get('garage', '')
            inmueble_estandarizado['estrato'] = inmueble.get('stratum', '')

            # Estado - determinar si es usado o nuevo
            antiquity = inmueble.get('antiquity')
            if antiquity is not None and antiquity > 0: #Todo: Cambiar a 3 años
                inmueble_estandarizado['estado'] = 'Usado'
            elif antiquity is not None and antiquity <= 3 and antiquity > 0:
                inmueble_estandarizado['estado'] = 'Semi-Nuevo'
            else:
                inmueble_estandarizado['estado'] = 'Nuevo'
            inmueble_estandarizado['antiguedad_construccion'] = inmueble.get('antiquity', '')
            
            # Información económica - usar campo price.amount en pesos colombianos
            price_data = inmueble.get('price', {})
            if isinstance(price_data, dict):
                inmueble_estandarizado['precio_venta'] = price_data.get('amount', '')  # Precio en pesos
                inmueble_estandarizado['precio_administracion'] = price_data.get('admin_included', '') - inmueble_estandarizado['precio_venta'] # Precio admin en pesos
            
            # Fechas - usar campos reales disponibles
            inmueble_estandarizado['fecha_publicacion'] = inmueble.get('created_at', '')
            inmueble_estandarizado['fecha_actualizacion'] = inmueble.get('updated_at', '')
            inmueble_estandarizado['fecha_ingreso'] = inmueble.get('created_at', '')
            
            # Campos adicionales específicos de Finca Raíz
            inmueble_estandarizado['direccion'] = inmueble.get('address', '')  # Usar dirección como sector

            # Campos contacto
            owner_data = inmueble.get('owner', {})
            if isinstance(owner_data, dict):
                inmueble_estandarizado['nombre_contacto'] = owner_data.get('name', '')

            # Detección de remodelado por texto (título/descripción/amenidades)
            try:
                textos: List[str] = []
                for clave in ('title', 'description'):
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
            
            # Definir orden de columnas según especificación
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
        
        # Estadísticas de geocodificación
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
        procesador = ProcesadorFincaRaiz()
        
        # Ejecutar procesamiento completo
        procesador.procesar_completo('fincaraiz.json')
        
    except Exception as e:
        logger.error(f"Error fatal en la ejecución: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
