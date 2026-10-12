"""Señales de confianza: fuentes enlazadas, equipo y JSON-LD de la organización, metodología con
historial de correcciones, indicadores previsionales y páginas legales."""

from __future__ import annotations

import copy
import datetime as dt
import json
import re

import pytest

from lucas import seo
from lucas.config import RAIZ, cargar_config, cargar_parametros
from lucas.confianza import (FUENTES_OFICIALES, cargar_correcciones, enlazar_fuentes, equipo_de,
                             nombre_fuente, redes_de, repositorio_de, vigencia)
from lucas.construir import construir, crear_contexto
from lucas.datos import comparar_uf_con_metodologia, comparar_utm_con_metodologia
from lucas.formato import pesos, redondear
from lucas.fuentes import ORDEN_FUENTES
from lucas.paginas import tabla_impuesto_pesos
from lucas.paginas_calculadoras_extra import porcentaje_corto
from lucas.paginas_previsionales import paginas_previsionales

from .conftest import HOY

D = dt.date

# Datos de ejemplo para las pruebas: no son personas reales.
CONFIANZA_EJEMPLO = {
    "correo_contacto": "contacto@ejemplo.cl",
    "equipo": [
        {"nombre": "Persona Uno", "rol": "Datos y fórmulas", "descripcion": "Revisa los parámetros.",
         "enlace": "https://www.linkedin.com/in/persona-uno/"},
        {"nombre": "Persona Dos", "rol": "Desarrollo", "enlace": "https://github.com/persona-dos"},
        {"nombre": "", "rol": "Sin nombre: se ignora"},
        {"nombre": "Persona Tres", "enlace": "http://inseguro.example"},
    ],
    "redes": ["https://www.instagram.com/ejemplo/", "no-es-una-url"],
    "repositorio": "https://github.com/ejemplo/saca-la-cuenta",
}


def _config_con_confianza() -> dict:
    cfg = copy.deepcopy(cargar_config())
    cfg["sitio"].update(copy.deepcopy(CONFIANZA_EJEMPLO))
    return cfg


def _leer(salida, ruta: str) -> str:
    return (salida / ruta.lstrip("/") / "index.html").read_text(encoding="utf-8")


def _jsonld(html: str) -> list[dict]:
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)]


def _parrafo_fuente(html: str) -> str:
    return re.search(r'<p class="fuente">.*?</p>', html, flags=re.S).group(0)


