"""Formato de números y fechas al estilo chileno (es-CL).

Se implementa a mano (sin ``locale``) para que el resultado sea idéntico en
cualquier sistema operativo: Windows, macOS, Linux o GitHub Actions.
"""

from __future__ import annotations

import datetime as dt
import math

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)
DIAS_SEMANA = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


def redondear(valor: float, decimales: int = 0) -> float:
    """Redondeo "mitad hacia arriba", el habitual en liquidaciones y en el SII.

    Usa exactamente las mismas operaciones que ``redondear`` en
    ``estaticos/js/calculos.js`` para que Python y JavaScript den el mismo
    resultado (ambos usan aritmética IEEE 754 de doble precisión).
    """
    factor = 10 ** decimales
    if valor < 0:
        return -math.floor(-valor * factor + 0.5) / factor
    return math.floor(valor * factor + 0.5) / factor


def numero(valor: float | int | None, decimales: int = 0) -> str:
    """Punto de miles y coma decimal: ``1234567.5`` -> ``'1.234.567,50'`` (2 decimales)."""
    if valor is None:
        return "—"
    v = redondear(float(valor), decimales)
    texto = f"{abs(v):,.{decimales}f}"  # p. ej. '1,234,567.50'
    texto = texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return ("-" if v < 0 else "") + texto


def pesos(valor: float | int | None, decimales: int = 0) -> str:
    """``39485.651`` -> ``'$39.485,65'`` (2 decimales)."""
    if valor is None:
        return "—"
    v = redondear(float(valor), decimales)
    return ("-$" if v < 0 else "$") + numero(abs(v), decimales)


def porcentaje(fraccion: float | None, decimales: int = 1, signo: bool = False) -> str:
    """``0.0127`` -> ``'1,27%'`` (2 decimales). Con ``signo=True`` agrega '+' a los positivos."""
    if fraccion is None:
        return "—"
    v = redondear(fraccion * 100, decimales)
    texto = numero(v, decimales) + "%"
    if signo and v > 0:
        texto = "+" + texto
    return texto


def a_fecha(valor: dt.date | dt.datetime | str) -> dt.date:
    if isinstance(valor, dt.datetime):
        return valor.date()
    if isinstance(valor, dt.date):
        return valor
    return dt.date.fromisoformat(str(valor)[:10])


def fecha_larga(valor) -> str:
    """``2026-10-12`` -> ``'12 de octubre de 2026'``."""
    f = a_fecha(valor)
    return f"{f.day} de {MESES[f.month - 1]} de {f.year}"


def fecha_con_dia(valor) -> str:
    """``2026-10-12`` -> ``'lunes 12 de octubre de 2026'``."""
    f = a_fecha(valor)
    return f"{DIAS_SEMANA[f.weekday()]} {fecha_larga(f)}"


def dia_mes(valor) -> str:
    """``2026-10-12`` -> ``'12 de octubre'``."""
    f = a_fecha(valor)
    return f"{f.day} de {MESES[f.month - 1]}"


def fecha_corta(valor) -> str:
    """``2026-10-12`` -> ``'12-10-2026'`` (formato habitual en Chile)."""
    f = a_fecha(valor)
    return f"{f.day:02d}-{f.month:02d}-{f.year}"


def dia_semana(valor) -> str:
    return DIAS_SEMANA[a_fecha(valor).weekday()]


def nombre_mes(mes: int) -> str:
    return MESES[mes - 1]


def mes_anio(anio: int, mes: int) -> str:
    """``(2026, 10)`` -> ``'octubre 2026'`` (como lo busca la gente en Google)."""
    return f"{MESES[mes - 1]} {anio}"


def mes_de_anio(anio: int, mes: int) -> str:
    """``(2026, 10)`` -> ``'octubre de 2026'`` (para texto corrido)."""
    return f"{MESES[mes - 1]} de {anio}"


def capitalizar(texto: str) -> str:
    return texto[:1].upper() + texto[1:] if texto else texto


def monto_corto(valor: float) -> str:
    """Montos redondos legibles: 1000000 -> '1 millón', 1500000 -> '1,5 millones', 800000 -> '800 mil'."""
    if valor >= 1_000_000:
        millones = valor / 1_000_000
        texto = numero(millones, 0 if millones == int(millones) else 1)
        return f"{texto} millón" if millones == 1 else f"{texto} millones"
    if valor >= 1000 and valor % 1000 == 0:
        return f"{numero(valor / 1000)} mil"
    return numero(valor)
