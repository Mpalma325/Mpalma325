"""Feriados en formato iCalendar (RFC 5545) para el botón "Agregar a mi calendario".

Cada año con página de feriados tiene su archivo ``/feriados/<año>.ics`` con un evento
de día completo por cada feriado nacional. Google Calendar, Outlook y el calendario del
teléfono lo importan directamente.

Reglas del formato que se cumplen aquí (y que revisa tests/test_seo_paginas.py):

- Cada línea termina en CRLF y mide como máximo 75 octetos; las más largas se "pliegan"
  en varias líneas que empiezan con un espacio (sección 3.1).
- Cada evento tiene ``UID`` (estable entre construcciones, para que el calendario no
  duplique eventos si se vuelve a importar) y ``DTSTAMP`` en UTC (sección 3.6.1).
- Los eventos de día completo usan ``DTSTART;VALUE=DATE`` y ``DTEND`` el día siguiente,
  porque el término no se incluye (sección 3.6.1).
- Las comas, puntos y comas y barras invertidas de los textos se escapan (sección 3.3.11).
"""

from __future__ import annotations

import datetime as dt
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

from .config import ZONA_CHILE
from .feriados import Feriado, anios_con_pagina, feriados_nacionales

FIN_DE_LINEA = "\r\n"
UN_DIA = dt.timedelta(days=1)


def ruta_ics(anio: int) -> str:
    """Ruta publicada del calendario del año (relativa a la raíz del sitio)."""
    return f"/feriados/{anio}.ics"


def _escapar(texto: str) -> str:
    """Escapa un valor de tipo TEXT."""
    return (texto.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n"))


def _plegar(linea: str) -> str:
    """Corta una línea de más de 75 octetos sin partir los caracteres UTF-8 (tildes, eñes)."""
    partes: list[str] = []
    actual = ""
    for caracter in linea:
        limite = 74 if partes else 75  # las líneas de continuación empiezan con un espacio
        if len((actual + caracter).encode("utf-8")) > limite:
            partes.append(actual)
            actual = caracter
        else:
            actual += caracter
    partes.append(actual)
    return (FIN_DE_LINEA + " ").join(partes)


def _slug(texto: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")


def _descripcion(feriado: Feriado, url_pagina: str) -> str:
    partes = [f"Feriado nacional {feriado.tipo.lower()}"
              + (", irrenunciable para los trabajadores del comercio." if feriado.irrenunciable else ".")]
    if feriado.nota:
        partes.append(feriado.nota.rstrip(".") + ".")
    partes.append(f"Calendario completo: {url_pagina}")
    return " ".join(partes)


def calendario_feriados(anio: int, extras: list[dict] | None, cfg: dict, creado: dt.datetime) -> str:
    """Texto del archivo .ics con los feriados nacionales de ``anio``.

    ``creado`` es la hora de la construcción (va en ``DTSTAMP``); si no tiene zona horaria
    se interpreta como hora de Chile.
    """
    sitio = cfg["sitio"]
    dominio = urlparse(sitio["url"]).hostname or "localhost"
    url_pagina = f"{sitio['url']}/feriados/{anio}/"
    if creado.tzinfo is None:
        creado = creado.replace(tzinfo=ZONA_CHILE)
    sello = creado.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lineas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//{_escapar(sitio['nombre'])}//Feriados de Chile//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Feriados de Chile {anio}",
    ]
    for feriado in feriados_nacionales(anio, extras):
        lineas += [
            "BEGIN:VEVENT",
            f"UID:{feriado.fecha:%Y%m%d}-{_slug(feriado.nombre)}@{dominio}",
            f"DTSTAMP:{sello}",
            f"DTSTART;VALUE=DATE:{feriado.fecha:%Y%m%d}",
            f"DTEND;VALUE=DATE:{feriado.fecha + UN_DIA:%Y%m%d}",
            f"SUMMARY:{_escapar(feriado.nombre)}",
            f"DESCRIPTION:{_escapar(_descripcion(feriado, url_pagina))}",
            "TRANSP:TRANSPARENT",  # un feriado no ocupa tu agenda
            "END:VEVENT",
        ]
    lineas.append("END:VCALENDAR")
    return "".join(_plegar(linea) + FIN_DE_LINEA for linea in lineas)


def escribir_calendarios(salida: Path, cfg: dict, hoy: dt.date, extras: list[dict] | None,
                         creado: dt.datetime) -> list[str]:
    """Escribe ``/feriados/<año>.ics`` para cada año con página de feriados. Devuelve las rutas."""
    rutas = []
    for anio in anios_con_pagina(hoy):
        ruta = ruta_ics(anio)
        destino = salida / ruta.lstrip("/")
        destino.parent.mkdir(parents=True, exist_ok=True)
        # En bytes, para que Windows no cambie los CRLF que exige el formato.
        destino.write_bytes(calendario_feriados(anio, extras, cfg, creado).encode("utf-8"))
        rutas.append(ruta)
    return rutas
