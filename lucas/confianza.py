"""Señales de confianza del sitio: fuentes oficiales enlazadas, equipo, redes, historial
de correcciones y vigencia de los parámetros legales.

- ``enlazar_fuentes`` convierte el texto de la macro ``m.fuente`` en HTML con enlaces a los
  organismos que conoce (``FUENTES_OFICIALES``), sin cambiar las plantillas que la llaman.
- ``equipo_de``, ``redes_de`` y ``repositorio_de`` leen ``sitio.equipo``, ``sitio.redes`` y
  ``sitio.repositorio`` de config.yaml (para /acerca/, /contacto/ y el JSON-LD).
- ``cargar_correcciones`` lee el historial público de correcciones
  (``contenido/correcciones.yaml``), que se muestra en /metodologia/.
- ``vigencia`` dice desde cuándo rige un valor de ``parametros/chile.yaml``.

Este módulo no importa ``construir`` para que ``seo`` y ``construir`` puedan usarlo.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from urllib.parse import urlparse

from markupsafe import Markup, escape

from .config import RAIZ, Parametros, leer_yaml

ARCHIVO_CORRECCIONES = RAIZ / "contenido" / "correcciones.yaml"

# Nombres tal como aparecen en los textos de fuente de las plantillas → página oficial
# (portadas o secciones estables, verificadas en octubre de 2026). Para enlazar un
# organismo nuevo basta con agregarlo aquí; las siglas apuntan a la misma URL que el
# nombre completo y en cada texto se enlaza una sola vez.
FUENTES_OFICIALES: dict[str, str] = {
    "Banco Central de Chile": "https://www.bcentral.cl/",
    "Banco Central": "https://www.bcentral.cl/",
    "Servicio de Impuestos Internos": "https://www.sii.cl/",
    "SII": "https://www.sii.cl/",
    "Instituto Nacional de Estadísticas": "https://www.ine.gob.cl/",
    "INE": "https://www.ine.gob.cl/",
    "Superintendencia de Pensiones": "https://www.spensiones.cl/",
    "Previred": "https://www.previred.com/",
    "Dirección del Trabajo": "https://www.dt.gob.cl/",
    "Código del Trabajo": "https://www.bcn.cl/leychile/navegar?idNorma=207436",
    "Biblioteca del Congreso Nacional": "https://www.bcn.cl/",
    "Comisión para el Mercado Financiero": "https://www.cmfchile.cl/",
    "CMF": "https://www.cmfchile.cl/",
}

# Los nombres más largos primero: "Banco Central de Chile" gana sobre "Banco Central".
_PATRON_FUENTES = re.compile(
    r"(?<!\w)(?:" + "|".join(re.escape(nombre) for nombre in
                             sorted(FUENTES_OFICIALES, key=len, reverse=True)) + r")(?!\w)")

# Dominio de una URL de fuente (parametros/chile.yaml) → nombre del organismo.
ORGANISMOS: dict[str, str] = {
    "spensiones.cl": "Superintendencia de Pensiones",
    "bcn.cl": "Biblioteca del Congreso Nacional",
    "sii.cl": "Servicio de Impuestos Internos",
    "afc.cl": "AFC Chile",
    "superdesalud.gob.cl": "Superintendencia de Salud",
    "chileatiende.gob.cl": "ChileAtiende",
    "dt.gob.cl": "Dirección del Trabajo",
    "cmfchile.cl": "Comisión para el Mercado Financiero",
    "previred.com": "Previred",
    "bcentral.cl": "Banco Central de Chile",
    "ine.gob.cl": "Instituto Nacional de Estadísticas",
    "gob.cl": "Gobierno de Chile",
}

# Dominio de un perfil público → nombre de la red.
REDES: dict[str, str] = {
    "github.com": "GitHub",
    "linkedin.com": "LinkedIn",
    "instagram.com": "Instagram",
    "x.com": "X",
    "twitter.com": "X",
    "facebook.com": "Facebook",
    "youtube.com": "YouTube",
    "tiktok.com": "TikTok",
    "threads.net": "Threads",
}


# ---------------------------------------------------------------------------
# Fuentes
# ---------------------------------------------------------------------------

def enlazar_fuentes(texto: str) -> Markup:
    """Escapa ``texto`` y enlaza los organismos conocidos, cada URL una sola vez.

    "Servicio de Impuestos Internos (SII)" queda con un solo enlace (en el nombre largo) y
    "Banco Central de Chile e INE, publicado por el SII" con tres.
    """
    usadas: set[str] = set()

    def enlace(coincidencia: re.Match) -> str:
        nombre = coincidencia.group(0)
        url = FUENTES_OFICIALES[nombre]
        if url in usadas:
            return nombre
        usadas.add(url)
        return f'<a href="{escape(url)}" rel="noopener" target="_blank">{nombre}</a>'

    return Markup(_PATRON_FUENTES.sub(enlace, str(escape(texto))))


def _dominio(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def _buscar_por_dominio(url: str, tabla: dict[str, str]) -> str | None:
    """Busca el dominio y luego sus dominios padre: "portal.sii.cl" → "sii.cl"."""
    partes = _dominio(url).split(".")
    for inicio in range(len(partes) - 1):
        nombre = tabla.get(".".join(partes[inicio:]))
        if nombre:
            return nombre
    return None


def nombre_fuente(url: str) -> str:
    """Nombre de una URL de fuente: el de FUENTES_OFICIALES si es exactamente una de ellas
    (p. ej. "Código del Trabajo"), si no el del organismo según el dominio, o el dominio."""
    exactas = [nombre for nombre, conocida in FUENTES_OFICIALES.items() if conocida == url]
    if exactas:
        return max(exactas, key=len)  # el nombre completo, no la sigla
    return _buscar_por_dominio(url, ORGANISMOS) or _dominio(url)


def etiqueta_red(url: str) -> str:
    """"LinkedIn", "GitHub", etc. para un perfil; si no se conoce, el dominio."""
    return _buscar_por_dominio(url, REDES) or _dominio(url)


# ---------------------------------------------------------------------------
# Equipo, redes y repositorio (config.yaml)
# ---------------------------------------------------------------------------

def _url_https(valor) -> str:
    texto = str(valor or "").strip()
    return texto if texto.startswith("https://") and len(texto) > len("https://") else ""


def equipo_de(cfg: dict) -> list[dict]:
    """Personas de ``sitio.equipo`` con nombre. Los enlaces que no son https se omiten
    (``tests/test_confianza.py`` revisa que config.yaml esté bien escrito)."""
    personas = []
    for entrada in cfg["sitio"].get("equipo") or []:
        if not isinstance(entrada, dict) or not str(entrada.get("nombre") or "").strip():
            continue
        enlace = _url_https(entrada.get("enlace"))
        personas.append({
            "nombre": str(entrada["nombre"]).strip(),
            "rol": str(entrada.get("rol") or "").strip(),
            "descripcion": str(entrada.get("descripcion") or "").strip(),
            "enlace": enlace,
            "red": etiqueta_red(enlace) if enlace else "",
        })
    return personas


def redes_de(cfg: dict) -> list[str]:
    """URL https de ``sitio.redes`` (perfiles públicos del sitio, para ``sameAs``)."""
    return [url for url in (_url_https(r) for r in cfg["sitio"].get("redes") or []) if url]


def repositorio_de(cfg: dict) -> str:
    """URL del repositorio público del código (``sitio.repositorio``), o "" si no hay."""
    return _url_https(cfg["sitio"].get("repositorio"))


# ---------------------------------------------------------------------------
# Historial de correcciones
# ---------------------------------------------------------------------------

def cargar_correcciones(ruta: Path | None = None) -> list[dict]:
    """Correcciones publicadas, de la más reciente a la más antigua.

    Cada una tiene ``fecha``, ``titulo``, ``detalle`` y, opcionalmente, ``paginas`` (rutas
    internas afectadas). Un archivo mal escrito detiene la construcción con un mensaje claro.
    """
    ruta = ruta or ARCHIVO_CORRECCIONES
    if not ruta.exists():
        return []
    entradas = leer_yaml(ruta).get("correcciones") or []
    correcciones = []
    for numero, entrada in enumerate(entradas, start=1):
        if not isinstance(entrada, dict):
            raise ValueError(f"{ruta.name}: la corrección N° {numero} no tiene el formato esperado")
        faltan = [campo for campo in ("fecha", "titulo", "detalle") if not entrada.get(campo)]
        if faltan:
            raise ValueError(f"{ruta.name}: a la corrección N° {numero} le falta {', '.join(faltan)}")
        fecha = como_fecha(entrada["fecha"])
        paginas = [str(r) for r in entrada.get("paginas") or []]
        if any(not (r.startswith("/") and r.endswith("/")) for r in paginas):
            raise ValueError(f"{ruta.name}: las páginas de la corrección N° {numero} deben ser "
                             "rutas internas como /calculadoras/finiquito/")
        correcciones.append({"fecha": fecha, "titulo": str(entrada["titulo"]).strip(),
                             "detalle": str(entrada["detalle"]).strip(), "paginas": paginas})
    return sorted(correcciones, key=lambda c: c["fecha"], reverse=True)


# ---------------------------------------------------------------------------
# Vigencia de los parámetros legales
# ---------------------------------------------------------------------------

def vigencia(params: Parametros, grupo: str, fecha: dt.date, campos: tuple[str, ...] = ()) -> dict:
    """Desde cuándo rige el valor vigente de ``grupo`` (o solo de sus ``campos``).

    Devuelve ``{"desde": fecha, "exacta": bool}``. Es exacta si en el historial hay una
    entrada anterior con otro valor: ahí cambió. Si el valor es el mismo desde la primera
    entrada registrada, solo se sabe que rige "al menos desde" esa fecha (por ejemplo, el
    7% de salud, que es anterior al inicio del registro).
    """
    historial = [e for e in params.historial(grupo) if como_fecha(e["desde"]) <= fecha]
    if not historial:
        raise ValueError(f"No hay parámetros de '{grupo}' vigentes al {fecha}")

    def valor(entrada: dict):
        if not campos:
            return {k: v for k, v in entrada.items() if k != "desde"}
        return tuple(entrada.get(campo) for campo in campos)

    actual = valor(historial[-1])
    inicio = len(historial) - 1
    while inicio > 0 and valor(historial[inicio - 1]) == actual:
        inicio -= 1
    return {"desde": como_fecha(historial[inicio]["desde"]), "exacta": inicio > 0}


def proximos_cambios(params: Parametros, grupo: str, fecha: dt.date) -> list[dict]:
    """Entradas ya cargadas en chile.yaml que empiezan a regir después de ``fecha``."""
    return [e for e in params.historial(grupo) if como_fecha(e["desde"]) > fecha]


def como_fecha(valor) -> dt.date:
    """Fecha de un valor de YAML (fecha, fecha y hora o texto AAAA-MM-DD)."""
    if isinstance(valor, dt.datetime):
        return valor.date()
    if isinstance(valor, dt.date):
        return valor
    return dt.date.fromisoformat(str(valor))
