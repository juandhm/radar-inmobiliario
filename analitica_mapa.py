#!/usr/bin/env python3
"""
Analítica: Generación de mapa de propiedades desde CSV consolidado.

Lee un CSV consolidado, filtra filas con latitud/longitud válidas, y genera
un mapa HTML con marcadores agrupados (clustering).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
import folium
from folium.plugins import MarkerCluster


def configurar_logging(verbose: bool) -> None:
    nivel = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=nivel,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generar mapa desde consolidado CSV')
    parser.add_argument('consolidado', type=Path, help='Ruta al CSV consolidado')
    parser.add_argument('--salida', type=Path, default=Path('mapa_propiedades.html'), help='Archivo HTML de salida')
    parser.add_argument('--lat-col', type=str, default='latitud', help='Nombre de columna de latitud')
    parser.add_argument('--lon-col', type=str, default='longitud', help='Nombre de columna de longitud')
    parser.add_argument('--popup-cols', type=str, nargs='*', default=['plataforma', 'id_inmueble', 'tipo_propiedad', 'precio_venta', 'precio_m2', 'direccion', 'ciudad'], help='Columnas para mostrar en el popup')
    parser.add_argument('--verbose', action='store_true', help='Habilitar logging detallado')
    return parser.parse_args(argv)


def cargar_datos(ruta_csv: Path, lat_col: str, lon_col: str) -> pd.DataFrame:
    df = pd.read_csv(ruta_csv, dtype=str, encoding='utf-8')
    # Convertir a numérico
    df[lat_col] = pd.to_numeric(df.get(lat_col), errors='coerce')
    df[lon_col] = pd.to_numeric(df.get(lon_col), errors='coerce')
    # Filtrar válidos
    df = df.dropna(subset=[lat_col, lon_col])
    # Rango aproximado Colombia por defecto (pero dejamos cualquier coord válida)
    return df


def crear_mapa(df: pd.DataFrame, lat_col: str, lon_col: str, popup_cols: list[str]) -> folium.Map:
    if df.empty:
        # Centro en Bogotá por defecto
        m = folium.Map(location=[4.711, -74.072], zoom_start=5)
        return m

    # Centroide simple
    center_lat = df[lat_col].mean()
    center_lon = df[lon_col].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='cartodbpositron')

    cluster = MarkerCluster()
    for _, row in df.iterrows():
        lat = row[lat_col]
        lon = row[lon_col]
        # Construir popup compacto
        values = []
        for c in popup_cols:
            if c in df.columns:
                val = row.get(c)
                if pd.notna(val) and val != '':
                    values.append(f"{c}: {val}")
        popup_html = '<br>'.join(values) if values else 'Propiedad'
        folium.Marker([lat, lon], popup=popup_html, icon=folium.Icon(color='blue', icon='home', prefix='fa')).add_to(cluster)

    cluster.add_to(m)
    return m


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configurar_logging(args.verbose)

    logging.info('Leyendo consolidado: %s', args.consolidado)
    try:
        df = cargar_datos(args.consolidado, args.lat_col, args.lon_col)
    except Exception as exc:
        logging.error('Error leyendo CSV: %s', exc)
        return 1

    logging.info('Registros con coordenadas válidas: %s', len(df))
    mapa = crear_mapa(df, args.lat_col, args.lon_col, args.popup_cols)

    try:
        mapa.save(str(args.salida))
        logging.info('Mapa guardado en: %s', args.salida)
    except Exception as exc:
        logging.error('Error guardando mapa: %s', exc)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())


