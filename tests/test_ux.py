"""Experiencia de uso y accesibilidad de las calculadoras: contraste, bloques de anuncios,
resultados en el HTML inicial, anuncios para lectores de pantalla, compartir, guías
relacionadas, gráficos y el <head>.

La interacción en un navegador real (CLS, axe-core, hash mal formado, tablas con teclado) se
revisa con Playwright fuera de las pruebas; aquí se prueba lo que no necesita un navegador.
"""

from __future__ import annotations

import copy
import datetime as dt
import json
import re
import shutil
import subprocess
from urllib.parse import quote

import pytest

from lucas import calculos, construir as construccion
from lucas.config import cargar_config
from lucas.construir import Pagina, construir
from lucas.feriados import dias_habiles_entre, feriados_nacionales
from lucas.formato import fecha_con_dia, mes_anio, numero, pesos, porcentaje
from lucas.graficos import grafico_ahorro, grafico_barras, grafico_linea
from lucas.guias import cargar_guias, contexto_de_revision
from lucas.paginas_calculadoras_extra import leido_del_formulario, texto_tiempo

from .conftest import HOY, RAIZ

NODE = shutil.which("node")
CSS = (RAIZ / "estaticos" / "css" / "estilos.css").read_text(encoding="utf-8")
APP_JS = (RAIZ / "estaticos" / "js" / "app.js").read_text(encoding="utf-8")
PUBLISHER = "ca-pub-1234567890123456"

CALCULADORAS = {
    "/calculadoras/sueldo-liquido/": "resultado-sueldo",
    "/calculadoras/boleta-honorarios/": "resultado-honorarios",
    "/calculadoras/reajuste-arriendo-ipc/": "resultado-arriendo",
    "/calculadoras/credito-hipotecario/": "resultado-hipotecario",
    "/calculadoras/interes-compuesto/": "resultado-ahorro",
    "/calculadoras/dias-habiles/": "resultado-dias",
    "/calculadoras/finiquito/": "resultado-finiquito",
    "/calculadoras/vacaciones-proporcionales/": "resultado-vacaciones",
    "/calculadoras/iva/": "resultado-iva",
    "/calculadoras/horas-extra/": "resultado-horas-extra",
    "/calculadoras/credito-consumo/": "resultado-consumo",
}


def leer(sitio, ruta: str) -> str:
    return (sitio / ruta.strip("/") / "index.html").read_text(encoding="utf-8")


def resultado_de(html: str, identificador: str) -> str:
    """El HTML del recuadro de resultado (hasta el cierre del layout de la calculadora)."""
    inicio = html.index(f'id="{identificador}"')
    return html[inicio:html.index("\n</div>\n</div>", inicio)]


def valor_de(html: str, clave: str) -> str:
    return re.search(rf'data-r="{clave}">(.*?)</', html, flags=re.S).group(1).strip()


@pytest.fixture(scope="module")
def sitio(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio_ux")
    construir(salida=salida, demo=True, hoy=HOY)
    return salida


@pytest.fixture(scope="module")
def sitio_con_anuncios(tmp_path_factory):
    """Sitio demo con los bloques de AdSense visibles: en modo demo la macro no muestra nada,
    así que se activan en el entorno de Jinja (solo para revisar su ubicación y su código)."""
    import lucas.paginas  # noqa: F401  (carga los módulos antes de parchear)

    salida = tmp_path_factory.mktemp("sitio_ux_anuncios")
    nombres = set()
    for plantilla in (RAIZ / "plantillas").glob("*.html"):
        nombres.update(re.findall(r'm\.anuncio\("([a-z_]+)"\)', plantilla.read_text(encoding="utf-8")))
    cfg = copy.deepcopy(cargar_config())
    cfg["monetizacion"]["adsense"].update(activo=True, publisher_id=PUBLISHER,
                                          slots={n: str(1000 + i) for i, n in enumerate(sorted(nombres))})
    original = construccion.crear_entorno

    def con_anuncios(cfg_, c, hashes):
        entorno = original(cfg_, c, hashes)
        entorno.globals.update(demo=False, anuncios_activos=True)
        return entorno

    with pytest.MonkeyPatch.context() as parche:
        parche.setattr(construccion, "crear_entorno", con_anuncios)
        construir(salida=salida, demo=True, hoy=HOY, cfg=cfg)
    return salida


@pytest.fixture(scope="module")
def contexto():
    return contexto_de_revision(demo=True, hoy=HOY)


# ---------------------------------------------------------------------------
# Contraste (WCAG 2.x), calculado con los colores de estilos.css
# ---------------------------------------------------------------------------

def _variables(bloque: str) -> dict[str, str]:
    return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{3,6})\b", bloque))


