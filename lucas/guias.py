"""Guías: artículos en Markdown que acompañan a las calculadoras (``contenido/guias/*.md``).

Cada guía es un archivo con un front matter YAML (título, descripción, fuentes,
preguntas frecuentes...) y un cuerpo en Markdown. El cuerpo y los campos de texto
se procesan primero como plantillas Jinja2, con el entorno del sitio y los
parámetros vigentes (así las cifras se actualizan solas), y después el cuerpo se
convierte a HTML. El formato está explicado en ``contenido/LEEME.md``.

Las reglas son las del validador de referencia de la especificación: todo lo que
él acepta se publica y se renderiza igual. Si una guía tiene errores, la
construcción se detiene indicando el archivo y el problema; ``python -m lucas
guias`` muestra el mismo diagnóstico sin construir el sitio.
"""

from __future__ import annotations

import datetime as dt
import itertools
import re
import unicodedata
from dataclasses import dataclass, field
from html import unescape
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, StrictUndefined, TemplateSyntaxError
from markupsafe import Markup

from . import calculos, seo
from .config import RAIZ, cargar_config, cargar_parametros, hoy_chile
from .construir import (DIRECTORIO_DEMO, Contexto, ErrorConstruccion, Pagina, crear_contexto,
                        crear_entorno)
from .datos import cargar_datos
from .feriados import feriados_nacionales

DIRECTORIO = RAIZ / "contenido" / "guias"

# Categorías en el orden en que aparecen en /guias/, con su nombre visible.
CATEGORIAS = {
    "trabajo": "Trabajo y sueldo",
    "impuestos": "Impuestos",
    "vivienda": "Vivienda y arriendo",
    "ahorro": "Ahorro e inversión",
    "indicadores": "Indicadores económicos",
}
OBLIGATORIOS = ("titulo", "descripcion", "h1", "resumen", "publicada", "revisada", "categoria",
                "calculadoras", "fuentes", "faq")
OPCIONALES = ("orden", "palabras_clave")
CON_JINJA = ("titulo", "descripcion", "h1", "resumen")
EXTENSIONES = ["tables", "toc", "sane_lists"]
CONFIG_EXTENSIONES = {"toc": {"toc_depth": "2-3"}}
MARCAS_JINJA = ("{{", "}}", "{%", "%}")
INICIO = ("Inicio", "/")
GUIAS = ("Guías", "/guias/")


@dataclass
class Guia:
    """Guía validada, con el front matter ya renderizado (texto plano) y el cuerpo en HTML."""
    slug: str
    archivo: Path
    titulo: str
    descripcion: str
    h1: str
    resumen: str
    publicada: dt.date
    revisada: dt.date
    categoria: str
    orden: int | None
    calculadoras: list[str]
    fuentes: list[dict]
    faq: list[tuple[str, str]]
    html: Markup
    indice: list[dict]            # tabla de contenidos: [{id, nombre, hijos: [...]}] (h2 y h3)
    palabras: int
    palabras_clave: list[str] = field(default_factory=list)

    @property
    def ruta(self) -> str:
        return f"/guias/{self.slug}/"

    @property
    def nombre_categoria(self) -> str:
        return CATEGORIAS[self.categoria]

    @property
    def minutos_lectura(self) -> int:
        return max(1, round(self.palabras / 200))


@dataclass
class Revision:
    """Resultado de revisar un archivo: errores, avisos y la guía si no hubo errores."""
    archivo: Path
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    titulo: str | None = None     # título renderizado (para detectar títulos repetidos)
    palabras: int | None = None
    html: str = ""
    guia: Guia | None = None


# ---------------------------------------------------------------------------
# Lectura y validación
# ---------------------------------------------------------------------------

def archivos_de_guias(directorio: Path | None = None) -> list[Path]:
    """Archivos de guías. Los que empiezan con "_" o con mayúscula (LEEME.md) no son guías."""
    directorio = directorio or DIRECTORIO
    return sorted(a for a in directorio.glob("*.md") if not (a.name.startswith("_") or a.name[0].isupper()))


