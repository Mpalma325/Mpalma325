"""Carga de la configuración del sitio (config.yaml) y de los parámetros legales
(parametros/chile.yaml), más utilidades de fecha en hora de Chile."""

from __future__ import annotations

import copy
import datetime as dt
import os
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import yaml

RAIZ = Path(__file__).resolve().parent.parent
ZONA_CHILE = ZoneInfo("America/Santiago")

CONFIG_POR_DEFECTO: dict = {
    "sitio": {
        "nombre": "Saca la Cuenta",
        "eslogan": "Indicadores y calculadoras para tus finanzas en Chile",
        "url": "https://sacalacuenta.cl",
        "idioma": "es-CL",
        "correo_contacto": "",
        "autores": "",
        "anio_inicio_datos": 2018,
    },
    "monetizacion": {
        "adsense": {"activo": False, "publisher_id": "", "slots": {}},
        "afiliados": [],
    },
    "analitica": {
        "cloudflare_web_analytics_token": "",
        "google_analytics_id": "",
    },
    "verificacion": {
        "google": "",
        "bing": "",
    },
    "indexnow": {"clave": ""},
}


def _fusionar(base: dict, extra: dict) -> dict:
    resultado = copy.deepcopy(base)
    for clave, valor in (extra or {}).items():
        if isinstance(valor, dict) and isinstance(resultado.get(clave), dict):
            resultado[clave] = _fusionar(resultado[clave], valor)
        else:
            resultado[clave] = valor
    return resultado


def leer_yaml(ruta: Path) -> dict:
    with open(ruta, encoding="utf-8") as archivo:
        return yaml.safe_load(archivo) or {}


def cargar_config(ruta: Path | None = None) -> dict:
    """Lee config.yaml y completa los valores que falten con los por defecto."""
    ruta = ruta or RAIZ / "config.yaml"
    crudo = leer_yaml(ruta) if ruta.exists() else {}
    cfg = _fusionar(CONFIG_POR_DEFECTO, crudo)
    # Permite sobrescribir la URL desde el entorno (útil para vistas previas).
    url = os.environ.get("LUCAS_URL") or cfg["sitio"]["url"]
    url = url.rstrip("/")
    cfg["sitio"]["url"] = url
    # Si el sitio vive en una subcarpeta (p. ej. usuario.github.io/saca-la-cuenta),
    # todos los enlaces internos deben llevar ese prefijo.
    cfg["sitio"]["ruta_base"] = urlparse(url).path.rstrip("/")
    return cfg


class Parametros:
    """Parámetros legales con fechas de vigencia (ver parametros/chile.yaml).

    Cada grupo tiene una lista ``vigencias`` de entradas con un campo ``desde``.
    ``vigente(grupo, fecha)`` devuelve la última entrada cuyo ``desde`` es
    anterior o igual a ``fecha``.
    """

    def __init__(self, crudo: dict):
        self.crudo = crudo

    def __getitem__(self, clave: str):
        return self.crudo[clave]

    def get(self, clave: str, defecto=None):
        return self.crudo.get(clave, defecto)

    def vigente(self, grupo: str, fecha: dt.date) -> dict:
        entradas = self.crudo[grupo]["vigencias"]
        candidatas = [e for e in entradas if _como_fecha(e["desde"]) <= fecha]
        if not candidatas:
            raise ValueError(f"No hay parámetros de '{grupo}' vigentes al {fecha}")
        return max(candidatas, key=lambda e: _como_fecha(e["desde"]))

    def historial(self, grupo: str) -> list[dict]:
        return sorted(self.crudo[grupo]["vigencias"], key=lambda e: _como_fecha(e["desde"]))

    def feriados_extra(self) -> list[dict]:
        return list((self.crudo.get("feriados_extra") or {}).get("lista") or [])

    def revisiones_pendientes(self, hoy: dt.date) -> list[tuple[str, dt.date, str]]:
        """Grupos cuya fecha ``revisar_antes_de`` ya llegó: (grupo, fecha, fuente)."""
        pendientes = []
        for grupo, valor in self.crudo.items():
            if isinstance(valor, dict) and valor.get("revisar_antes_de"):
                limite = _como_fecha(valor["revisar_antes_de"])
                if limite <= hoy:
                    pendientes.append((grupo, limite, valor.get("fuente", "")))
        return pendientes


def _como_fecha(valor) -> dt.date:
    if isinstance(valor, dt.datetime):
        return valor.date()
    if isinstance(valor, dt.date):
        return valor
    return dt.date.fromisoformat(str(valor))


def cargar_parametros(ruta: Path | None = None) -> Parametros:
    ruta = ruta or RAIZ / "parametros" / "chile.yaml"
    return Parametros(leer_yaml(ruta))


def hoy_chile() -> dt.date:
    """Fecha de hoy en Chile. Se puede forzar con la variable de entorno LUCAS_HOY=AAAA-MM-DD."""
    forzado = os.environ.get("LUCAS_HOY")
    if forzado:
        return dt.date.fromisoformat(forzado)
    return dt.datetime.now(ZONA_CHILE).date()


def ahora_chile() -> dt.datetime:
    forzado = os.environ.get("LUCAS_HOY")
    if forzado:
        return dt.datetime.combine(dt.date.fromisoformat(forzado), dt.time(7, 0), ZONA_CHILE)
    return dt.datetime.now(ZONA_CHILE)