def _temas() -> dict[str, dict[str, str]]:
    claro = _variables(re.search(r"^:root \{(.*?)^\}", CSS, flags=re.M | re.S).group(1))
    oscuro = dict(claro)
    oscuro.update(_variables(re.search(r"@media \(prefers-color-scheme: dark\) \{\s*:root \{(.*?)\}", CSS,
                                       flags=re.S).group(1)))
    return {"claro": claro, "oscuro": oscuro}


def _rgb(color: str) -> tuple[float, ...]:
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(c * 2 for c in color)
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def _mezcla(frente: str, fondo: str, alfa: float) -> tuple[float, ...]:
    return tuple(alfa * a + (1 - alfa) * b for a, b in zip(_rgb(frente), _rgb(fondo)))


def contraste(a, b) -> float:
    def luminancia(color):
        canales = [v / 255 for v in (_rgb(color) if isinstance(color, str) else color)]
        r, g, b_ = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in canales]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b_
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


@pytest.mark.parametrize("tema", ["claro", "oscuro"])
def test_contrastes_cumplen_wcag(tema):
    v = _temas()[tema]
    # Botones (.boton): texto --sobre-primario sobre --primario y, al pasar el mouse, --primario-fuerte
    assert contraste(v["sobre-primario"], v["primario"]) >= 4.5
    assert contraste(v["sobre-primario"], v["primario-fuerte"]) >= 4.5
    # .destacado: etiqueta blanca al 90% sobre el inicio del degradado
    assert contraste(_mezcla("#ffffff", v["destacado-inicio"], 0.9), v["destacado-inicio"]) >= 4.5
    # Borde de los campos (WCAG 1.4.11): 3:1 con la superficie y con el fondo del campo
    assert contraste(v["borde-campo"], v["superficie"]) >= 3
    assert contraste(v["borde-campo"], v["fondo"]) >= 3
    # Anillo de foco: --primario sólido sobre la superficie
    assert contraste(v["primario"], v["superficie"]) >= 3
    # Feriados pasados: --texto-suave sobre la superficie
    assert contraste(v["texto-suave"], v["superficie"]) >= 4.5


def test_reglas_de_contraste_usan_las_variables():
    assert re.search(r"\.boton \{[^}]*color: var\(--sobre-primario\)", CSS)
    assert re.search(r"\.boton:hover \{[^}]*color: var\(--sobre-primario\)", CSS)
    assert "linear-gradient(135deg, var(--destacado-inicio)" in CSS
    assert re.search(r"input, select \{[^}]*border: 1px solid var\(--borde-campo\)", CSS)
    assert "input:focus, select:focus { outline: 3px solid var(--primario);" in CSS
    pasado = re.search(r"\.tabla-feriados \.pasado \{([^}]*)\}", CSS).group(1)
    assert "opacity" not in pasado and "var(--texto-suave)" in pasado
    # Antes: blanco sobre #2fbfb1 (2,3:1) y etiqueta del destacado (2,1:1); ahora pasan
    assert contraste("#ffffff", "#2fbfb1") < 3 <= 4.5 <= contraste(_temas()["oscuro"]["sobre-primario"], "#2fbfb1")