def separar(texto: str) -> tuple[dict, str, int]:
    """Separa el front matter YAML del cuerpo. Devuelve (datos, cuerpo, línea donde empieza el cuerpo)."""
    texto = texto.lstrip("\ufeff").replace("\r\n", "\n")
    if not texto.startswith("---\n"):
        raise ValueError("el archivo debe empezar con '---' (front matter YAML)")
    fin = texto.find("\n---\n", 4)
    if fin == -1:
        raise ValueError("falta la línea '---' que cierra el front matter")
    datos = yaml.safe_load(texto[4:fin]) or {}
    if not isinstance(datos, dict):
        raise ValueError("el front matter debe ser un diccionario YAML")
    return datos, texto[fin + 5:], texto[:fin + 5].count("\n") + 1


def sin_bloques_de_codigo(md: str) -> str:
    return re.sub(r"```.*?```", "", md, flags=re.S)


def contar_palabras(html: str) -> int:
    """Palabras del HTML del cuerpo, contadas igual que el validador de referencia."""
    texto = re.sub(r"<[^>]+>", " ", html)
    return len(re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ$%.,]+", texto))


def entorno_de_guias(entorno: Environment) -> Environment:
    """El entorno Jinja del sitio (mismos filtros y globales, incluida ``ruta``) con el
    manejo de espacios del validador: sin ``trim_blocks`` ni ``lstrip_blocks``. Así una
    tabla armada con ``{% for %}`` queda igual en el sitio y en la validación."""
    return entorno.overlay(autoescape=True, undefined=StrictUndefined,
                           trim_blocks=False, lstrip_blocks=False)


def variables_de(c: Contexto) -> dict:
    """Variables de la especificación para el cuerpo y los campos con Jinja.

    ``feriados`` son los feriados nacionales de hoy.year-2 a hoy.year+1, para los ejemplos
    con ``calc.finiquito(...)`` o ``calc.dias_corridos_de_feriado(...)``.
    """
    feriados = {f.fecha for anio in range(c.hoy.year - 2, c.hoy.year + 2)
                for f in feriados_nacionales(anio, c.feriados_extra)}
    return {"p": c.p, "uf_hoy": c.uf_hoy, "utm_hoy": c.utm_hoy, "hoy": c.hoy, "dolar": c.dolar,
            "calc": calculos, "sitio": c.cfg["sitio"], "feriados": feriados}


def _linea_del_error(error: Exception) -> int | None:
    """Línea de la plantilla donde ocurrió un error de Jinja (de sintaxis o al renderizar)."""
    if isinstance(error, TemplateSyntaxError):
        return error.lineno
    linea = None
    rastro = error.__traceback__
    while rastro is not None:
        if rastro.tb_frame.f_code.co_filename == "<template>":
            linea = rastro.tb_lineno
        rastro = rastro.tb_next
    return linea


def _como_lista(valor) -> list[str]:
    if valor is None:
        return []
    if isinstance(valor, (list, tuple)):
        return [str(v) for v in valor]
    return [str(valor)]


