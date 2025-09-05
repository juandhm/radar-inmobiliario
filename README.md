# Radar Inmobiliario

Proyecto para procesar y estandarizar datos inmobiliarios provenientes de múltiples plataformas: Ciencuadras, Finca Raíz y Metrocuadrado.

## Requisitos

- Python 3.8+
- Pip

## Instalación

```bash
pip install -r requirements.txt
```

## Estructura

```
radar-inmobiliario/
  ciencuadras/
    procesador_ciencuadras.py
  finca_raiz/
    procesador_fincaraiz.py
  metrocuadrado/
    procesador_metrocuadrado.py
  requirements.txt
  README.md
```

## Uso

Cada procesador espera que el archivo JSON de entrada esté en el mismo directorio desde el cual se ejecuta el script. Los nombres por defecto son `ciencuadras.json`, `fincaraiz.json` y `metrocuadrado.json` respectivamente.

### Ciencuadras

```bash
cd ciencuadras
python procesador_ciencuadras.py
```

Genera: `ciencuadras_json_procesado.json` y `ciencuadras_csv_procesado.csv`

### Finca Raíz

```bash
cd finca_raiz
python procesador_fincaraiz.py
```

Genera: `fincaraiz_json_procesado.json` y `fincaraiz_csv_procesado.csv`

### Metrocuadrado

```bash
cd metrocuadrado
python procesador_metrocuadrado.py
```

Genera: `metrocuadrado_json_procesado.json` y `metrocuadrado_csv_procesado.csv`

## Notas

- Dependencias unificadas en `requirements.txt` en la raíz (antes estaban por carpeta).
- Los scripts incluyen logging a archivo y consola.
- La geocodificación (vía `geopy`) está implementada/soportada principalmente en Finca Raíz y puede ajustarse según necesidad.