def test_solo_lectores_y_foco_de_tablas():
    assert re.search(r"\.solo-lectores \{[^}]*clip: rect\(0, 0, 0, 0\)", CSS)
    assert ".tabla-desplazable:focus-visible" in CSS


# ---------------------------------------------------------------------------
# Bloques de anuncios
# ---------------------------------------------------------------------------

def _anuncio(contexto, **globales) -> str:
    _, entorno = contexto
    entorno = entorno.overlay()
    entorno.globals.update(globales)
    plantilla = entorno.from_string('{% import "_macros.html" as m with context %}{{ m.anuncio("uf_superior") }}')
    return plantilla.render()


def test_macro_anuncio_aside_con_rotulo_y_tamano_fijo(contexto):
    adsense = {"activo": True, "publisher_id": PUBLISHER, "slots": {"uf_superior": "555"}}
    html = _anuncio(contexto, demo=False, anuncios_activos=True, adsense=adsense)
    assert '<aside class="anuncio" aria-labelledby="anuncio-uf_superior">' in html
    # Rótulo visible: AdSense solo admite "Anuncios" o "Enlaces patrocinados"
    assert '<p class="anuncio-etiqueta" id="anuncio-uf_superior">Anuncios</p>' in html
    ins = re.search(r"<ins [^>]*>", html, flags=re.S).group(0)
    assert 'class="adsbygoogle anuncio-bloque"' in ins and 'style="display:inline-block"' in ins
    assert f'data-ad-client="{PUBLISHER}"' in ins and 'data-ad-slot="555"' in ins
    # Tamaño exacto (método de AdSense): sin formato adaptable ni ancho completo
    assert "data-ad-format" not in ins and "data-full-width-responsive" not in ins
    assert "<div" not in html and "aria-label=" not in html
    # Sin slot, en modo demo o sin anuncios activos no se muestra nada
    assert _anuncio(contexto, demo=True, anuncios_activos=True, adsense=adsense).strip() == ""
    assert _anuncio(contexto, demo=False, anuncios_activos=False, adsense=adsense).strip() == ""
    assert _anuncio(contexto, demo=False, anuncios_activos=True, adsense={**adsense, "slots": {}}).strip() == ""


def test_css_reserva_el_alto_del_anuncio():
    assert re.search(r"\.anuncio-bloque \{[^}]*width: 336px;[^}]*max-width: 100%;[^}]*height: 280px;", CSS)
    assert re.search(r"@media \(min-width: 760px\) \{ \.anuncio-bloque \{ width: 728px; height: 250px; \} \}", CSS)
    assert "min-height: 100px" not in CSS
    # Respaldo contra clics accidentales si no hay contenido entre el anuncio y la FAQ
    assert re.search(r"\.anuncio \+ \.faq \{ margin-top: 7\.5rem; \}", CSS)


_INTERACTIVOS = re.compile(r'<(?:button|input|select|textarea|summary)\b|class="boton\b')


@pytest.mark.parametrize("ruta", sorted(CALCULADORAS))
def test_anuncio_de_calculadora_despues_de_la_primera_seccion(sitio_con_anuncios, ruta):
    html = leer(sitio_con_anuncios, ruta)
    assert html.count('<aside class="anuncio"') == 1, ruta
    anuncio = html.index('<aside class="anuncio"')
    fin_anuncio = html.index("</aside>", anuncio)
    # Antes del anuncio: la calculadora completa y al menos una sección explicativa
    fin_calculadora = html.index("\n</div>\n</div>", html.index('class="calculadora-layout"'))
    entre = html[fin_calculadora:anuncio]
    assert "<h2" in entre and "</section>" in entre, ruta
    assert not _INTERACTIVOS.search(entre), ruta
    # Después: una sección de contenido (no la FAQ) antes del próximo campo o botón
    siguiente = _INTERACTIVOS.search(html, fin_anuncio)
    tramo = html[fin_anuncio:siguiente.start() if siguiente else len(html)]
    assert re.search(r'<section(?! class="faq")', tramo), ruta