def revisar(archivo: Path, entorno: Environment, variables: dict, hoy: dt.date) -> Revision:
    """Valida una guía con las reglas de la especificación y, si está correcta, la renderiza.

    ``entorno`` es el de :func:`entorno_de_guias` y ``hoy`` la fecha máxima admitida
    para ``revisada``.
    """
    r = Revision(archivo)
    errores, avisos = r.errores, r.avisos
    slug = archivo.stem
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) or len(slug) > 60:
        errores.append(f"nombre de archivo inválido '{slug}': usa minúsculas, números y guiones (máx. 60)")
    try:
        datos, cuerpo, linea_cuerpo = separar(archivo.read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001 - YAML inválido, archivo ilegible, etc.
        errores.append(f"front matter: {error}")
        return r

    faltan = [campo for campo in OBLIGATORIOS if campo not in datos]
    errores += [f"falta el campo obligatorio '{campo}'" for campo in faltan]
    avisos += [f"campo desconocido '{campo}' (se ignorará)" for campo in datos
               if campo not in OBLIGATORIOS + OPCIONALES]
    if faltan:
        return r

    def renderizar(texto) -> str:
        return entorno.from_string(str(texto)).render(**variables)

    # Los largos se miden sobre el texto renderizado tal como lo hace el validador;
    # la página usa el texto plano (las plantillas del sitio vuelven a escaparlo).
    render = {}
    for campo in CON_JINJA:
        try:
            render[campo] = renderizar(datos[campo]).strip()
        except Exception as error:  # noqa: BLE001 - cualquier error de plantilla o de filtro
            errores.append(f"{campo}: error de plantilla: {error}")
            render[campo] = str(datos[campo])
    titulo, descripcion = render["titulo"], render["descripcion"]
    r.titulo = titulo
    if len(titulo) > 70:
        errores.append(f"titulo con {len(titulo)} caracteres (máx. 70): {titulo!r}")
    if not 50 <= len(descripcion) <= 230:
        errores.append(f"descripcion con {len(descripcion)} caracteres (entre 50 y 230)")
    elif not 110 <= len(descripcion) <= 165:
        avisos.append(f"descripcion con {len(descripcion)} caracteres (ideal 110-165)")
    if len(render["resumen"]) > 220:
        errores.append(f"resumen con {len(render['resumen'])} caracteres (máx. 220)")
    if len(render["h1"]) > 90:
        errores.append("h1 demasiado largo (máx. 90)")

    fechas = {}
    for campo in ("publicada", "revisada"):
        valor = datos[campo]
        if isinstance(valor, dt.datetime):
            valor = valor.date()
        if isinstance(valor, dt.date):
            fechas[campo] = valor
        else:
            errores.append(f"{campo} debe ser una fecha AAAA-MM-DD sin comillas")
    if len(fechas) == 2:
        if fechas["revisada"] < fechas["publicada"]:
            errores.append("revisada es anterior a publicada")
        if fechas["revisada"] > hoy:
            errores.append("revisada es posterior a hoy")
    categoria = datos["categoria"]
    if not isinstance(categoria, str) or categoria not in CATEGORIAS:
        errores.append(f"categoria '{categoria}' no está en {sorted(CATEGORIAS)}")
    if "orden" in datos and not isinstance(datos["orden"], int):
        errores.append("orden debe ser un número entero")

    calculadoras = datos["calculadoras"]
    if not isinstance(calculadoras, list) or not calculadoras:
        errores.append("calculadoras debe ser una lista con al menos una ruta")
    else:
        for destino in calculadoras:
            if not isinstance(destino, str) or not re.fullmatch(r"/[a-z0-9\-/]*/", destino):
                errores.append(f"ruta de calculadora inválida: {destino!r} (ej. '/calculadoras/finiquito/')")

    fuentes = datos["fuentes"]
    if not isinstance(fuentes, list) or len(fuentes) < 2:
        errores.append("fuentes debe ser una lista con al menos 2 fuentes")
    else:
        for fuente in fuentes:
            if (not isinstance(fuente, dict) or not fuente.get("nombre")
                    or not str(fuente.get("url", "")).startswith("https://")):
                errores.append(f"fuente inválida (requiere nombre y url https): {fuente!r}")

    faq = []
    if not isinstance(datos["faq"], list) or not 2 <= len(datos["faq"]) <= 6:
        errores.append("faq debe tener entre 2 y 6 preguntas")
    else:
        for item in datos["faq"]:
            if not isinstance(item, dict) or set(item) != {"pregunta", "respuesta"}:
                errores.append(f"cada faq debe tener exactamente 'pregunta' y 'respuesta': {item!r}")
                continue
            try:
                pregunta = renderizar(item["pregunta"])
                respuesta = renderizar(item["respuesta"])
            except Exception as error:  # noqa: BLE001
                errores.append(f"faq: error de plantilla: {error}")
                continue
            if not pregunta.strip().endswith("?") or not pregunta.strip().startswith("¿"):
                errores.append(f"la pregunta debe ir entre '¿' y '?': {pregunta!r}")
            if len(respuesta) < 40:
                errores.append(f"respuesta demasiado corta: {respuesta!r}")
            faq.append((unescape(pregunta.strip()), unescape(respuesta.strip())))

    fuente_md = sin_bloques_de_codigo(cuerpo)
    if re.search(r"^# ", fuente_md, flags=re.M):
        errores.append("el cuerpo no debe tener títulos '# ' (h1): empieza las secciones con '## '")
    secciones = re.findall(r"^## ", fuente_md, flags=re.M)
    if len(secciones) < 3:
        errores.append(f"el cuerpo tiene {len(secciones)} secciones '## ' (mínimo 3)")
    if re.search(r"\]\(/", fuente_md):
        errores.append("enlace interno sin ruta(): usa [texto]({{ ruta('/calculadoras/...') }})")
    if re.search(r"\]\(http://", fuente_md):
        errores.append("enlace externo con http://: usa https://")

    try:
        md_renderizado = renderizar(cuerpo)
    except Exception as error:  # noqa: BLE001
        linea = _linea_del_error(error)
        donde = f" (línea {linea + linea_cuerpo - 1} del archivo)" if linea else ""
        errores.append(f"cuerpo: error de plantilla Jinja{donde}: {error}")
        return r
    convertidor = markdown.Markdown(extensions=EXTENSIONES, extension_configs=CONFIG_EXTENSIONES)
    r.html = convertidor.convert(md_renderizado)
    if any(marca in r.html for marca in MARCAS_JINJA):
        errores.append("quedaron marcas de Jinja sin procesar en el HTML")
    r.palabras = contar_palabras(r.html)
    if r.palabras < 500:
        errores.append(f"solo {r.palabras} palabras (mínimo 500; ideal 900-1.600)")
    elif r.palabras < 800:
        avisos.append(f"{r.palabras} palabras (ideal 900-1.600)")
    if errores:
        return r

    r.guia = Guia(
        slug=slug,
        archivo=archivo,
        titulo=unescape(titulo),
        descripcion=unescape(descripcion),
        h1=unescape(render["h1"]),
        resumen=unescape(render["resumen"]),
        publicada=fechas["publicada"],
        revisada=fechas["revisada"],
        categoria=categoria,
        orden=datos.get("orden"),
        calculadoras=list(calculadoras),
        fuentes=[{"nombre": str(f["nombre"]), "url": str(f["url"])} for f in fuentes],
        faq=faq,
        html=Markup(r.html),
        indice=_indice(convertidor.toc_tokens),
        palabras=r.palabras,
        palabras_clave=_como_lista(datos.get("palabras_clave")),
    )
    return r


def _indice(tokens: list[dict]) -> list[dict]:
    """Tabla de contenidos desde la extensión ``toc`` (``name`` ya viene escapado)."""
    return [{"id": t["id"], "nombre": Markup(t["name"]), "hijos": _indice(t["children"])} for t in tokens]


def revisar_todas(archivos: list[Path], c: Contexto, entorno: Environment,
                  rutas: set[str] | None = None) -> list[Revision]:
    """Revisa varias guías con el entorno del sitio. Como el validador, un título repetido
    es un error. Si se entregan las ``rutas`` del sitio, avisa de calculadoras inexistentes."""
    entorno_guias = entorno_de_guias(entorno)
    variables = variables_de(c)
    # Una guía no puede estar revisada en el futuro. Se compara con la fecha real además de
    # la del sitio, para que el sitio de demostración (fecha fija) acepte guías revisadas después.
    limite = max(c.hoy, hoy_chile())
    revisiones = []
    titulos: dict[str, str] = {}
    for archivo in archivos:
        r = revisar(archivo, entorno_guias, variables, limite)
        if r.titulo:
            if r.titulo in titulos:
                r.errores.append(f"título repetido con {titulos[r.titulo]}")
                r.guia = None
            titulos[r.titulo] = archivo.name
        if rutas is not None and r.guia:
            for destino in r.guia.calculadoras:
                if destino not in rutas:
                    r.avisos.append(f"la página {destino} no existe en el sitio (enlace roto)")
        revisiones.append(r)
    return revisiones


def _nombre(archivo: Path) -> str:
    try:
        return archivo.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return str(archivo)


def cargar_guias(c: Contexto, entorno: Environment, directorio: Path | None = None) -> list[Guia]:
    """Valida y renderiza todas las guías (antes de crear las páginas: el título y la
    descripción ya renderizados van en el ``<head>`` y en el sitemap). Si alguna tiene
    errores, detiene la construcción con la lista de archivos y problemas."""
    revisiones = revisar_todas(archivos_de_guias(directorio), c, entorno)
    problemas = [f"{_nombre(r.archivo)}: {error}" for r in revisiones for error in r.errores]
    if problemas:
        raise ErrorConstruccion("Hay guías con errores (revísalas con: python -m lucas guias):\n- "
                                + "\n- ".join(problemas))
    return [r.guia for r in revisiones]


def contexto_de_revision(demo: bool = False, hoy: dt.date | None = None) -> tuple[Contexto, Environment]:
    """Contexto y entorno del sitio para revisar guías sin construirlo: usa los datos de
    ``data/`` si existen y, si no (o con ``demo``), los de demostración."""
    cfg = cargar_config()
    params = cargar_parametros()
    if not (RAIZ / "data" / "series" / "uf.json").exists():
        demo = True
    datos = cargar_datos(DIRECTORIO_DEMO if demo else RAIZ / "data",
                         mantener_utm_si_ipc_negativo=params.get("utm_se_mantiene_con_ipc_negativo", False))
    if hoy is None:
        referencia = datos.meta.get("fecha_referencia") if demo else None
        hoy = dt.date.fromisoformat(referencia) if referencia else hoy_chile()
    c = crear_contexto(cfg, params, datos, hoy, dt.datetime.combine(hoy, dt.time(7, 0)))
    return c, crear_entorno(cfg, c, {})


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

def _clave_alfabetica(texto: str) -> str:
    """Orden alfabético en español que ignora tildes, mayúsculas y signos iniciales (¿, ¡)."""
    plano = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^0-9a-z ]", "", plano).strip()


