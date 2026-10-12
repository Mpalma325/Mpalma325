"""API abierta y gratuita de indicadores, widget para otros sitios y sus páginas.

La API son archivos JSON estáticos que se regeneran en cada construcción del sitio
(dos veces al día en GitHub Actions). Cloudflare los sirve con CORS abierto y caché de
30 minutos (reglas de ``/api/*`` en ``seo.cabeceras_cloudflare``):

- ``/api/v1/indicadores.json``: UF de hoy (y de mañana si se conoce), dólar observado,
  euro, UTM del mes y último IPC.
- ``/api/v1/uf.json``: UF diaria desde 30 días atrás hasta la última conocida.
- ``/api/v1/dolar.json``: los últimos 30 valores del dólar observado.
- ``/api/v1/feriados/<año>.json``: feriados del año anterior, el actual y el siguiente.

Formato: JSON compacto en UTF-8, fechas ISO (los meses como ``AAAA-MM``) y números sin
formato. Quien ya usa ``v1`` depende de estos nombres: agregar campos está bien, pero
cambiar o quitar uno exige publicar ``/api/v2/``.

El widget (``widget/widget.js``) se publica en ``/widget.js``, en la raíz y no en
``/estaticos/``: esa carpeta se guarda en caché por un año y el código que otros sitios
insertan tiene que poder corregirse. Su enlace de atribución queda en el HTML del sitio
que lo inserta y lleva ``rel="nofollow"``, como pide Google para los enlaces que se
distribuyen dentro de widgets (detalles en docs/LANZAMIENTO.md).
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import html
import json
import shutil
from pathlib import Path

from . import seo
from .config import RAIZ, ZONA_CHILE
from .construir import Contexto, Pagina
from .datos import Datos, primer_dia
from .feriados import Feriado, feriados_nacionales, feriados_regionales
from .formato import redondear

VERSION = "v1"
DIAS_UF = 30          # uf.json parte 30 días antes de hoy
VALORES_DOLAR = 30    # dolar.json trae los últimos 30 valores publicados
ARCHIVO_WIDGET = RAIZ / "widget" / "widget.js"
# (clave, nombre en el generador, marcado por defecto). El euro solo se ofrece si hay datos.
OPCIONES_WIDGET = [("uf", "UF", True), ("dolar", "Dólar observado", True), ("euro", "Euro", False),
                   ("utm", "UTM", True)]
INICIO = ("Inicio", "/")


# ---------------------------------------------------------------------------
# Contenido de los archivos JSON
# ---------------------------------------------------------------------------

def anios_feriados(hoy: dt.date) -> list[int]:
    return [hoy.year - 1, hoy.year, hoy.year + 1]


def _actualizado(c: Contexto) -> str:
    """Fecha y hora ISO de la última actualización de los datos (la misma del pie del sitio)."""
    texto = c.datos.meta.get("actualizado")
    momento = dt.datetime.fromisoformat(texto) if texto else c.ahora
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=ZONA_CHILE)
    return momento.isoformat(timespec="seconds")


def _pie(c: Contexto, fuente: str) -> dict:
    """Campos comunes al final de cada archivo: fuente, condiciones de uso y documentación."""
    nombre, url = c.cfg["sitio"]["nombre"], c.cfg["sitio"]["url"]
    return {
        "fuente": fuente,
        "condiciones": (f"Uso gratuito, también comercial, citando la fuente: muestra junto a los datos "
                        f"un enlace visible a {nombre} ({url}/), que puede llevar rel=\"nofollow\". "
                        "Valores referenciales: verifícalos en las fuentes oficiales antes de usarlos "
                        "en pagos, contratos o declaraciones."),
        "atribucion": {"texto": nombre, "enlace": url + "/"},
        "documentacion": seo.url_absoluta(c.cfg, "/api/"),
    }


def _punto(dato: tuple[dt.date, float]) -> dict:
    return {"fecha": dato[0].isoformat(), "valor": dato[1]}


def _serie(puntos) -> list[dict]:
    return [{"fecha": f.isoformat(), "valor": v} for f, v in puntos]


def datos_indicadores(c: Contexto) -> dict:
    hoy = c.hoy
    manana = hoy + dt.timedelta(days=1)
    uf_manana = c.datos.uf_dia(manana)
    # c.utm_hoy es la UTM del mes o, si aún no se conoce, la última publicada.
    mes_utm = primer_dia(hoy)
    if c.datos.utm_mes(hoy) is None:
        mes_utm = Datos.ultimo(c.datos.utm_completa(), hoy)[0]
    utm = int(c.utm_hoy) if c.utm_hoy == int(c.utm_hoy) else c.utm_hoy  # la UTM es un monto entero
    nombre = c.cfg["sitio"]["nombre"]
    return {
        "version": VERSION,
        "actualizado": _actualizado(c),
        "uf": {"fecha": hoy.isoformat(), "valor": c.uf_hoy,
               "manana": None if uf_manana is None else {"fecha": manana.isoformat(), "valor": uf_manana}},
        "dolar": _punto(c.dolar),
        "euro": _punto(c.euro) if c.euro else None,
        "utm": {"mes": mes_utm.strftime("%Y-%m"), "valor": utm},
        # Variación mensual en porcentaje, como la publica el INE (0.4 = 0,4 %).
        "ipc": {"mes": c.ipc[0].strftime("%Y-%m"), "variacion_porcentual": redondear(c.ipc[1] * 100, 2)},
        **_pie(c, "Banco Central de Chile (UF, dólar observado y euro), Servicio de Impuestos Internos "
                  f"(UTM) e Instituto Nacional de Estadísticas (IPC), recopilados por {nombre}"),
    }


def datos_uf(c: Contexto) -> dict:
    desde = c.hoy - dt.timedelta(days=DIAS_UF)
    puntos = [(f, v) for f, v in c.datos.uf_completa().items() if f >= desde]
    calculadas = sorted(f for f in c.datos.uf_calculada if f >= desde)
    return {
        "version": VERSION,
        "actualizado": _actualizado(c),
        "indicador": "uf",
        "nombre": "Unidad de Fomento (UF)",
        "unidad": "CLP",
        "desde": puntos[0][0].isoformat(),
        "hasta": puntos[-1][0].isoformat(),
        # Días posteriores al último valor descargado: calculados con la fórmula del Banco
        # Central a partir del IPC ya publicado (ver lucas/datos.py).
        "calculada_desde": calculadas[0].isoformat() if calculadas else None,
        "serie": _serie(puntos),
        **_pie(c, "Banco Central de Chile; los días posteriores al último valor publicado se calculan "
                  "con la fórmula oficial a partir del IPC del INE"),
    }


def datos_dolar(c: Contexto) -> dict:
    puntos = [(f, v) for f, v in sorted(c.datos.dolar.items()) if f <= c.hoy][-VALORES_DOLAR:]
    return {
        "version": VERSION,
        "actualizado": _actualizado(c),
        "indicador": "dolar",
        "nombre": "Dólar observado",
        "unidad": "CLP",
        "serie": _serie(puntos),
        **_pie(c, "Banco Central de Chile (dólar observado, publicado cada día hábil)"),
    }


def _feriado(f: Feriado) -> dict:
    """Todos los atributos del feriado (nombre, tipo, irrenunciable, nota, regional...)."""
    return {**dataclasses.asdict(f), "fecha": f.fecha.isoformat()}


def datos_feriados(c: Contexto, anio: int) -> dict:
    return {
        "version": VERSION,
        "actualizado": _actualizado(c),
        "anio": anio,
        "feriados": [_feriado(f) for f in feriados_nacionales(anio, c.feriados_extra)],
        "regionales": [_feriado(f) for f in feriados_regionales(anio)],
        **_pie(c, "Calculados según la legislación chilena vigente (leyes 2.977, 19.668, 19.973, "
                  "20.215, 20.299, 20.983 y 21.357, entre otras), más los feriados especiales publicados"),
    }


def archivos_api(c: Contexto) -> dict[str, dict]:
    """Ruta publicada (relativa a la raíz del sitio) -> contenido de cada archivo JSON."""
    archivos = {f"api/{VERSION}/indicadores.json": datos_indicadores(c),
                f"api/{VERSION}/uf.json": datos_uf(c),
                f"api/{VERSION}/dolar.json": datos_dolar(c)}
    for anio in anios_feriados(c.hoy):
        archivos[f"api/{VERSION}/feriados/{anio}.json"] = datos_feriados(c, anio)
    return archivos


def json_compacto(valor) -> str:
    return json.dumps(valor, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def escribir_api(salida: Path, c: Contexto) -> list[str]:
    """Escribe los JSON de la API y el widget en ``salida``. Devuelve las rutas escritas."""
    archivos = archivos_api(c)
    for ruta, contenido in archivos.items():
        destino = salida / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json_compacto(contenido), encoding="utf-8")
    shutil.copyfile(ARCHIVO_WIDGET, salida / "widget.js")
    return [*archivos, "widget.js"]


# ---------------------------------------------------------------------------
# Páginas /widget/ y /api/
# ---------------------------------------------------------------------------

def codigo_widget(cfg: dict, indicadores=("uf", "dolar", "utm"), tema: str = "auto") -> str:
    """Código para insertar el widget. ``widget-generador.js`` arma exactamente el mismo texto."""
    url = html.escape(cfg["sitio"]["url"])
    texto = html.escape(f"Indicadores de {cfg['sitio']['nombre']}")
    return (f'<div class="lucas-claras-widget" data-indicadores="{",".join(indicadores)}" data-tema="{tema}">'
            f'<a href="{url}/" rel="nofollow">{texto}</a></div>\n'
            f'<script async src="{url}/widget.js"></script>')


def _bonito(valor) -> str:
    return json.dumps(valor, ensure_ascii=False, indent=2)


def paginas_api_widget(c: Contexto) -> list[Pagina]:
    cfg = c.cfg
    nombre = cfg["sitio"]["nombre"]
    archivos = archivos_api(c)
    indicadores = archivos[f"api/{VERSION}/indicadores.json"]
    uf = archivos[f"api/{VERSION}/uf.json"]
    dolar = archivos[f"api/{VERSION}/dolar.json"]
    anios = anios_feriados(c.hoy)
    feriados = archivos[f"api/{VERSION}/feriados/{c.hoy.year}.json"]
    proximo = next((f for f in feriados["feriados"] if f["fecha"] >= c.hoy.isoformat()), feriados["feriados"][-1])

    endpoints = [
        (f"/api/{VERSION}/indicadores.json",
         "UF de hoy y de mañana, dólar observado, euro, UTM del mes y último IPC."),
        (f"/api/{VERSION}/uf.json",
         f"UF diaria desde hace {DIAS_UF} días hasta el último valor conocido (normalmente, el día 9 "
         "del mes siguiente)."),
        (f"/api/{VERSION}/dolar.json",
         f"Los últimos {VALORES_DOLAR} valores del dólar observado (días hábiles)."),
    ] + [(f"/api/{VERSION}/feriados/{anio}.json", f"Feriados nacionales y regionales de {anio}.")
         for anio in anios]

    descripcion_api = ("API gratuita y abierta con la UF, el dólar observado, el euro, la UTM, el IPC y los "
                       "feriados de Chile en JSON. Sin registro ni clave, con CORS y ejemplos en "
                       "JavaScript, curl y Python.")
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Indicadores económicos y feriados de Chile en JSON",
        "description": ("UF diaria, dólar observado, euro, UTM, último IPC y feriados de Chile en archivos "
                        "JSON abiertos, actualizados dos veces al día con datos del Banco Central de Chile, "
                        "el SII y el INE."),
        "url": seo.url_absoluta(cfg, "/api/"),
        "isAccessibleForFree": True,
        "inLanguage": cfg["sitio"]["idioma"],
        "creator": {"@type": "Organization", "name": nombre, "url": cfg["sitio"]["url"] + "/"},
        "license": seo.url_absoluta(cfg, "/api/") + "#condiciones",
        "spatialCoverage": "Chile",
        "keywords": ["UF", "dólar observado", "euro", "UTM", "IPC", "feriados", "Chile"],
        "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json",
                          "contentUrl": seo.url_absoluta(cfg, ruta)} for ruta, _ in endpoints],
    }
    comunes = {"frecuencia": "monthly", "prioridad": 0.5, "modificada": dt.date(2026, 10, 12)}
    return [
        Pagina(
            ruta="/widget/",
            plantilla="widget.html",
            titulo="Widget gratis de UF, dólar y UTM para tu sitio web",
            descripcion=("Agrega gratis a tu sitio web un widget con la UF, el dólar observado y la UTM "
                         "del día, en formato chileno y con tema claro u oscuro. Elige los indicadores, "
                         "copia el código y listo."),
            h1="Widget de UF, dólar y UTM para tu sitio web",
            migas=[INICIO, ("Widget para tu sitio", "/widget/")],
            faq=[
                ("¿El widget es gratis?",
                 "Sí. Puedes usarlo sin costo y sin registrarte en blogs, sitios de empresas, intranets o "
                 f"proyectos personales. Solo te pedimos mantener visible el enlace a {nombre} que "
                 "viene en el código."),
                ("¿Cada cuánto se actualizan los valores?",
                 "Cada vez que alguien abre tu página, el widget lee los últimos valores que publicamos. "
                 "Los actualizamos dos veces al día con datos del Banco Central de Chile, el SII y el "
                 "INE. El dólar observado y el euro cambian solo en días hábiles."),
                ("¿Funciona en WordPress, Blogger u otras plataformas?",
                 "Funciona en cualquier sitio que permita pegar HTML con JavaScript, por ejemplo en un "
                 "bloque de HTML personalizado de WordPress. Algunos servicios de blogs gratuitos "
                 "eliminan los scripts: en ese caso solo se verá el enlace."),
                ("¿El widget usa cookies o recopila datos de mis visitantes?",
                 "No usa cookies ni guarda datos personales. Para mostrar los valores, el navegador de "
                 "tu visitante descarga el script y un archivo con los indicadores desde nuestro sitio, "
                 "que recibe datos técnicos como la dirección IP, igual que en cualquier visita web."),
                ("¿Por qué el enlace lleva rel=\"nofollow\"?",
                 "Porque Google pide que los enlaces que se distribuyen dentro de widgets lleven "
                 "nofollow (o no existan), para que no influyan en el posicionamiento. Así el widget "
                 "cumple sus políticas contra el spam de enlaces, tanto para tu sitio como para el nuestro."),
                ("¿Qué pasa si los datos no cargan?",
                 "Tu página sigue funcionando normalmente: el script se carga de forma asíncrona y, si "
                 "no logra leer los indicadores, deja visible el enlace original."),
            ],
            contexto={
                "codigo": codigo_widget(cfg),
                "texto_enlace": f"Indicadores de {nombre}",
                "opciones": [o for o in OPCIONES_WIDGET if o[0] != "euro" or c.euro],
            },
            **comunes,
        ),
        Pagina(
            ruta="/api/",
            plantilla="api.html",
            titulo="API gratuita de indicadores económicos de Chile (JSON)",
            descripcion=descripcion_api,
            h1="API gratuita de indicadores económicos de Chile",
            migas=[INICIO, ("API de indicadores", "/api/")],
            jsonld=[dataset],
            faq=[
                ("¿Necesito registrarme o una clave de API?",
                 "No. Son archivos JSON públicos: basta con pedirlos por HTTPS, desde un servidor o desde "
                 "el navegador."),
                ("¿Puedo usarla en un proyecto comercial?",
                 f"Sí, siempre que muestres junto a los datos un enlace visible a {nombre}. Si lo "
                 "prefieres, puedes marcar ese enlace con rel=\"nofollow\"."),
                ("¿Puedo consultarla desde el navegador?",
                 "Sí. Las respuestas incluyen la cabecera Access-Control-Allow-Origin: *, así que puedes "
                 "leerlas con fetch desde cualquier sitio."),
                ("¿Cada cuánto se actualizan los datos?",
                 "Dos veces al día, en la mañana y en la tarde (hora de Chile). Las respuestas se pueden "
                 "guardar en caché por 30 minutos."),
                ("¿Hay un límite de consultas?",
                 "No hay un límite fijo, pero te pedimos guardar las respuestas en caché y no consultar "
                 "más de una vez cada 30 minutos desde un mismo servidor. Si muestras los datos en un "
                 "sitio con mucho tráfico, consúltalos desde tu servidor y no en cada visita."),
                ("¿Los valores son oficiales?",
                 "Son referenciales. Provienen de fuentes oficiales (Banco Central de Chile, SII e INE), "
                 "pero antes de usarlos en un pago, contrato o declaración, verifícalos en la fuente "
                 "oficial."),
            ],
            contexto={
                "endpoints": endpoints,
                "url_api": cfg["sitio"]["url"] + f"/api/{VERSION}/",
                "ejemplo_indicadores": _bonito(indicadores),
                "ejemplo_uf": _bonito({**uf, "serie": uf["serie"][:2]}),
                "uf_dias": len(uf["serie"]),
                "uf_desde": uf["desde"],
                "uf_hasta": uf["hasta"],
                "ejemplo_dolar": _bonito(dolar["serie"][-2:]),
                "ejemplo_feriado": _bonito(proximo),
                "anios_feriados": anios,
            },
            **comunes,
        ),
    ]