def test_indice_de_calculadoras_sin_anuncio_e_ipc_bajo_la_tabla(sitio_con_anuncios):
    assert 'class="anuncio"' not in leer(sitio_con_anuncios, "/calculadoras/")
    ipc = leer(sitio_con_anuncios, "/ipc/")
    assert ipc.count('<aside class="anuncio"') == 1
    assert ipc.index("IPC de los últimos 24 meses") < ipc.index("</table>") < ipc.index('<aside class="anuncio"')
    assert ipc.index('<aside class="anuncio"') > ipc.index('class="figura"')


def test_sitio_con_anuncios_declara_la_cuenta(sitio_con_anuncios):
    inicio = (sitio_con_anuncios / "index.html").read_text(encoding="utf-8")
    assert f'<meta name="google-adsense-account" content="{PUBLISHER}">' in inicio


# ---------------------------------------------------------------------------
# <head>: canónica y cuenta de AdSense
# ---------------------------------------------------------------------------

def _render_pagina(contexto, pagina: Pagina, **globales) -> str:
    _, entorno = contexto
    entorno = entorno.overlay()
    entorno.globals.update(globales)
    return entorno.get_template(pagina.plantilla).render(pagina=pagina, jsonld=[], **pagina.contexto)


def test_404_sin_canonica(sitio):
    html = (sitio / "404.html").read_text(encoding="utf-8")
    assert 'rel="canonical"' not in html and '<meta name="robots" content="noindex">' in html
    assert '<link rel="canonical" href="https://lucasclaras.cl/calculadoras/iva/">' in leer(sitio, "/calculadoras/iva/")


def test_meta_de_adsense_aunque_los_anuncios_no_esten_activos(contexto):
    pagina = Pagina(ruta="/contacto/", plantilla="contacto.html", titulo="Contacto", descripcion="d" * 60, h1="Contacto")
    activo_no = {"activo": False, "publisher_id": PUBLISHER, "slots": {}}
    html = _render_pagina(contexto, pagina, adsense=activo_no, anuncios_activos=False)
    assert f'<meta name="google-adsense-account" content="{PUBLISHER}">' in html
    assert "adsbygoogle.js" not in html
    sin_cuenta = _render_pagina(contexto, pagina, adsense={"activo": False, "publisher_id": "", "slots": {}})
    assert "google-adsense-account" not in sin_cuenta


# ---------------------------------------------------------------------------
# Calculadoras: anuncio para lectores, compartir, valores iniciales y guías
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ruta", sorted(CALCULADORAS))
def test_resultado_accesible_y_para_compartir(sitio, ruta):
    html = leer(sitio, ruta)
    resultado = resultado_de(html, CALCULADORAS[ruta])
    assert resultado.startswith(f'id="{CALCULADORAS[ruta]}">'), "el contenedor no debe llevar aria-live"
    assert resultado.count('<p class="solo-lectores" role="status" aria-live="polite" data-r-anuncio></p>') == 1
    assert html.count("aria-live") == 1, ruta
    assert "data-compartir" in resultado, ruta
    whatsapp = re.search(r'<a class="boton-secundario" href="([^"]+)" data-whatsapp="([^"]+)"', resultado)
    assert whatsapp, ruta
    h1 = re.search(r"<h1>(.*?)</h1>", html).group(1)
    assert whatsapp.group(2) == h1
    assert whatsapp.group(1).startswith("https://wa.me/?text=")
    assert quote(f"https://lucasclaras.cl{ruta}") in whatsapp.group(1)
    # El resultado principal ya viene calculado en el HTML (buscadores y sin JavaScript)
    principal = re.search(r'class="resultado-principal" data-r="[a-z_]+">(.*?)</p>', resultado).group(1)
    assert principal and principal != "—", ruta
    assert ">—<" not in resultado, ruta