@pytest.fixture(scope="module")
def sitio(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio_confianza")
    construir(salida=salida, demo=True, hoy=HOY)
    return salida


@pytest.fixture(scope="module")
def sitio_con_equipo(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio_con_equipo")
    construir(salida=salida, demo=True, hoy=HOY, cfg=_config_con_confianza())
    return salida


@pytest.fixture(scope="module")
def contexto(datos_demo, params):
    return crear_contexto(cargar_config(), params, datos_demo, HOY, dt.datetime(2026, 10, 12, 7))


# --- Fuentes con enlace (macro m.fuente) ---------------------------------------

def test_enlaza_cada_organismo_una_vez():
    html = str(enlazar_fuentes("Banco Central de Chile e INE, publicado por el SII"))
    assert html.count("<a ") == 3
    assert '<a href="https://www.bcentral.cl/" rel="noopener" target="_blank">Banco Central de Chile</a>' in html
    # La sigla después del nombre completo no se enlaza dos veces
    html = str(enlazar_fuentes("Servicio de Impuestos Internos (SII)"))
    assert html.count("<a ") == 1 and html.endswith("</a> (SII)")
    # El nombre largo gana sobre el corto y no se enlazan pedazos de palabras
    assert str(enlazar_fuentes("Banco Central (UF)")).count("<a ") == 1
    assert "<a " not in str(enlazar_fuentes("MINEDUC y SIIX"))


def test_enlazar_fuentes_escapa_el_texto():
    html = str(enlazar_fuentes('<script>alert(1)</script> & SII'))
    assert "<script>" not in html and "&lt;script&gt;" in html and "&amp;" in html
    assert 'href="https://www.sii.cl/"' in html


def test_todas_las_fuentes_de_las_plantillas_tienen_enlace():
    """Cada texto de m.fuente nombra al menos un organismo conocido. Si agregas una fuente nueva,
    suma el organismo a FUENTES_OFICIALES (lucas/confianza.py) con su URL oficial verificada."""
    textos = set()
    for plantilla in (RAIZ / "plantillas").glob("*.html"):
        textos |= set(re.findall(r'm\.fuente\("([^"]+)"\)', plantilla.read_text(encoding="utf-8")))
    assert len(textos) >= 15
    sin_enlace = [t for t in textos if "<a " not in str(enlazar_fuentes(t))]
    assert sin_enlace == []


def test_urls_oficiales_son_https_de_dominios_oficiales():
    oficiales = ("bcentral.cl", "sii.cl", "ine.gob.cl", "spensiones.cl", "previred.com", "dt.gob.cl",
                 "bcn.cl", "cmfchile.cl")
    for nombre, url in FUENTES_OFICIALES.items():
        assert url.startswith("https://www.") and any(d in url for d in oficiales), nombre


def test_nombre_de_las_fuentes_de_los_parametros():
    assert nombre_fuente("https://www.spensiones.cl/portal/institucional/594/w3-article-16885.html") == \
        "Superintendencia de Pensiones"
    assert nombre_fuente("https://www.bcn.cl/leychile/navegar?idNorma=207436") == "Código del Trabajo"
    assert nombre_fuente("https://www.sii.cl/") == "Servicio de Impuestos Internos"
    assert nombre_fuente("https://ejemplo.org/x") == "ejemplo.org"


def test_macro_fuente_enlaza_en_las_paginas(sitio):
    fuente = _parrafo_fuente(_leer(sitio, "/uf/"))
    assert '<a href="https://www.bcentral.cl/" rel="noopener" target="_blank">Banco Central de Chile</a>' in fuente
    assert 'href="https://www.ine.gob.cl/"' in fuente and 'href="https://www.sii.cl/"' in fuente
    assert 'href="/metodologia/"' in fuente  # "Cómo calculamos"
    fuente = _parrafo_fuente(_leer(sitio, "/utm/"))
    assert fuente.count('href="https://www.sii.cl/"') == 1


# --- Equipo y JSON-LD de la organización ---------------------------------------

def test_jsonld_sin_datos_queda_como_antes():
    cfg = cargar_config()
    cfg["sitio"].update(correo_contacto="", equipo=[], redes=[])
    assert seo.jsonld_sitio(cfg)[1] == {
        "@context": "https://schema.org", "@type": "Organization", "name": "Saca la Cuenta",
        "url": "https://sacalacuenta.cl/", "logo": "https://sacalacuenta.cl/estaticos/img/logo-512.png"}
    sin_claves = copy.deepcopy(cfg)
    for clave in ("equipo", "redes", "repositorio"):
        sin_claves["sitio"].pop(clave, None)  # un config.yaml antiguo sin las claves nuevas
    assert seo.jsonld_organizacion(sin_claves) == seo.jsonld_sitio(cfg)[1]


def test_jsonld_con_correo_equipo_y_redes():
    organizacion = seo.jsonld_organizacion(_config_con_confianza())
    assert organizacion["email"] == "contacto@ejemplo.cl"
    assert organizacion["sameAs"] == ["https://www.instagram.com/ejemplo/"]
    assert organizacion["founder"] == [
        {"@type": "Person", "name": "Persona Uno", "jobTitle": "Datos y fórmulas",
         "description": "Revisa los parámetros.", "sameAs": ["https://www.linkedin.com/in/persona-uno/"]},
        {"@type": "Person", "name": "Persona Dos", "jobTitle": "Desarrollo",
         "sameAs": ["https://github.com/persona-dos"]},
        {"@type": "Person", "name": "Persona Tres"},  # el enlace sin https se omite
    ]


def test_equipo_redes_y_repositorio():
    cfg = _config_con_confianza()
    equipo = equipo_de(cfg)
    assert [p["nombre"] for p in equipo] == ["Persona Uno", "Persona Dos", "Persona Tres"]
    assert [p["red"] for p in equipo] == ["LinkedIn", "GitHub", ""]
    assert redes_de(cfg) == ["https://www.instagram.com/ejemplo/"]
    assert repositorio_de(cfg) == "https://github.com/ejemplo/saca-la-cuenta"


def test_config_yaml_de_confianza_bien_escrito():
    """Revisa lo que los dueños escriban en sitio.equipo, sitio.redes y sitio.repositorio."""
    sitio = cargar_config()["sitio"]
    equipo = sitio.get("equipo") or []
    assert isinstance(equipo, list), "sitio.equipo debe ser una lista"
    for persona in equipo:
        assert isinstance(persona, dict) and str(persona.get("nombre") or "").strip(), \
            f"Cada persona de sitio.equipo necesita un nombre: {persona!r}"
        enlace = persona.get("enlace")
        assert not enlace or str(enlace).startswith("https://"), \
            f"El enlace de {persona['nombre']} debe empezar con https://"
    redes = sitio.get("redes") or []
    assert isinstance(redes, list) and all(str(r).startswith("https://") for r in redes), \
        "sitio.redes debe ser una lista de direcciones que empiezan con https://"
    repositorio = sitio.get("repositorio") or ""
    assert not repositorio or str(repositorio).startswith("https://"), \
        "sitio.repositorio debe empezar con https://"


def test_acerca_sin_equipo_mantiene_el_texto(sitio):
    html = _leer(sitio, "/acerca/")
    assert "es un proyecto independiente hecho en Chile" in html
    assert "Quiénes hacemos" not in html
    for destino in ("/metodologia/", "/indicadores-previsionales/", "/metodologia/#correcciones", "/contacto/"):
        assert f'href="{destino}"' in html, destino
    for url in ("https://www.bcentral.cl/", "https://www.sii.cl/", "https://www.ine.gob.cl/"):
        assert f'href="{url}"' in html
    assert any(b.get("@type") == "Organization" for b in _jsonld(html))


def test_acerca_y_contacto_con_equipo(sitio_con_equipo):
    acerca = _leer(sitio_con_equipo, "/acerca/")
    assert "Quiénes hacemos" in acerca
    assert "Persona Uno" in acerca and "Perfil en LinkedIn" in acerca and "Perfil en GitHub" in acerca
    assert "mailto:contacto@ejemplo.cl" in acerca
    assert 'href="https://github.com/ejemplo/saca-la-cuenta"' in acerca
    for html in (acerca, _leer(sitio_con_equipo, "/")):
        organizacion = next(b for b in _jsonld(html) if b.get("@type") == "Organization")
        assert organizacion["email"] == "contacto@ejemplo.cl" and len(organizacion["founder"]) == 3
    contacto = _leer(sitio_con_equipo, "/contacto/")
    assert 'href="mailto:contacto@ejemplo.cl"' in contacto and "Todavía no publicamos" not in contacto
    assert 'href="mailto:contacto@ejemplo.cl"' in _leer(sitio_con_equipo, "/privacidad/")


# --- Metodología -----------------------------------------------------------------

def test_correcciones_de_octubre_de_2026():
    correcciones = cargar_correcciones()
    assert len(correcciones) >= 3
    textos = " ".join(c["titulo"] + " " + c["detalle"] for c in correcciones)
    for clave in ("obra o faena", "510.500", "último día del mes"):
        assert clave in textos, clave
    for correccion in correcciones:
        assert correccion["fecha"] <= dt.date.today() + dt.timedelta(days=1), correccion["titulo"]
    fechas = [c["fecha"] for c in correcciones]
    assert fechas == sorted(fechas, reverse=True)


def test_correcciones_mal_escritas(tmp_path):
    archivo = tmp_path / "correcciones.yaml"
    archivo.write_text("correcciones:\n  - fecha: 2026-10-12\n    titulo: Algo\n", encoding="utf-8")
    with pytest.raises(ValueError, match="detalle"):
        cargar_correcciones(archivo)
    archivo.write_text("correcciones:\n  - {fecha: 2026-10-12, titulo: A, detalle: B, paginas: [uf]}\n",
                       encoding="utf-8")
    with pytest.raises(ValueError, match="rutas internas"):
        cargar_correcciones(archivo)
    assert cargar_correcciones(tmp_path / "no-existe.yaml") == []


def test_vigencia_exacta_o_al_menos(params):
    assert vigencia(params, "topes_imponibles", HOY) == {"desde": D(2026, 2, 1), "exacta": True}
    assert vigencia(params, "salud", HOY)["exacta"] is False  # el 7% es anterior al registro
    aporte = vigencia(params, "cotizaciones_empleador", HOY, ("aporte_reforma_pensiones", "sis"))
    assert aporte == {"desde": D(2026, 8, 1), "exacta": True}
    mutual = vigencia(params, "cotizaciones_empleador", HOY, ("mutual_basica",))
    assert mutual == {"desde": D(2026, 1, 1), "exacta": False}


def test_pagina_de_metodologia(sitio, datos_demo, params):
    html = _leer(sitio, "/metodologia/")
    for ancla in ("fuentes", "actualizacion", "oficiales", "verificacion", "parametros", "correcciones"):
        assert f'id="{ancla}"' in html, ancla
    # Las fuentes de cada indicador salen de fuentes.ORDEN_FUENTES
    for nombre in ("UF", "UTM y UTA", "IPC", "Dólar observado", "Euro"):
        assert f"<td>{nombre}</td>" in html, nombre
    assert len(ORDEN_FUENTES) == 5
    assert "https://www.sii.cl/valores_y_fechas/uf/uf2026.htm" in html
    # La verificación usa los mismos datos con que se construye el sitio
    comparadas, diferencias = comparar_uf_con_metodologia(datos_demo.uf, datos_demo.ipc)
    assert f"{comparadas - len(diferencias):,}".replace(",", ".") + " de los " in html
    mantener = params.get("utm_se_mantiene_con_ipc_negativo")
    meses, _ = comparar_utm_con_metodologia(datos_demo.utm, datos_demo.ipc, mantener)
    assert f"recalculamos {meses} meses de UTM" in html
    assert "IPC usado fue negativo" in html
    # Historial de correcciones con enlaces a las páginas afectadas
    for correccion in cargar_correcciones():
        assert correccion["titulo"] in html
        for destino in correccion["paginas"]:
            assert f'href="{destino}"' in html and (sitio / destino.lstrip("/") / "index.html").exists()
    # Cada grupo de parámetros con su fuente
    for grupo, valor in params.crudo.items():
        if isinstance(valor, dict) and valor.get("fuente"):
            assert f'href="{valor["fuente"]}"' in html.replace("&amp;", "&"), grupo


def test_enlaces_del_pie_y_de_la_calculadora(sitio):
    html = _leer(sitio, "/uf/")
    assert 'href="/metodologia/">Metodología</a>' in html
    assert 'href="/indicadores-previsionales/">Indicadores previsionales</a>' in html
    assert 'href="/indicadores-previsionales/"' in _leer(sitio, "/calculadoras/sueldo-liquido/")
    sitemap = (sitio / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://sacalacuenta.cl/metodologia/" in sitemap
    assert "https://sacalacuenta.cl/indicadores-previsionales/" in sitemap


# --- Indicadores previsionales ---------------------------------------------------

def test_previsionales_usa_los_valores_de_p(contexto):
    p = contexto.p
    pagina = paginas_previsionales(contexto)[0]
    datos = pagina.contexto
    assert datos["uf"] == p["uf_topes"] and datos["fecha_uf"] == D(2026, 10, 31)
    assert datos["utm"] == p["utm"] and datos["uta"] == 12 * p["utm"]
    assert datos["topes"][0] == {"nombre": "AFP y salud", "uf": p["tope_imponible_uf"],
                                 "pesos": redondear(p["tope_imponible_uf"] * p["uf_topes"])}
    assert datos["topes"][1]["pesos"] == redondear(p["tope_cesantia_uf"] * p["uf_topes"])
    assert datos["minimos"][0] == ("Trabajadores de 18 a 65 años", p["imm"])
    assert datos["gratificacion_anual"] == p["gratificacion_tope_imm_anual"] * p["imm"]
    assert {a["nombre"]: a["total"] for a in datos["afps"]} == {
        p["nombres_afp"][k]: p["tasa_afp"] + v for k, v in p["comisiones_afp"].items()}
    assert [f["empleador"] for f in datos["cesantia"]] == list(p["cesantia_empleador"].values())
    assert (datos["aporte"], datos["sis"], datos["mutual"]) == (
        p["aporte_empleador_reforma"], p["sis"], p["mutual_basica"])
    assert datos["honorarios"] == p["retencion_honorarios"]
    assert datos["apv_mensual_uf"] == p["tope_apv_mensual_uf"]
    assert pagina.titulo == "Indicadores previsionales octubre 2026: topes, AFP, SIS y más"


def test_previsionales_tabla_de_impuesto_con_la_utm_del_mes(contexto):
    p = contexto.p
    tabla = paginas_previsionales(contexto)[0].contexto["tabla_impuesto"]
    assert tabla == tabla_impuesto_pesos(p, p["utm"])
    assert tabla[0]["hasta"] == pytest.approx(13.5 * p["utm"])
    otra = copy.copy(contexto)
    otra.p = dict(p, utm=70_000.0)
    tabla = paginas_previsionales(otra)[0].contexto["tabla_impuesto"]
    assert tabla[0]["hasta"] == pytest.approx(13.5 * 70_000)
    assert tabla[1]["rebaja"] == pytest.approx(0.54 * 70_000)


def test_pagina_de_indicadores_previsionales(sitio, contexto, params):
    p = contexto.p
    html = _leer(sitio, "/indicadores-previsionales/")
    tope = redondear(p["tope_imponible_uf"] * p["uf_topes"])
    for valor in (pesos(p["uf_topes"], 2), pesos(p["utm"]), pesos(12 * p["utm"]), pesos(tope), pesos(p["imm"]),
                  porcentaje_corto(p["retencion_honorarios"]), porcentaje_corto(p["aporte_empleador_reforma"]),
                  porcentaje_corto(p["mutual_basica"])):
        assert valor in html, valor
    for clave, comision in p["comisiones_afp"].items():
        assert f"<td>{p['nombres_afp'][clave]}</td><td class=\"num\">{porcentaje_corto(comision)}</td>" in html
    for fila in tabla_impuesto_pesos(p, p["utm"]):
        assert pesos(fila["rebaja"], 2) in html
    # Cada bloque con su vigencia y la fuente de su grupo en chile.yaml
    for grupo in ("topes_imponibles", "ingreso_minimo", "gratificacion", "afp", "salud",
                  "cotizaciones_empleador", "seguro_cesantia", "apv", "retencion_honorarios", "impuesto_unico"):
        assert f'href="{params[grupo]["fuente"]}"' in html.replace("&amp;", "&"), grupo
    assert html.count("Vigente desde el") + html.count("Vigente al menos desde el") >= 11
    assert "documento oficial" in html and 'href="https://www.previred.com/"' in html
    bloques = _jsonld(html)
    assert {b["@type"] for b in bloques} == {"BreadcrumbList", "FAQPage"}


# --- Páginas legales ---------------------------------------------------------------

def test_contacto_sin_correo_sigue_siendo_util(sitio):
    html = _leer(sitio, "/contacto/")
    assert "mailto:" not in html
    assert "Todavía no publicamos un correo de contacto" in html
    assert "Cómo reportar un error" in html and 'href="/metodologia/#correcciones"' in html
    assert 'href="https://www.previred.com/"' in html and 'href="/indicadores-previsionales/"' in html


def test_contacto_sin_correo_ofrece_el_repositorio_y_las_redes(datos_demo, params):
    from lucas.construir import crear_entorno
    from lucas.paginas import paginas_institucionales
    cfg = _config_con_confianza()
    cfg["sitio"]["correo_contacto"] = ""
    c = crear_contexto(cfg, params, datos_demo, HOY, dt.datetime(2026, 10, 12, 7))
    pagina = next(p for p in paginas_institucionales(c) if p.ruta == "/contacto/")
    html = crear_entorno(cfg, c, {}).get_template(pagina.plantilla).render(
        pagina=pagina, jsonld=pagina.jsonld, **pagina.contexto)
    assert "mailto:" not in html and "Todavía no publicamos un correo de contacto" in html
    assert 'href="https://github.com/ejemplo/saca-la-cuenta"' in html
    assert 'href="https://www.instagram.com/ejemplo/" rel="noopener" target="_blank">Instagram</a>' in html


def test_privacidad_cita_las_leyes_de_datos_personales(sitio):
    html = _leer(sitio, "/privacidad/")
    assert 'href="https://www.bcn.cl/leychile/navegar?idNorma=141599"' in html   # Ley 19.628
    assert 'href="https://www.bcn.cl/leychile/navegar?idNorma=1209272"' in html  # Ley 21.719
    assert "13 de diciembre de 2024" in html and "1 de diciembre de 2026" in html
    assert "18.623-07" in html  # proyecto que propone postergarla


def test_terminos_con_la_api_y_el_widget(sitio):
    html = _leer(sitio, "/terminos/")
    assert 'href="/api/#condiciones"' in html and 'href="/widget/"' in html
    assert "enlace visible" in html
    assert 'id="condiciones"' in _leer(sitio, "/api/")
