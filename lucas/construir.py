"""Construcción del sitio estático: arma el contexto, genera todas las páginas y
escribe el resultado en ``dist/`` (o la carpeta que se indique)."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

from . import __version__, formato, seo
from .calculos import contexto_parametros
from .config import RAIZ, Parametros, ahora_chile, cargar_config, cargar_parametros, hoy_chile
from .datos import Datos, cargar_datos, mes_siguiente, primer_dia, revisar_frescura

DIRECTORIO_DEMO = RAIZ / "tests" / "fixtures" / "datos_demo"


class ErrorConstruccion(Exception):
    pass


@dataclass
class Pagina:
    ruta: str                      # "/uf/" (con barra final) o "/404.html"
    plantilla: str                 # archivo en plantillas/
    titulo: str                    # <title>
    descripcion: str               # meta description
    h1: str = ""
    contexto: dict = field(default_factory=dict)
    migas: list[tuple[str, str]] = field(default_factory=list)
    faq: list[tuple[str, str]] = field(default_factory=list)
    clave: str = ""                # sección, para ubicar afiliados (p. ej. "ahorro")
    calculadora: bool = False      # incluye calculos.js
    datos_js: dict | None = None   # JSON para el JavaScript de la página
    jsonld: list[dict] = field(default_factory=list)
    prioridad: float = 0.6
    frecuencia: str = "daily"
    modificada: dt.date | None = None
    en_sitemap: bool = True
    indexar: bool = True

    @property
    def archivo(self) -> str:
        if self.ruta.endswith("/"):
            return self.ruta.lstrip("/") + "index.html"
        return self.ruta.lstrip("/")


@dataclass
class Contexto:
    cfg: dict
    params: Parametros
    datos: Datos
    hoy: dt.date
    ahora: dt.datetime
    p: dict                                 # parámetros vigentes para las calculadoras
    uf_hoy: float
    utm_hoy: float
    dolar: tuple[dt.date, float]
    euro: tuple[dt.date, float] | None
    ipc: tuple[dt.date, float]
    feriados_extra: list[dict]
    advertencias: list[str] = field(default_factory=list)


def crear_contexto(cfg: dict, params: Parametros, datos: Datos, hoy: dt.date,
                   ahora: dt.datetime) -> Contexto:
    errores, advertencias = revisar_frescura(datos, hoy)
    if errores:
        raise ErrorConstruccion("Datos insuficientes para construir el sitio:\n- " + "\n- ".join(errores))
    uf_hoy = datos.uf_dia(hoy)
    utm_hoy = datos.utm_mes(hoy) or Datos.ultimo(datos.utm_completa(), hoy)[1]
    # Los topes de la remuneración del mes se convierten con la UF del último día del mes
    # (o la última publicada, si aún no se conoce) y el tope de las indemnizaciones, con la
    # UF del último día del mes anterior (art. 172 del Código del Trabajo).
    fin_de_mes = mes_siguiente(primer_dia(hoy)) - dt.timedelta(days=1)
    uf_topes = Datos.ultimo(datos.uf_completa(), fin_de_mes)[1]
    uf_indemnizaciones = datos.uf_dia(primer_dia(hoy) - dt.timedelta(days=1)) or uf_hoy
    ultimo_ipc = max(datos.ipc)
    return Contexto(
        cfg=cfg,
        params=params,
        datos=datos,
        hoy=hoy,
        ahora=ahora,
        p=contexto_parametros(hoy, uf_hoy, utm_hoy, params, uf_topes, uf_indemnizaciones),
        uf_hoy=uf_hoy,
        utm_hoy=utm_hoy,
        dolar=Datos.ultimo(datos.dolar, hoy),
        euro=Datos.ultimo(datos.euro, hoy) if datos.euro_vigente(hoy) else None,
        ipc=(ultimo_ipc, datos.ipc[ultimo_ipc]),
        feriados_extra=params.feriados_extra(),
        advertencias=advertencias,
    )


# ---------------------------------------------------------------------------
# Jinja2
# ---------------------------------------------------------------------------

def _hash_archivo(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:10]


def crear_entorno(cfg: dict, c: Contexto, hashes: dict[str, str]) -> Environment:
    entorno = Environment(
        loader=FileSystemLoader(RAIZ / "plantillas"),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    base = cfg["sitio"]["ruta_base"]

    def ruta(destino: str) -> str:
        return base + destino

    def estatico(archivo: str) -> str:
        version = hashes.get(archivo)
        sufijo = f"?v={version}" if version else ""
        return f"{base}/estaticos/{archivo}{sufijo}"

    def afiliados_de(clave: str) -> list[dict]:
        return [a for a in cfg["monetizacion"].get("afiliados") or []
                if a.get("activo", True) and (clave in (a.get("secciones") or []) or "todas" in (a.get("secciones") or []))]

    for nombre in ("pesos", "numero", "porcentaje", "fecha_larga", "fecha_con_dia", "fecha_corta",
                   "dia_mes", "dia_semana", "nombre_mes", "capitalizar", "monto_corto"):
        entorno.filters[nombre] = getattr(formato, nombre)
    entorno.filters["mes_anio"] = lambda fecha: formato.mes_anio(fecha.year, fecha.month)
    entorno.filters["mes_de_anio"] = lambda fecha: formato.mes_de_anio(fecha.year, fecha.month)
    entorno.filters["json_seguro"] = lambda valor: Markup(
        json.dumps(valor, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))

    actualizado = c.datos.meta.get("actualizado")
    entorno.globals.update(
        sitio=cfg["sitio"],
        cfg=cfg,
        hoy=c.hoy,
        ahora=c.ahora,
        demo=c.datos.demo,
        version=__version__,
        ruta=ruta,
        estatico=estatico,
        afiliados_de=afiliados_de,
        url_absoluta=lambda r: seo.url_absoluta(cfg, r),
        actualizado=dt.datetime.fromisoformat(actualizado) if actualizado else c.ahora,
        cabecera={"uf": c.uf_hoy, "dolar": c.dolar, "utm": c.utm_hoy},
        hay_euro=c.euro is not None,
        # UF de los próximos días: el JavaScript muestra la del día del visitante
        # aunque el sitio se haya generado hace un par de días.
        uf_ventana={f.isoformat(): v for f, v in c.datos.uf_completa().items()
                    if c.hoy - dt.timedelta(days=1) <= f <= c.hoy + dt.timedelta(days=14)},
        adsense=cfg["monetizacion"]["adsense"],
        anuncios_activos=bool(cfg["monetizacion"]["adsense"].get("activo")
                              and cfg["monetizacion"]["adsense"].get("publisher_id")),
        analitica=cfg["analitica"],
        verificacion=cfg["verificacion"],
    )
    return entorno


# ---------------------------------------------------------------------------
# Construcción
# ---------------------------------------------------------------------------

def construir(salida: Path | None = None, demo: bool = False, hoy: dt.date | None = None,
              cfg: dict | None = None, directorio_datos: Path | None = None) -> dict:
    """Genera el sitio completo. Devuelve un resumen con la cantidad de páginas y advertencias."""
    from .paginas import todas_las_paginas  # import diferido: paginas importa este módulo
    from .api import escribir_api

    salida = Path(salida or RAIZ / "dist")
    cfg = cfg or cargar_config()
    params = cargar_parametros()
    if directorio_datos is None:
        directorio_datos = DIRECTORIO_DEMO if demo else RAIZ / "data"
    datos = cargar_datos(directorio_datos,
                         mantener_utm_si_ipc_negativo=params.get("utm_se_mantiene_con_ipc_negativo", True))
    if datos.demo and not demo:
        raise ErrorConstruccion("Los datos cargados son de demostración; usa --demo o descarga datos reales.")
    if demo:
        datos.meta["demo"] = True
    hoy = hoy or hoy_chile()
    ahora = ahora_chile() if hoy == hoy_chile() else dt.datetime.combine(hoy, dt.time(7, 0))
    c = crear_contexto(cfg, params, datos, hoy, ahora)

    estaticos = RAIZ / "estaticos"
    hashes = {str(r.relative_to(estaticos)).replace("\\", "/"): _hash_archivo(r)
              for r in estaticos.rglob("*") if r.is_file()}
    entorno = crear_entorno(cfg, c, hashes)

    paginas = todas_las_paginas(c)
    rutas = [p.ruta for p in paginas]
    repetidas = {r for r in rutas if rutas.count(r) > 1}
    if repetidas:
        raise ErrorConstruccion(f"Rutas repetidas: {sorted(repetidas)}")

    if salida.exists():
        shutil.rmtree(salida)
    salida.mkdir(parents=True)
    shutil.copytree(estaticos, salida / "estaticos")

    for pagina in paginas:
        jsonld = list(pagina.jsonld)
        if len(pagina.migas) > 1:
            jsonld.append(seo.jsonld_migas(cfg, pagina.migas))
        if pagina.faq:
            jsonld.append(seo.jsonld_faq(pagina.faq))
        plantilla = entorno.get_template(pagina.plantilla)
        html = plantilla.render(pagina=pagina, jsonld=jsonld, **pagina.contexto)
        destino = salida / pagina.archivo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(html, encoding="utf-8")

    (salida / "sitemap.xml").write_text(seo.sitemap_xml(cfg, paginas, hoy), encoding="utf-8")
    (salida / "robots.txt").write_text(seo.robots_txt(cfg), encoding="utf-8")
    (salida / "_headers").write_text(seo.cabeceras_cloudflare(), encoding="utf-8")
    escribir_api(salida, c)  # /api/v1/*.json y /widget.js
    ads = seo.ads_txt(cfg)
    if ads:
        (salida / "ads.txt").write_text(ads, encoding="utf-8")
    clave_indexnow = (cfg.get("indexnow") or {}).get("clave", "").strip()
    if clave_indexnow:
        (salida / f"{clave_indexnow}.txt").write_text(clave_indexnow, encoding="utf-8")
    (salida / "favicon.ico").write_bytes((estaticos / "img" / "favicon.ico").read_bytes())

    return {
        "paginas": len(paginas),
        "salida": str(salida),
        "hoy": hoy.isoformat(),
        "demo": datos.demo,
        "advertencias": c.advertencias,
        "rutas": rutas,
    }