def test_valores_iniciales_arriendo(sitio, datos_demo):
    html = resultado_de(leer(sitio, "/calculadoras/reajuste-arriendo-ipc/"), "resultado-arriendo")
    meses = sorted(datos_demo.ipc)[-6:]
    r = calculos.reajustar_por_ipc(500_000, [datos_demo.ipc[m] for m in meses])
    assert valor_de(html, "nuevo") == pesos(r["nuevo_monto"])
    assert valor_de(html, "variacion") == porcentaje(r["variacion"], 2, True)
    assert valor_de(html, "diferencia") == pesos(r["diferencia"])
    assert valor_de(html, "meses") == f"6 ({mes_anio(meses[0].year, meses[0].month)} a {mes_anio(meses[-1].year, meses[-1].month)})"
    formulario = leer(sitio, "/calculadoras/reajuste-arriendo-ipc/")
    assert f'<option value="{meses[0]:%Y-%m}" selected>' in formulario


def test_valores_iniciales_hipotecario_e_interes(sitio):
    pagina = leer(sitio, "/calculadoras/credito-hipotecario/")
    datos = json.loads(re.search(r'id="datos-pagina">(.*?)</script>', pagina).group(1))
    p = datos["parametros"]
    tasa = leido_del_formulario(p["tasa_hipotecaria_referencia"] * 100, 2) / 100
    r = calculos.simular_hipotecario(3000, 0.2, tasa, 25, p)
    html = resultado_de(pagina, "resultado-hipotecario")
    assert valor_de(html, "dividendo_uf") == numero(r["dividendo_total_uf"], 2) + " UF"
    assert valor_de(html, "dividendo_pesos") == pesos(r["dividendo_pesos"])
    assert valor_de(html, "credito") == f"{numero(r['credito_uf'])} UF ({pesos(r['credito_uf'] * p['uf'])})"
    assert valor_de(html, "renta") == pesos(r["renta_minima"])
    assert valor_de(html, "total") == numero(r["total_pagado_uf"]) + " UF"
    assert html.count("<tr><td>") == 25  # saldo año a año

    html = resultado_de(leer(sitio, "/calculadoras/interes-compuesto/"), "resultado-ahorro")
    a = calculos.proyectar_ahorro(1_000_000, 100_000, 0.05, 10)
    assert valor_de(html, "saldo") == pesos(a["saldo"]) == "$17.065.211"
    assert valor_de(html, "aportado") == pesos(a["aportado"])
    assert valor_de(html, "ganancia") == pesos(a["ganancia"])
    lienzo = re.search(r'<div class="grafico-ahorro-lienzo" data-r="grafico">(.*?)</div>', html, flags=re.S).group(1)
    assert lienzo.startswith('<svg class="grafico" viewBox="0 0 320 160">') and lienzo.count("<rect") == 22
    assert '<p class="leyenda">' in html  # la leyenda es fija: el JavaScript solo redibuja el SVG


def test_valores_iniciales_dias_habiles_finiquito_y_vacaciones(sitio, params):
    html = resultado_de(leer(sitio, "/calculadoras/dias-habiles/"), "resultado-dias")
    fin = HOY.replace(day=28)
    assert valor_de(html, "principal") == str(dias_habiles_entre(HOY, fin, params.feriados_extra()))
    assert valor_de(html, "detalle") == f"Entre el {fecha_con_dia(HOY)} y el {fecha_con_dia(fin)}."
    excluidos = [f for f in feriados_nacionales(HOY.year, params.feriados_extra()) if HOY <= f.fecha <= fin]
    for feriado in excluidos:
        assert f"<li>Se excluye el feriado del {fecha_con_dia(feriado.fecha)}: {feriado.nombre}</li>" in html
    assert html.count("<li>") == len(excluidos) == 1  # el 12 de octubre de 2026

    # Mismo texto que textoTiempo en app.js (antes decía "3 años, 7 meses y 1 días" y cambiaba al cargar)
    tiempo = valor_de(resultado_de(leer(sitio, "/calculadoras/finiquito/"), "resultado-finiquito"), "tiempo")
    t = calculos.tiempo_trabajado(calculos.sumar_meses(HOY, -43), HOY)
    assert tiempo == texto_tiempo(t["anios"], t["meses"], t["dias"]) == "3 años, 7 meses, 1 día"
    periodo = valor_de(resultado_de(leer(sitio, "/calculadoras/vacaciones-proporcionales/"),
                                    "resultado-vacaciones"), "periodo")
    proporcional = calculos.feriado_proporcional(calculos.sumar_meses(HOY, -8), HOY, _p_demo(sitio))
    assert periodo == texto_tiempo(0, proporcional["meses"], proporcional["dias"]) == "8 meses, 1 día"


