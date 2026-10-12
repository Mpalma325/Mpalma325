"""Descarga de datos desde fuentes públicas.

1. Tablas de "Valores y fechas" del SII (oficial, sin clave): UF (incluidos los
   valores futuros hasta el día 9), dólar observado, UTM e IPC.
2. https://mindicador.cl (sin clave): además trae el euro y otros indicadores
   (TPM, cobre, IMACEC...). Ojo: no responde desde los servidores de GitHub Actions.
3. API de la CMF, con una clave gratuita (https://api.cmfchile.cl): si defines la
   variable de entorno ``CMF_API_KEY`` (en GitHub: Settings → Secrets → Actions),
   se usa como respaldo y para obtener el euro.

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

# Si un indicador falla esta cantidad de años seguidos, se dejan de pedir sus años
# más antiguos (evita que GitHub Actions se quede minutos esperando).
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


class SinFuente(ErrorDescarga):
    """Ninguna fuente disponible publica el indicador (no hubo intento de descarga)."""


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
    """Lee los valores diarios (UF o dólar) de una página del SII.

    La página trae dos formatos y se leen ambos: una grilla día × mes (filas 1 a 31
    y una columna por mes) y una tabla por mes (título con el nombre del mes y filas
    con pares día-valor).
    """
    serie: dict[dt.date, float] = {}

    def guardar(mes: int, dia_texto: str, valor_texto: str) -> None:
        if not dia_texto.strip().isdigit():
            return
        valor = _numero_o_nada(valor_texto)
        if valor is None:
            return
        try:
            serie[dt.date(anio, mes, int(dia_texto))] = valor
        except ValueError:
            pass

    for tabla in tablas_html(html):
        columnas: dict[int, int] = {}
        mes_de_tabla: int | None = None
        for fila in tabla:
            meses = {i: _mes_de_texto(celda) for i, celda in enumerate(fila)}
            if sum(1 for m in meses.values() if m) >= 3:  # encabezado de la grilla
                columnas = {i: m for i, m in meses.items() if m}
                continue
            if len(fila) == 1 and _mes_de_texto(fila[0]) and len(fila[0]) > 3:  # título "Octubre"
                mes_de_tabla = _mes_de_texto(fila[0])
                continue
            if columnas and fila and fila[0].strip().isdigit():
                for i, mes in columnas.items():
                    if i < len(fila):
                        guardar(mes, fila[0], fila[i])
            elif mes_de_tabla:
                for i in range(0, len(fila) - 1, 2):
                    guardar(mes_de_tabla, fila[i], fila[i + 1])
    return serie


def serie_mensual_sii(html: str, anio: int, columna: str) -> dict[dt.date, float]:
    """Lee la tabla anual de UTM, UTA e IPC del SII.

    Cada fila de datos es: mes, UTM, UTA, IPC (índice), variación mensual, variación
    acumulada del año y variación en 12 meses. ``columna`` es "utm" o "ipc" (variación
    mensual en %). Se valida que la UTA sea 12 veces la UTM para detectar si el SII
    cambió el formato de la tabla.
    """
    serie: dict[dt.date, float] = {}
    for tabla in tablas_html(html):
        for fila in tabla:
            mes = _mes_de_texto(fila[0]) if fila else None
            if mes is None or len(fila) < 5:
                continue
            utm, uta = _numero_o_nada(fila[1]), _numero_o_nada(fila[2])
            if utm is None:
                continue
            if uta is not None and abs(uta - 12 * utm) > 12:
                raise ErrorDescarga("La tabla de UTM del SII cambió de formato (UTA ≠ 12 × UTM)")
            if columna == "utm":
                serie[dt.date(anio, mes, 1)] = utm
            else:
                variacion = _numero_o_nada(fila[4])
                if variacion is not None:
                    serie[dt.date(anio, mes, 1)] = variacion
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
    """Serie de un año desde la primera fuente que responda.

    Orden: SII (oficial, sin clave; UF, dólar, UTM e IPC), mindicador.cl (también
    trae el euro, pero no responde desde algunos servidores en la nube) y la API de
    la CMF si hay clave. ``fuentes_caidas`` acumula las fuentes que no respondieron
    en esta ejecución para no volver a esperarlas.
    """
    caidas = fuentes_caidas if fuentes_caidas is not None else set()
    clave = os.environ.get("CMF_API_KEY", "").strip()
    intentos = [
        ("sii.cl", (lambda: serie_sii(indicador, anio)) if indicador in SII_PAGINAS else None),
        ("mindicador.cl", lambda: serie_mindicador(indicador, anio, intentos=1, timeout=20)),
        ("api.cmfchile.cl", (lambda: serie_cmf(indicador, anio, clave)) if clave else None),
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
    if not errores:
        raise SinFuente(f"Ninguna fuente disponible publica {indicador} (configura CMF_API_KEY)")
    raise ErrorDescarga(" | ".join(errores))


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
    fuentes_caidas: set[str] = set()

    for indicador in SERIES:
        ruta = directorio / "series" / f"{indicador}.json"
        existente = leer_serie(ruta)
        if existente:
            anios = sorted({hoy.year, (hoy - dt.timedelta(days=45)).year}, reverse=True)
        else:
            # Del más reciente al más antiguo: lo importante primero.
            anios = list(range(hoy.year, anio_inicio - 1, -1))

        nuevos: dict[dt.date, float] = {}
        fallas_seguidas = 0  # por indicador; las fuentes caídas se recuerdan en fuentes_caidas
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
            except SinFuente as error:
                # No es una falla de red: simplemente no hay de dónde sacar este indicador.
                resumen["errores"].append(str(error))
                print(f"  {indicador}: {error}", flush=True)
                break
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

    if "mindicador.cl" not in fuentes_caidas:
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
