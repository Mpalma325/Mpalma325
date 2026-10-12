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
from html.parser import HTMLParser
from pathlib import Path

from .config import RAIZ, ahora_chile, hoy_chile
from .datos import SERIES, SERIES_MENSUALES, escribir_serie, leer_serie, primer_dia

MINDICADOR = "https://mindicador.cl/api"
SII = "https://www.sii.cl/valores_y_fechas"
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

# Si la fuente falla esta cantidad de veces seguidas, se deja de consultar en esta
# ejecución (evita que GitHub Actions se quede minutos esperando a una API caída).
MAX_FALLAS_SEGUIDAS = 4

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


def descargar_json(url: str, intentos: int = 3, espera: float = 2.0, timeout: float = 25) -> dict:
    ultimo_error: Exception | None = None
    for intento in range(intentos):
        try:
            solicitud = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(solicitud, timeout=timeout) as respuesta:
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


def serie_mindicador(indicador: str, anio: int, **opciones) -> dict[dt.date, float]:
    respuesta = descargar_json(f"{MINDICADOR}/{indicador}/{anio}", **opciones)
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


# ---------------------------------------------------------------------------
# Respaldo sin clave: tablas públicas del SII (valores y fechas)
# ---------------------------------------------------------------------------

MESES_CORTOS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
SII_PAGINAS = {"uf": "uf/uf{anio}.htm", "dolar": "dolar/dolar{anio}.htm", "utm": "utm/utm{anio}.htm",
               "ipc": "utm/utm{anio}.htm"}