def _campo(html: str, identificador: str) -> str:
    return re.search(rf'id="{identificador}"[^>]*value="([^"]*)"', html).group(1)


def test_valores_por_defecto_del_formulario_son_los_del_resultado_inicial(sitio):
    """El resultado inicial se calcula en Python con estos valores: si cambia el valor por
    defecto de un campo, hay que cambiarlo también en lucas/paginas.py (paginas_calculadoras)."""
    arriendo = leer(sitio, "/calculadoras/reajuste-arriendo-ipc/")
    assert _campo(arriendo, "a-monto") == "500.000"
    hipotecario = leer(sitio, "/calculadoras/credito-hipotecario/")
    assert (_campo(hipotecario, "hi-valor"), _campo(hipotecario, "hi-pie"), _campo(hipotecario, "hi-seguros")) == ("3.000", "20", "0")
    assert '<option value="25" selected>' in hipotecario
    ahorro = leer(sitio, "/calculadoras/interes-compuesto/")
    assert [_campo(ahorro, c) for c in ("ah-inicial", "ah-aporte", "ah-tasa", "ah-anios")] == ["1.000.000", "100.000", "5", "10"]
    dias = leer(sitio, "/calculadoras/dias-habiles/")
    assert (_campo(dias, "d-inicio"), _campo(dias, "d-fin")) == (HOY.isoformat(), HOY.replace(day=28).isoformat())
    assert 'name="incluir_inicio" checked' in dias and 'name="sabados">' in dias
    assert _campo(leer(sitio, "/calculadoras/boleta-honorarios/"), "h-monto") == "1.000.000"


def test_tabla_de_dias_habiles_por_mes(sitio, params):
    html = leer(sitio, "/calculadoras/dias-habiles/")
    assert f"Días hábiles de cada mes de {HOY.year}" in html
    filas = re.findall(r"<tr(?: class=\"fila-hoy\")?><td>([^<]+)</td><td class=\"num\">(\d+)</td>", html)
    assert len(filas) == 12
    octubre = dias_habiles_entre(dt.date(2026, 10, 1), dt.date(2026, 10, 31), params.feriados_extra())
    assert ("Octubre", str(octubre)) in filas and octubre == 21
    assert '<tr class="fila-hoy"><td>Octubre</td>' in html


def test_honorarios_tiene_resultado_principal(sitio):
    html = resultado_de(leer(sitio, "/calculadoras/boleta-honorarios/"), "resultado-honorarios")
    assert '<p class="resultado-etiqueta" data-r="etiqueta">Monto líquido</p>' in html
    assert valor_de(html, "principal") == pesos(calculos.honorarios_desde_bruto(1_000_000, _p_demo(sitio))["liquido"])


def _p_demo(sitio) -> dict:
    html = leer(sitio, "/calculadoras/boleta-honorarios/")
    return json.loads(re.search(r'id="datos-pagina">(.*?)</script>', html).group(1))["parametros"]


