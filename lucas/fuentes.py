"""Descarga de datos desde APIs públicas.

Fuente principal: https://mindicador.cl (gratuita y sin clave; replica datos del
Banco Central, INE y SII). Respaldo opcional: API de la CMF, que requiere una
clave gratuita (https://api.cmfchile.cl). Si defines la variable de entorno
``CMF_API_KEY`` (en GitHub: Settings → Secrets → Actions), se usa cuando
mindicador.cl falla.

Los datos se guardan en ``data/`` y GitHub Actions los sube al repositorio en
cada actualización: así el sitio siempre tiene un respaldo aunque la API se caiga.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from .config import RAIZ, ahora_chile, hoy_chile
from .datos import SERIES, SERIES_MENSUALES, escribir_serie, leer_serie, primer_dia

MINDICADOR = "https://mindicador.cl/api"
CMF = "https://api.cmfchile.cl/api-sbifv3/recursos_api"
USER_AGENT = "LucasClaras/1.0 (sitio de indicadores; contacto en el sitio)"

# Rango de valores plausibles: protege al sitio de publicar datos corruptos.
RANGOS_VALIDOS = {
    "uf": (10_000, 200_000),
    "dolar": (300, 3_000),
    "euro": (300, 3_500),
    "utm": (20_000, 400_000),
    "ipc": (-5, 10),  # variación mensual en %
}

# recurso de la API CMF y nombre de la lista en su respuesta
CMF_RECURSOS = {
    "uf": ("uf", "UFs"),
    "dolar": ("dolar", "Dolares"),
    "euro": ("euro", "Euros"),
    "utm": ("utm", "UTMs"),
    "ipc": ("ipc", "IPCs"),
}


class ErrorDescarga(Exception):
    pass


def _ocultar_claves(texto: str) -> str:
    return re.sub(r"apikey=[^&\s]+", "apikey=***", texto)


def descargar_json(url: str, intentos: int = 3, espera: float = 2.0) -> dict:
    ultimo_error: Exception | None = None
    for intento in range(intentos):
        try:
            solicitud = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(solicitud, timeout=30) as respuesta:
                return json.loads(respuesta.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError,
                UnicodeDecodeError) as error:
            ultimo_error = error
            if intento < intentos - 1:
                time.sleep(espera * (2 ** intento))
    raise ErrorDescarga(_ocultar_claves(f"No se pudo descargar {url}: {ultimo_error}"))


def numero_chileno(texto: str) -> float:
    """'39.485,65' -> 39485.65"""
    return float(str(texto).strip().replace(".", "").replace(",", "."))


def serie_mindicador(indicador: str, anio: int) -> dict[dt.date, float]:
    respuesta = descargar_json(f"{MINDICADOR}/{indicador}/{anio}")
    serie = {}
    for punto in respuesta.get("serie", []):
        # mindicador entrega la medianoche de Chile en UTC ("2026-10-12T03:00:00.000Z"):
        # la parte de la fecha corresponde siempre al día chileno.
        fecha = dt.date.fromisoformat(punto["fecha"][:10])
        serie[fecha] = float(punto["valor"])
    return serie


def serie_cmf(indicador: str, anio: int, clave: str) -> dict[dt.date, float]:
    recurso, lista = CMF_RECURSOS[indicador]
    respuesta = descargar_json(f"{CMF}/{recurso}/{anio}?apikey={clave}&formato=json")
    return {dt.date.fromisoformat(item["Fecha"][:10]): numero_chileno(item["Valor"])
            for item in respuesta.get(lista, [])}


def obtener_serie(indicador: str, anio: int) -> tuple[dict[dt.date, float], str]:
    """Serie de un año desde mindicador.cl, o desde la CMF si la primera falla."""
    try:
        return serie_mindicador(indicador, anio), "mindicador.cl"
    except ErrorDescarga as error_principal:
        clave = os.environ.get("CMF_API_KEY", "").strip()
        if not clave:
            raise
        try:
            return serie_cmf(indicador, anio, clave), "api.cmfchile.cl"
        except ErrorDescarga as error_respaldo:
            raise ErrorDescarga(f"{error_principal} | respaldo CMF: {error_respaldo}") from None


def filtrar_valores_validos(indicador: str, serie: dict[dt.date, float]) -> tuple[dict, list[str]]:
    minimo, maximo = RANGOS_VALIDOS[indicador]
    validos, descartados = {}, []
    for fecha, valor in serie.items():
        if minimo <= valor <= maximo:
            validos[fecha] = valor
        else:
            descartados.append(f"{indicador} {fecha}: {valor} fuera de rango")
    return validos, descartados


def ultimos_indicadores() -> dict:
    """Último valor de todos los indicadores que publica mindicador.cl (TPM, cobre, IMACEC, etc.)."""
    respuesta = descargar_json(MINDICADOR)
    resultado = {}
    for codigo, item in respuesta.items():
        if isinstance(item, dict) and "valor" in item and "fecha" in item:
            resultado[codigo] = {
                "nombre": item.get("nombre", codigo),
                "unidad": item.get("unidad_medida", ""),
                "fecha": item["fecha"][:10],
                "valor": float(item["valor"]),
            }
    return resultado


def actualizar(directorio: Path | None = None, anio_inicio: int = 2018,
               hoy: dt.date | None = None, pausa: float = 0.4) -> dict:
    """Descarga los datos nuevos y los fusiona con los existentes en ``directorio``.

    La primera vez descarga desde ``anio_inicio``; después, solo el año en curso
    (y el anterior durante enero, para cerrar el año).
    """
    directorio = directorio or RAIZ / "data"
    hoy = hoy or hoy_chile()
    resumen: dict = {"series": {}, "errores": [], "fuentes": set()}

    for indicador in SERIES:
        ruta = directorio / "series" / f"{indicador}.json"
        existente = leer_serie(ruta)
        if existente:
            anios = sorted({hoy.year, (hoy - dt.timedelta(days=45)).year})
        else:
            anios = list(range(anio_inicio, hoy.year + 1))

        nuevos: dict[dt.date, float] = {}
        for anio in anios:
            try:
                serie, fuente = obtener_serie(indicador, anio)
                nuevos.update(serie)
                resumen["fuentes"].add(fuente)
            except ErrorDescarga as error:
                resumen["errores"].append(str(error))
            time.sleep(pausa)

        nuevos, descartados = filtrar_valores_validos(indicador, nuevos)
        resumen["errores"] += descartados
        if indicador in SERIES_MENSUALES:
            nuevos = {primer_dia(fecha): valor for fecha, valor in nuevos.items()}
            existente = {primer_dia(fecha): valor for fecha, valor in existente.items()}

        combinado = {**existente, **nuevos}
        cambios = sum(1 for f, v in nuevos.items() if existente.get(f) != v)
        if combinado:
            escribir_serie(ruta, combinado)
        resumen["series"][indicador] = {
            "descargados": len(nuevos),
            "cambios": cambios,
            "total": len(combinado),
            "ultimo": max(combinado).isoformat() if combinado else None,
        }

    try:
        ultimos = ultimos_indicadores()
        with open(directorio / "ultimos.json", "w", encoding="utf-8") as archivo:
            json.dump(ultimos, archivo, indent=1, ensure_ascii=False)
            archivo.write("\n")
    except ErrorDescarga as error:
        resumen["errores"].append(str(error))

    resumen["fuentes"] = sorted(resumen["fuentes"])
    hubo_cambios = any(s["cambios"] for s in resumen["series"].values())
    ruta_meta = directorio / "meta.json"
    meta = {}
    if ruta_meta.exists():
        with open(ruta_meta, encoding="utf-8") as archivo:
            meta = json.load(archivo)
    meta.pop("demo", None)
    meta["ultima_consulta"] = ahora_chile().isoformat(timespec="seconds")
    if hubo_cambios or "actualizado" not in meta:
        meta["actualizado"] = meta["ultima_consulta"]
    meta["fuentes"] = resumen["fuentes"] or meta.get("fuentes", [])
    with open(ruta_meta, "w", encoding="utf-8") as archivo:
        json.dump(meta, archivo, indent=1, ensure_ascii=False)
        archivo.write("\n")
    return resumen
