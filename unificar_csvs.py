#!/usr/bin/env python3
"""
Unificador de CSVs de portales inmobiliarios.

Busca archivos *_csv_procesado.csv en subdirectorios (ciencuadras, finca_raiz, metrocuadrado),
los concatena alineando columnas, elimina duplicados por (plataforma, id_inmueble)
y guarda un CSV consolidado en la raíz.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List

import pandas as pd


def configurar_logging(verbose: bool) -> None:
    nivel = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def encontrar_csvs(base_dir: Path) -> List[Path]:
    patrones = ["*_csv_procesado.csv"]
    candidatos = []
    for sub in base_dir.iterdir():
        if sub.is_dir():
            for patron in patrones:
                candidatos.extend(sub.glob(patron))
    # incluir raíz por si acaso
    for patron in patrones:
        candidatos.extend(base_dir.glob(patron))
    # deduplicar por path
    unicos = []
    vistos = set()
    for p in candidatos:
        rp = p.resolve()
        if rp not in vistos:
            vistos.add(rp)
            unicos.append(p)
    return unicos


def leer_csv_seguro(ruta: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(ruta, dtype=str, encoding="utf-8")
        df["__origen_csv__"] = str(ruta)
        return df
    except Exception as exc:
        logging.error("Error leyendo %s: %s", ruta, exc)
        return pd.DataFrame()


def unificar_csvs(rutas: List[Path]) -> pd.DataFrame:
    if not rutas:
        logging.warning("No se encontraron CSVs para unificar.")
        return pd.DataFrame()

    dataframes = [leer_csv_seguro(r) for r in rutas]
    dataframes = [df for df in dataframes if not df.empty]
    if not dataframes:
        logging.warning("Ningún CSV válido fue leído.")
        return pd.DataFrame()

    # columnas objetivo mínimas esperadas según especificación
    columnas_minimas = [
        "id_inmueble",
        "plataforma",
        "url_anuncio",
        "pais",
        "departamento",
        "ciudad",
        "barrio1",
        "direccion",
        "latitud",
        "longitud",
        "tipo_propiedad",
        "area_total_m2",
        "precio_m2",
        "num_habitaciones",
        "num_banos",
        "num_parqueaderos",
        "estrato",
        "estado",
        "antiguedad_construccion",
        "remodelado",
        "precio_venta",
        "precio_administracion",
        "fecha_publicacion",
        "fecha_actualizacion",
        "fecha_ingreso",
        "nombre_contacto",
    ]

    # concatenar y alinear columnas
    df_total = pd.concat(dataframes, axis=0, ignore_index=True, sort=False)

    # Calcular precio por m2 si es posible
    try:
        precio = pd.to_numeric(df_total.get("precio_venta"), errors="coerce")
        area = pd.to_numeric(df_total.get("area_total_m2"), errors="coerce")
        df_total["precio_m2"] = (precio / area).where((area > 0), other=pd.NA)
        # Redondear a entero si es número
        df_total["precio_m2"] = df_total["precio_m2"].round(0)
    except Exception:
        # Si falla el cálculo, dejar la columna vacía y continuar
        df_total["precio_m2"] = ""
    for col in columnas_minimas:
        if col not in df_total.columns:
            df_total[col] = ""

    # ordenar columnas: primero las estándar y luego las adicionales
    cols_adicionales = [c for c in df_total.columns if c not in columnas_minimas + ["__origen_csv__"]]
    columnas_ordenadas = columnas_minimas + cols_adicionales + ["__origen_csv__"]
    df_total = df_total[columnas_ordenadas]

    # deduplicación
    if {"plataforma", "id_inmueble"}.issubset(df_total.columns):
        antes = len(df_total)
        df_total = df_total.drop_duplicates(subset=["plataforma", "id_inmueble"], keep="first")
        despues = len(df_total)
        logging.info("Deduplicados %s registros (antes=%s, después=%s)", antes - despues, antes, despues)
    else:
        logging.warning("No se pudo deduplicar: faltan columnas clave.")

    return df_total


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unificar CSVs de portales inmobiliarios")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directorio base donde buscar subcarpetas de portales",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("consolidado_portales.csv"),
        help="Ruta del CSV consolidado de salida",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Habilitar logging detallado",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configurar_logging(args.verbose)

    logging.info("Base dir: %s", args.base_dir)
    rutas = encontrar_csvs(args.base_dir)
    if not rutas:
        logging.warning("No se encontraron archivos *_csv_procesado.csv")
    else:
        for r in rutas:
            logging.info("Encontrado: %s", r)

    df = unificar_csvs(rutas)
    if df.empty:
        logging.warning("Nada que escribir. Terminando.")
        return 0

    try:
        df.to_csv(args.salida, index=False, encoding="utf-8")
        logging.info("CSV consolidado guardado en: %s", args.salida)
    except Exception as exc:
        logging.error("Error al escribir salida: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())