def test_guias_relacionadas(sitio, contexto):
    c, entorno = contexto
    guias = cargar_guias(c, entorno)
    enlaces = {}
    for ruta in list(CALCULADORAS) + ["/ipc/"]:
        html = leer(sitio, ruta)
        esperadas = {g.ruta for g in guias if ruta in g.calculadoras}
        if not esperadas:
            assert "Guías relacionadas" not in html, ruta
            continue
        bloque = html[html.index('<section class="guias-relacionadas"'):]
        bloque = bloque[:bloque.index("</section>")]
        enlaces[ruta] = re.findall(r'href="([^"]+)"', bloque)
        assert sorted(enlaces[ruta]) == sorted(esperadas), ruta
    # Primero las guías cuya calculadora principal es esta página; luego por su orden
    assert enlaces["/calculadoras/credito-hipotecario/"] == ["/guias/credito-hipotecario-en-uf/", "/guias/que-es-la-uf/"]
    assert enlaces["/calculadoras/sueldo-liquido/"][0] == "/guias/como-calcular-el-sueldo-liquido/"
    assert enlaces["/calculadoras/sueldo-liquido/"][-1] == "/guias/jornada-laboral-42-horas-y-horas-extra/"
    assert len(enlaces["/calculadoras/sueldo-liquido/"]) == 5


def test_global_guias_de(contexto):
    c, entorno = contexto
    c.guias = cargar_guias(c, entorno)
    try:
        rutas = [g.ruta for g in entorno.globals["guias_de"]("/calculadoras/finiquito/")]
        assert rutas == ["/guias/como-calcular-el-finiquito/"]
        assert entorno.globals["guias_de"]("/calculadoras/no-existe/") == []
    finally:
        c.guias = []


def test_dias_habiles_tiene_boton_copiar(sitio):
    html = resultado_de(leer(sitio, "/calculadoras/dias-habiles/"), "resultado-dias")
    assert "data-compartir" in html and "data-whatsapp" in html


# ---------------------------------------------------------------------------
# Portada, gráficos y CSS
# ---------------------------------------------------------------------------

def test_portada_con_indicadores_en_dos_columnas(sitio):
    inicio = (sitio / "index.html").read_text(encoding="utf-8")
    assert '<section class="tarjetas tarjetas-indicadores" aria-label="Indicadores de hoy">' in inicio
    movil = re.search(r"@media \(max-width: 40rem\) \{\s*\.tarjetas-indicadores \{ grid-template-columns: "
                      r"repeat\(2, minmax\(0, 1fr\)\);", CSS)
    assert movil


def test_graficos_angostos_y_figura_limitada():
    puntos = [(dt.date(2026, 1, 1) + dt.timedelta(days=30 * i), 38_000 + 50 * i) for i in range(12)]
    assert 'viewBox="0 0 480 240"' in grafico_linea(puntos, "UF")
    barras = grafico_barras([(dt.date(2025, m, 1), 0.3) for m in range(1, 13)], "IPC")
    assert 'viewBox="0 0 480 240"' in barras
    # La primera y la última fecha quedan dentro del gráfico
    etiquetas = re.findall(r'<text class="g-texto" x="([\d.]+)" y="232" text-anchor="(\w+)">', barras)
    assert [a for _, a in etiquetas] == ["start", "middle", "end"]
    assert float(etiquetas[-1][0]) <= 480 - 10
    assert re.search(r"\.figura \{[^}]*max-width: 760px;", CSS)
    assert re.search(r"\.grafico-ahorro-lienzo \{ aspect-ratio: 2 / 1; \}", CSS)


def test_texto_tiempo():
    assert texto_tiempo(0, 8, 0) == "8 meses, 0 días"
    assert texto_tiempo(1, 1, 1) == "1 año, 1 mes, 1 día"
    assert texto_tiempo(3, 7, 12) == "3 años, 7 meses, 12 días"
    assert leido_del_formulario(4.2, 2) == 4.2 and leido_del_formulario(0.0425 * 100, 2) == 4.25


# ---------------------------------------------------------------------------
# app.js: funciones puras comparadas con Python en Node
# ---------------------------------------------------------------------------

def funcion_de_app(nombre: str) -> str:
    """Código de una función de primer nivel de app.js (dentro de la IIFE, con 2 espacios)."""
    encontrada = re.search(rf"^  function {nombre}\(.*?^  \}}$", APP_JS, flags=re.M | re.S)
    assert encontrada, nombre
    return encontrada.group(0)