def ordenar(guias: list[Guia]) -> list[Guia]:
    """Por ``orden`` (las que no lo tienen van al final) y luego por título."""
    return sorted(guias, key=lambda g: (g.orden is None, g.orden or 0, _clave_alfabetica(g.titulo)))


def guias_destacadas(guias: list[Guia], cantidad: int = 6) -> list[Guia]:
    """Hasta ``cantidad`` guías, alternando categorías para que el bloque sea variado."""
    por_categoria = [ordenar([g for g in guias if g.categoria == clave]) for clave in CATEGORIAS]
    alternadas = [g for ronda in itertools.zip_longest(*por_categoria) for g in ronda if g]
    return alternadas[:cantidad]


def _nombre_desde_ruta(destino: str) -> str:
    """Nombre de respaldo para una ruta sin página: '/calculadoras/horas-extra/' -> 'Horas extra'."""
    partes = [p for p in destino.split("/") if p]
    return (partes[-1].replace("-", " ") if partes else "Inicio").capitalize()


def paginas_guias(c: Contexto, existentes: list[Pagina]) -> list[Pagina]:
    """El índice /guias/ y una página por guía. ``existentes`` son las demás páginas del
    sitio: de ellas sale el nombre de cada calculadora del recuadro "Calcúlalo"."""
    nombres = {p.ruta: p.h1 or p.titulo for p in existentes}
    nombres.update({g.ruta: g.h1 for g in c.guias})
    nombres[GUIAS[1]] = GUIAS[0]
    paginas = []
    for guia in c.guias:
        calculadoras = []
        for destino in guia.calculadoras:
            if destino not in nombres:
                c.advertencias.append(f"La guía {guia.archivo.name} enlaza a {destino}, que no existe en el sitio")
            calculadoras.append((nombres.get(destino) or _nombre_desde_ruta(destino), destino))
        # Otras guías de la misma categoría o, si no hay, de las demás (enlaces internos).
        mismas = [g for g in ordenar(c.guias) if g.categoria == guia.categoria and g is not guia][:6]
        otras = [g for g in guias_destacadas(c.guias, len(c.guias)) if g is not guia][:3]
        paginas.append(Pagina(
            ruta=guia.ruta,
            plantilla="guia.html",
            titulo=guia.titulo,
            descripcion=guia.descripcion,
            h1=guia.h1,
            migas=[INICIO, GUIAS, (guia.h1, guia.ruta)],
            faq=guia.faq,
            clave=guia.categoria,
            prioridad=0.7,
            frecuencia="monthly",
            modificada=guia.revisada,
            jsonld=[seo.jsonld_articulo(c.cfg, guia.h1, guia.descripcion, guia.ruta, guia.publicada,
                                        guia.revisada, guia.palabras_clave)],
            contexto={
                "guia": guia,
                "calculadoras": calculadoras,
                "relacionadas": mismas or otras,
                "misma_categoria": bool(mismas),
            },
        ))

    categorias = [{"clave": clave, "nombre": nombre, "guias": ordenar([g for g in c.guias if g.categoria == clave])}
                  for clave, nombre in CATEGORIAS.items()]
    paginas.insert(0, Pagina(
        ruta=GUIAS[1],
        plantilla="guias.html",
        titulo="Guías de sueldo, impuestos, vivienda y ahorro en Chile",
        descripcion=("Guías claras sobre sueldo, impuestos, vivienda, ahorro e indicadores en Chile, "
                     "con ejemplos que se actualizan solos y enlaces a las fuentes oficiales."),
        h1="Guías para entender tus finanzas",
        migas=[INICIO, GUIAS],
        prioridad=0.8,
        frecuencia="weekly",
        modificada=max((g.revisada for g in c.guias), default=None),
        contexto={"categorias": [cat for cat in categorias if cat["guias"]]},
    ))
    return paginas
