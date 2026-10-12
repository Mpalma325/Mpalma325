"""Genera datos de DEMOSTRACIÓN (ficticios) para probar el sitio sin internet.

Los valores son inventados a propósito (UF que parte en $35.000, dólar en $850,
etc.) y el sitio construido con ``--demo`` muestra un aviso de "datos ficticios"
y se marca como ``noindex``. Nunca se publican: el sitio real usa ``data/``.

Uso: python tests/fixtures/generar_datos_demo.py
"""

from __future__ import annotations

import datetime as dt
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from lucas.datos import (escribir_serie, mes_anterior, mes_siguiente, uf_segun_metodologia,  # noqa: E402
                         utm_segun_metodologia)
from lucas.feriados import feriados_nacionales  # noqa: E402

FECHA_REFERENCIA = dt.date(2026, 10, 12)  # "hoy" de los datos de demostración
DESTINO = Path(__file__).resolve().parent / "datos_demo"
UN_DIA = dt.timedelta(days=1)


def generar() -> None:
    azar = random.Random(20261012)

    # IPC mensual en % con un decimal, desde nov-2022 hasta el mes anterior al de referencia.
    ipc: dict[dt.date, float] = {}
    mes = dt.date(2022, 11, 1)
    ultimo_ipc = mes_anterior(FECHA_REFERENCIA)
    while mes <= ultimo_ipc:
        ipc[mes] = round(azar.uniform(-0.3, 0.9), 1)
        mes = mes_siguiente(mes)
    ipc_fraccion = {m: v / 100 for m, v in ipc.items()}

    # UF: parte el 9 de enero de 2023 en $35.000 y sigue la fórmula oficial.
    # Los datos "descargados" llegan hasta el día de referencia; el sitio calcula el resto.
    uf: dict[dt.date, float] = {dt.date(2023, 1, 9): 35000.00}
    dia = dt.date(2023, 1, 10)
    base, valor_base = dt.date(2023, 1, 9), 35000.00
    while dia <= FECHA_REFERENCIA:
        if dia.day == 10:
            base, valor_base = dia - UN_DIA, uf[dia - UN_DIA]
        uf[dia] = uf_segun_metodologia(dia, valor_base, ipc_fraccion[mes_anterior(base)])
        dia += UN_DIA

    # Dólar y euro: caminata aleatoria en días hábiles.
    feriados = {f.fecha for anio in range(2023, 2027) for f in feriados_nacionales(anio)}
    dolar: dict[dt.date, float] = {}
    euro: dict[dt.date, float] = {}
    valor_dolar, paridad = 850.0, 1.08
    dia = dt.date(2023, 1, 2)
    while dia <= FECHA_REFERENCIA:
        if dia.weekday() < 5 and dia not in feriados:
            valor_dolar = min(1100, max(750, valor_dolar + azar.gauss(0.05, 4.5)))
            paridad = min(1.2, max(1.0, paridad + azar.gauss(0, 0.004)))
            dolar[dia] = round(valor_dolar, 2)
            euro[dia] = round(valor_dolar * paridad, 2)
        dia += UN_DIA

    # UTM: parte en $61.000 en enero de 2023 y se reajusta con el IPC de dos meses antes.
    utm = {dt.date(2023, 1, 1): 61000.0}
    mes = dt.date(2023, 2, 1)
    while mes <= FECHA_REFERENCIA.replace(day=1):
        utm[mes] = utm_segun_metodologia(utm[mes_anterior(mes)], ipc_fraccion[mes_anterior(mes_anterior(mes))],
                                         mantener_si_ipc_negativo=False)
        mes = mes_siguiente(mes)

    escribir_serie(DESTINO / "series" / "uf.json", uf)
    escribir_serie(DESTINO / "series" / "dolar.json", dolar)
    escribir_serie(DESTINO / "series" / "euro.json", euro)
    escribir_serie(DESTINO / "series" / "utm.json", utm)
    escribir_serie(DESTINO / "series" / "ipc.json", ipc)

    ultimo_habil = max(dolar)
    ultimos = {
        "tpm": {"nombre": "Tasa Política Monetaria (TPM)", "unidad": "Porcentaje",
                "fecha": ultimo_habil.isoformat(), "valor": 4.5},
        "libra_cobre": {"nombre": "Libra de Cobre", "unidad": "Dólar",
                        "fecha": ultimo_habil.isoformat(), "valor": 4.25},
        "imacec": {"nombre": "Imacec", "unidad": "Porcentaje",
                   "fecha": dt.date(2026, 8, 1).isoformat(), "valor": 2.1},
        "tasa_desempleo": {"nombre": "Tasa de desempleo", "unidad": "Porcentaje",
                           "fecha": dt.date(2026, 8, 1).isoformat(), "valor": 8.4},
        "bitcoin": {"nombre": "Bitcoin", "unidad": "Dólar",
                    "fecha": ultimo_habil.isoformat(), "valor": 61000.0},
    }
    meta = {
        "demo": True,
        "aviso": "DATOS FICTICIOS generados por tests/fixtures/generar_datos_demo.py",
        "fecha_referencia": FECHA_REFERENCIA.isoformat(),
        "actualizado": f"{FECHA_REFERENCIA.isoformat()}T07:00:00-03:00",
    }
    for nombre, contenido in (("ultimos", ultimos), ("meta", meta)):
        with open(DESTINO / f"{nombre}.json", "w", encoding="utf-8") as archivo:
            json.dump(contenido, archivo, indent=1, ensure_ascii=False)
            archivo.write("\n")
    print(f"Datos de demostración escritos en {DESTINO}")


if __name__ == "__main__":
    generar()