PROGRAMA = r"""
let entrada = '';
process.stdin.on('data', d => entrada += d);
process.stdin.on('end', () => {
  const { codigo, nombres, casos } = JSON.parse(entrada);
  const f = new Function(codigo + '\nreturn {' + nombres.map(n => n + ': ' + n).join(', ') + '};')();
  process.stdout.write(JSON.stringify(casos.map(c => f[c.fn].apply(null, c.args))));
});
"""


def ejecutar_app(nombres: list[str], casos: list[tuple[str, list]]) -> list:
    entrada = {"codigo": "\n".join(funcion_de_app(n) for n in nombres), "nombres": nombres,
               "casos": [{"fn": fn, "args": args} for fn, args in casos]}
    resultado = subprocess.run([NODE, "-e", PROGRAMA], input=json.dumps(entrada), capture_output=True,
                               text=True, check=True, timeout=60)
    return json.loads(resultado.stdout)


solo_con_node = pytest.mark.skipif(NODE is None, reason="Node.js no está instalado")


@solo_con_node
def test_hash_mal_formado_no_rompe_la_calculadora():
    resultado = ejecutar_app(["decodificar"], [("decodificar", ["1%E0%A4%A"]), ("decodificar", ["%"]),
                                               ("decodificar", ["1.000.000"]), ("decodificar", ["l%C3%ADquido"])])
    assert resultado == [None, None, "1.000.000", "líquido"]
    # Todo decodeURIComponent pasa por decodificar (protegido con try/catch)
    assert APP_JS.count("decodeURIComponent(") == 1
    cargar = funcion_de_app("cargarDesdeEnlace")
    assert "decodificar(kv[0]" in cargar and "decodificar(kv[1]" in cargar and "=== null" in cargar


@solo_con_node
def test_formato_de_app_igual_que_python():
    """Lo que escribe app.js en el resultado coincide con el valor inicial que pone Python."""
    valores = [0, 0.5, 1.005, 2.675, 999.995, 12_345.678, 1_609_565.4999, -152_500, -0.004, 17_065_211.27]
    casos = [("numero", [v, d]) for v in valores for d in (0, 1, 2)]
    casos += [("pesos", [v]) for v in valores] + [("porcentaje", [v / 1e6, 2, True]) for v in valores]
    casos += [("textoTiempo", [{"anios": a, "meses": m, "dias": d}]) for a, m, d in ((0, 8, 0), (1, 1, 1), (3, 7, 12))]
    esperado = [numero(v, d) for v in valores for d in (0, 1, 2)]
    esperado += [pesos(v) for v in valores] + [porcentaje(v / 1e6, 2, True) for v in valores]
    esperado += [texto_tiempo(a, m, d) for a, m, d in ((0, 8, 0), (1, 1, 1), (3, 7, 12))]
    assert ejecutar_app(["redondear", "numero", "pesos", "porcentaje", "textoTiempo"], casos) == esperado


@solo_con_node
def test_grafico_de_ahorro_igual_en_python_y_javascript():
    serie = calculos.proyectar_ahorro(1_000_000, 100_000, 0.05, 10)["serie"]
    js = ejecutar_app(["graficoAhorro"], [("graficoAhorro", [serie])])[0]
    assert str(grafico_ahorro(serie)) == js


def test_app_js_marca_tablas_desplazables_y_anuncia_con_espera():
    marcar = funcion_de_app("marcarTablasDesplazables")
    for atributo in ("'tabindex', '0'", "'role', 'region'", "'aria-label', tituloCercano(caja)"):
        assert atributo in marcar
    calculadora = funcion_de_app("calculadora")
    assert "[data-r-anuncio]" in calculadora and "700" in calculadora and "clearTimeout(espera)" in calculadora
    assert "aria-live" not in APP_JS  # la región la declara la plantilla
    # ES5, como el resto de app.js
    assert not re.search(r"=>|`|\b(let|const)\s|\.\.\.", APP_JS)
