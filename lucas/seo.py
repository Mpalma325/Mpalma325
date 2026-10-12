"""Datos estructurados (JSON-LD), sitemap.xml, robots.txt y otros archivos para buscadores."""

from __future__ import annotations

import datetime as dt
from xml.sax.saxutils import escape

from .confianza import equipo_de, redes_de


def url_absoluta(cfg: dict, ruta: str) -> str:
    return cfg["sitio"]["url"] + ruta


def _organizacion(cfg: dict) -> dict:
    sitio = cfg["sitio"]
    return {
        "@type": "Organization",
        "name": sitio["nombre"],
        "url": sitio["url"] + "/",
        "logo": sitio["url"] + "/estaticos/img/logo-512.png",
    }


def _persona(persona: dict) -> dict:
    """Person de schema.org para una entrada de ``sitio.equipo`` (ya limpia: confianza.equipo_de)."""
    datos = {"@type": "Person", "name": persona["nombre"]}
    if persona["rol"]:
        datos["jobTitle"] = persona["rol"]
    if persona["descripcion"]:
        datos["description"] = persona["descripcion"]
    if persona["enlace"]:
        datos["sameAs"] = [persona["enlace"]]
    return datos


def jsonld_organizacion(cfg: dict) -> dict:
    """Organization del sitio con lo que haya en config.yaml para generar confianza: correo de
    contacto (``email``), equipo (``founder``) y perfiles públicos (``sameAs``). Sin esos datos
    queda igual que la organización básica."""
    organizacion = {"@context": "https://schema.org", **_organizacion(cfg)}
    correo = (cfg["sitio"].get("correo_contacto") or "").strip()
    if correo:
        organizacion["email"] = correo
    equipo = equipo_de(cfg)
    if equipo:
        organizacion["founder"] = [_persona(persona) for persona in equipo]
    redes = redes_de(cfg)
    if redes:
        organizacion["sameAs"] = redes
    return organizacion


def jsonld_sitio(cfg: dict) -> list[dict]:
    sitio = cfg["sitio"]
    return [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": sitio["nombre"],
            "url": sitio["url"] + "/",
            "inLanguage": sitio["idioma"],
            "description": sitio["eslogan"],
        },
        jsonld_organizacion(cfg),
    ]


def jsonld_migas(cfg: dict, migas: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": nombre, "item": url_absoluta(cfg, ruta)}
            for i, (nombre, ruta) in enumerate(migas)
        ],
    }


def jsonld_faq(preguntas: list[tuple[str, str]]) -> dict:
    """FAQPage. Google ya no muestra resultados enriquecidos de FAQ para la mayoría de los
    sitios (desde 2023), pero el marcado sigue siendo válido y ayuda a otros buscadores."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": pregunta,
             "acceptedAnswer": {"@type": "Answer", "text": respuesta}}
            for pregunta, respuesta in preguntas
        ],
    }


def jsonld_aplicacion(cfg: dict, nombre: str, descripcion: str, ruta: str) -> dict:
    """WebApplication para calculadoras (sin valoraciones inventadas)."""
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": nombre,
        "description": descripcion,
        "url": url_absoluta(cfg, ruta),
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Cualquiera (navegador web)",
        "inLanguage": cfg["sitio"]["idioma"],
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CLP"},
    }


def jsonld_articulo(cfg: dict, titulo: str, descripcion: str, ruta: str, publicada: dt.date,
                    modificada: dt.date, palabras_clave: list[str] | None = None) -> dict:
    """Article para las guías. El autor y el editor son el propio sitio (Organization)."""
    organizacion = _organizacion(cfg)
    articulo = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": titulo,
        "description": descripcion,
        "image": cfg["sitio"]["url"] + "/estaticos/img/og.png",
        "datePublished": publicada.isoformat(),
        "dateModified": modificada.isoformat(),
        "inLanguage": cfg["sitio"]["idioma"],
        "author": organizacion,
        "publisher": organizacion,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url_absoluta(cfg, ruta)},
    }
    if palabras_clave:
        articulo["keywords"] = ", ".join(palabras_clave)
    return articulo


def sitemap_xml(cfg: dict, paginas: list, hoy: dt.date) -> str:
    """Solo las páginas indexables y canónicas, con la fecha de su último cambio real.

    Google ignora ``changefreq`` y ``priority``, y usa ``lastmod`` solo si es confiable: por
    eso cada página declara en ``modificada`` cuándo cambió su contenido (sin ese dato se usa
    hoy) y nunca se publica una fecha futura.
    """
    lineas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for pagina in paginas:
        if not pagina.en_sitemap or not pagina.indexar or pagina.canonica not in (None, pagina.ruta):
            continue
        ultima = min(pagina.modificada or hoy, hoy)
        lineas.append(
            "  <url>"
            f"<loc>{escape(url_absoluta(cfg, pagina.ruta))}</loc>"
            f"<lastmod>{ultima.isoformat()}</lastmod>"
            "</url>"
        )
    lineas.append("</urlset>")
    return "\n".join(lineas) + "\n"


def robots_txt(cfg: dict) -> str:
    return ("User-agent: *\n"
            "Allow: /\n"
            "Disallow: /404.html\n\n"
            f"Sitemap: {cfg['sitio']['url']}/sitemap.xml\n")


def ads_txt(cfg: dict) -> str | None:
    """ads.txt autoriza a Google a vender anuncios en el sitio (requerido por AdSense)."""
    publisher = (cfg["monetizacion"]["adsense"].get("publisher_id") or "").strip()
    if not publisher:
        return None
    publisher = publisher.replace("ca-pub-", "pub-")
    return f"google.com, {publisher}, DIRECT, f08c47fec0942fa0\n"


def cabeceras_cloudflare() -> str:
    """Archivo _headers (Cloudflare Pages/Workers): caché y cabeceras de seguridad."""
    return (
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  X-Frame-Options: SAMEORIGIN\n"
        "/estaticos/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        # API abierta (lucas/api.py): cualquier sitio puede leerla y guardarla 30 minutos.
        "/api/*\n"
        "  Access-Control-Allow-Origin: *\n"
        "  Cache-Control: public, max-age=1800\n"
        # Widget que insertan otros sitios: caché corta para poder corregirlo. Ninguna otra
        # regla puede fijar Cache-Control para estas rutas (Cloudflare uniría los valores).
        "/widget.js\n"
        "  Cache-Control: public, max-age=3600\n"
        # App instalable: el service worker se revisa siempre para que las versiones
        # nuevas lleguen de inmediato.
        "/sw.js\n"
        "  Cache-Control: no-cache\n"
        "/manifest.webmanifest\n"
        "  Cache-Control: public, max-age=86400\n"
    )