class _LectorTablas(HTMLParser):
    """Extrae todas las tablas de una página HTML como listas de filas de texto."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tablas: list[list[list[str]]] = []
        self._pila: list[list[list[str]]] = []
        self._celda: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._pila.append([])
        elif tag == "tr" and self._pila:
            self._pila[-1].append([])
        elif tag in ("td", "th") and self._pila:
            self._celda = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._celda is not None and self._pila and self._pila[-1]:
            self._pila[-1][-1].append(" ".join("".join(self._celda).split()))
            self._celda = None
        elif tag == "table" and self._pila:
            self.tablas.append(self._pila.pop())

    def handle_data(self, data):
        if self._celda is not None:
            self._celda.append(data)


def tablas_html(html: str) -> list[list[list[str]]]:
    lector = _LectorTablas()
    lector.feed(html)
    return [[fila for fila in tabla if fila] for tabla in lector.tablas]


def _mes_de_texto(texto: str) -> int | None:
    texto = texto.strip().lower()[:3]
    return MESES_CORTOS.index(texto) + 1 if texto in MESES_CORTOS else None


def _numero_o_nada(texto: str) -> float | None:
    texto = texto.replace("$", "").replace("%", "").strip()
    if not texto or not any(ch.isdigit() for ch in texto):
        return None
    try:
        return numero_chileno(texto)
    except ValueError:
        return None


def serie_diaria_sii(html: str, anio: int) -> dict[dt.date, float]:
    """Lee una grilla día × mes (UF o dólar): filas 1..31 y una columna por mes."""
    serie: dict[dt.date, float] = {}
    for tabla in tablas_html(html):
        columnas: dict[int, int] = {}
        for fila in tabla:
            meses = {i: _mes_de_texto(celda) for i, celda in enumerate(fila)}
            if sum(1 for m in meses.values() if m) >= 3:
                columnas = {i: m for i, m in meses.items() if m}
                continue
            if not columnas or not fila or not fila[0].strip().isdigit():
                continue
            dia = int(fila[0])
            for i, mes in columnas.items():
                if i < len(fila) and 1 <= dia <= 31:
                    valor = _numero_o_nada(fila[i])
                    if valor is not None:
                        try:
                            serie[dt.date(anio, mes, dia)] = valor
                        except ValueError:
                            pass
    return serie


def serie_mensual_sii(html: str, anio: int, columna: str) -> dict[dt.date, float]:
    """Lee la tabla mensual de la UTM: ``columna`` es "utm" o "ipc" (variación mensual en %)."""
    serie: dict[dt.date, float] = {}
    for tabla in tablas_html(html):
        indice = None
        for fila in tabla:
            encabezados = [celda.lower() for celda in fila]
            if any("utm" in e for e in encabezados) and _mes_de_texto(fila[0]) is None:
                if columna == "utm":
                    indice = next((i for i, e in enumerate(encabezados) if e.startswith("utm")), None)
                else:
                    indice = next((i for i, e in enumerate(encabezados)
                                   if "mensual" in e and ("var" in e or "ipc" in e)), None)
                continue
            mes = _mes_de_texto(fila[0]) if fila else None
            if indice is None or mes is None or indice >= len(fila):
                continue
            valor = _numero_o_nada(fila[indice])
            if valor is not None:
                serie[dt.date(anio, mes, 1)] = valor
    return serie


def descargar_texto(url: str, intentos: int = 3, espera: float = 2.0, timeout: float = 25) -> str:
    ultimo_error: Exception | None = None
    for intento in range(intentos):
        try:
            solicitud = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(solicitud, timeout=timeout) as respuesta:
                crudo = respuesta.read()
            for codificacion in ("utf-8", "latin-1"):
                try:
                    return crudo.decode(codificacion)
                except UnicodeDecodeError:
                    continue
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            ultimo_error = error
            if intento < intentos - 1:
                time.sleep(espera * (2 ** intento))
    raise ErrorDescarga(f"No se pudo descargar {url}: {ultimo_error}")


def serie_sii(indicador: str, anio: int, **opciones) -> dict[dt.date, float]:
    if indicador not in SII_PAGINAS:
        raise ErrorDescarga(f"El SII no publica {indicador}")
    html = descargar_texto(f"{SII}/{SII_PAGINAS[indicador].format(anio=anio)}", **opciones)
    if indicador in ("uf", "dolar"):
        serie = serie_diaria_sii(html, anio)
    else:
        serie = serie_mensual_sii(html, anio, indicador)
    if not serie:
        raise ErrorDescarga(f"No se encontraron datos de {indicador} {anio} en la página del SII")
    return serie


def obtener_serie(indicador: str, anio: int, fuentes_caidas: set[str] | None = None
                  ) -> tuple[dict[dt.date, float], str]:
    """Serie de un año: primero mindicador.cl, luego la CMF (si hay clave) y luego el SII.

    ``fuentes_caidas`` acumula las fuentes que fallaron en esta ejecución para no
    volver a esperarlas en cada consulta.
    """
    caidas = fuentes_caidas if fuentes_caidas is not None else set()
    clave = os.environ.get("CMF_API_KEY", "").strip()
    intentos = [
        # Un solo intento corto: si mindicador no responde (pasa desde algunos
        # servidores en la nube), se pasa de inmediato a la siguiente fuente.
        ("mindicador.cl", lambda: serie_mindicador(indicador, anio, intentos=1, timeout=20)),
        ("api.cmfchile.cl", (lambda: serie_cmf(indicador, anio, clave)) if clave else None),
        ("sii.cl", (lambda: serie_sii(indicador, anio)) if indicador in SII_PAGINAS else None),
    ]
    errores = []
    for nombre, funcion in intentos:
        if funcion is None or nombre in caidas:
            continue
        try:
            return funcion(), nombre
        except ErrorDescarga as error:
            errores.append(str(error))
            if "No se pudo descargar" in str(error):
                caidas.add(nombre)
    raise ErrorDescarga(" | ".join(errores) or f"Sin fuentes disponibles para {indicador} {anio}")


def filtrar_valores_validos(indicador: str, serie: dict[dt.date, float]) -> tuple[dict, list[str]]:
    minimo, maximo = RANGOS_VALIDOS[indicador]
    validos, descartados = {}, []
    for fecha, valor in serie.items():
        if minimo <= valor <= maximo:
            validos[fecha] = valor
        else:
            descartados.append(f"{indicador} {fecha}: {valor} fuera de rango")
    return validos, descartados


def ultimos_indicadores(**opciones) -> dict:
    """Último valor de todos los indicadores que publica mindicador.cl (TPM, cobre, IMACEC, etc.)."""
    respuesta = descargar_json(MINDICADOR, **opciones)
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
    fallas_seguidas = 0
    fuentes_caidas: set[str] = set()

    for indicador in SERIES:
        ruta = directorio / "series" / f"{indicador}.json"
        existente = leer_serie(ruta)
        if existente:
            anios = sorted({hoy.year, (hoy - dt.timedelta(days=45)).year})
        else:
            anios = list(range(anio_inicio, hoy.year + 1))

        nuevos: dict[dt.date, float] = {}
        for anio in anios:
            if fallas_seguidas >= MAX_FALLAS_SEGUIDAS:
                resumen["errores"].append(f"Se omitió {indicador} {anio}: la fuente no responde")
                continue
            inicio = time.monotonic()
            try:
                serie, fuente = obtener_serie(indicador, anio, fuentes_caidas)
                nuevos.update(serie)
                resumen["fuentes"].add(fuente)
                fallas_seguidas = 0
                print(f"  {indicador} {anio}: {len(serie)} valores ({fuente}, "
                      f"{time.monotonic() - inicio:.1f} s)", flush=True)
            except ErrorDescarga as error:
                fallas_seguidas += 1
                resumen["errores"].append(str(error))
                print(f"  {indicador} {anio}: ERROR tras {time.monotonic() - inicio:.1f} s: {error}", flush=True)
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

    if fallas_seguidas < MAX_FALLAS_SEGUIDAS and "mindicador.cl" not in fuentes_caidas:
        try:
            ultimos = ultimos_indicadores(intentos=1, timeout=20)
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
