"""API abierta (JSON estáticos en /api/v1/), widget para otros sitios (/widget.js) y sus
páginas /widget/ y /api/, construidos con los datos de demostración."""

from __future__ import annotations

import copy
import dataclasses
import datetime as dt
import html
import json
import re
import shutil
import subprocess

import pytest

from lucas.api import VERSION, codigo_widget, escribir_api
from lucas.config import cargar_config, cargar_parametros
from lucas.construir import construir, crear_contexto
from lucas.datos import cargar_datos
from lucas.feriados import feriados_nacionales, feriados_regionales

from .conftest import DEMO, HOY, RAIZ

NODE = shutil.which("node")
API = f"api/{VERSION}"
ANIOS = (HOY.year - 1, HOY.year, HOY.year + 1)
ARCHIVOS = ([f"{API}/indicadores.json", f"{API}/uf.json", f"{API}/dolar.json"]
            + [f"{API}/feriados/{anio}.json" for anio in ANIOS])


@pytest.fixture(scope="module")
def sitio(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio_api")
    construir(salida=salida, demo=True, hoy=HOY)
    return salida


def leer_json(salida, ruta):
    return json.loads((salida / ruta).read_text(encoding="utf-8"))


def serie_demo(nombre: str) -> dict[dt.date, float]:
    crudo = json.loads((DEMO / "series" / f"{nombre}.json").read_text(encoding="utf-8"))
    return {dt.date.fromisoformat(fecha): valor for fecha, valor in crudo.items()}


def codigo_de_la_pagina(salida) -> str:
    pagina = (salida / "widget" / "index.html").read_text(encoding="utf-8")
    return html.unescape(re.search(r'<textarea id="codigo-widget"[^>]*>(.*?)</textarea>', pagina, re.S).group(1))


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def test_json_existen_compactos_y_en_utf8(sitio):
    for ruta in ARCHIVOS:
        texto = (sitio / ruta).read_text(encoding="utf-8")
        datos = json.loads(texto)
        assert texto == json.dumps(datos, ensure_ascii=False, separators=(",", ":")), ruta
        assert datos["version"] == VERSION
        assert dt.datetime.fromisoformat(datos["actualizado"]).tzinfo is not None
        assert datos["documentacion"] == "https://lucasclaras.cl/api/"
        assert datos["atribucion"] == {"texto": "Lucas Claras", "enlace": "https://lucasclaras.cl/"}
        assert "https://lucasclaras.cl/" in datos["condiciones"] and "nofollow" in datos["condiciones"]
        assert datos["fuente"]
    assert '"nombre":"Dólar observado"' in (sitio / f"{API}/dolar.json").read_text(encoding="utf-8")
    assert not (sitio / f"{API}/feriados/{HOY.year + 2}.json").exists()


def test_indicadores_coinciden_con_los_datos_demo(sitio, datos_demo):
    d = leer_json(sitio, f"{API}/indicadores.json")
    manana = HOY + dt.timedelta(days=1)
    assert d["actualizado"] == "2026-10-12T07:00:00-03:00"  # meta.json de la demo
    assert d["uf"] == {"fecha": "2026-10-12", "valor": serie_demo("uf")[HOY],
                       "manana": {"fecha": "2026-10-13", "valor": datos_demo.uf_dia(manana)}}
    # El último dólar y euro publicados son del viernes 9 (el 12 de octubre es feriado).
    assert d["dolar"] == {"fecha": "2026-10-09", "valor": serie_demo("dolar")[dt.date(2026, 10, 9)]}
    assert d["euro"] == {"fecha": "2026-10-09", "valor": serie_demo("euro")[dt.date(2026, 10, 9)]}
    assert d["utm"] == {"mes": "2026-10", "valor": serie_demo("utm")[dt.date(2026, 10, 1)]}
    assert isinstance(d["utm"]["valor"], int)
    assert d["ipc"] == {"mes": "2026-09", "variacion_porcentual": serie_demo("ipc")[dt.date(2026, 9, 1)]}
    assert isinstance(d["uf"]["valor"], float) and isinstance(d["dolar"]["valor"], float)
    assert "Banco Central de Chile" in d["fuente"]


def test_uf_diaria_desde_30_dias_atras_hasta_la_ultima_conocida(sitio, datos_demo):
    d = leer_json(sitio, f"{API}/uf.json")
    fechas = [dt.date.fromisoformat(p["fecha"]) for p in d["serie"]]
    completa = datos_demo.uf_completa()
    assert fechas[0] == HOY - dt.timedelta(days=30)
    assert fechas[-1] == max(completa) == dt.date(2026, 11, 9)  # se conoce hasta el día 9 del mes siguiente
    assert fechas == [fechas[0] + dt.timedelta(days=i) for i in range(len(fechas))]
    assert [p["valor"] for p in d["serie"]] == [completa[f] for f in fechas]
    assert (d["desde"], d["hasta"]) == (fechas[0].isoformat(), fechas[-1].isoformat())
    assert d["calculada_desde"] == min(datos_demo.uf_calculada).isoformat() == "2026-10-13"


def test_dolar_ultimos_30_valores(sitio):
    d = leer_json(sitio, f"{API}/dolar.json")
    esperado = [(f, v) for f, v in sorted(serie_demo("dolar").items()) if f <= HOY][-30:]
    assert [(p["fecha"], p["valor"]) for p in d["serie"]] == [(f.isoformat(), v) for f, v in esperado]
    assert len(d["serie"]) == 30 and d["serie"][-1]["fecha"] == "2026-10-09"


def test_feriados_del_anio_anterior_actual_y_siguiente(sitio, params):
    for anio in ANIOS:
        d = leer_json(sitio, f"{API}/feriados/{anio}.json")
        assert d["anio"] == anio
        # Todos los atributos de cada feriado, tal como los calcula lucas/feriados.py.
        esperados = feriados_nacionales(anio, params.feriados_extra())
        assert d["feriados"] == [{**dataclasses.asdict(f), "fecha": f.fecha.isoformat()} for f in esperados]
        assert [f["nombre"] for f in d["regionales"]] == [f.nombre for f in feriados_regionales(anio)]
    feriados_2026 = leer_json(sitio, f"{API}/feriados/2026.json")["feriados"]
    assert {"fecha": "2026-10-12", "nombre": "Encuentro de Dos Mundos", "tipo": "Civil",
            "irrenunciable": False, "nota": "", "regional": ""} in feriados_2026
    # Los feriados especiales de parametros/chile.yaml también se incluyen (elecciones de 2025).
    assert "2025-11-16" in [f["fecha"] for f in leer_json(sitio, f"{API}/feriados/2025.json")["feriados"]]


def test_escribir_api_devuelve_las_rutas_que_escribe(tmp_path):
    params = cargar_parametros()
    datos = cargar_datos(DEMO, params.get("utm_se_mantiene_con_ipc_negativo", True))
    del datos.meta["actualizado"]  # sin la hora de descarga se usa la de la construcción, en hora de Chile
    c = crear_contexto(cargar_config(), params, datos, HOY, dt.datetime(2026, 10, 12, 7, 0))
    rutas = escribir_api(tmp_path, c)
    assert sorted(rutas) == sorted(ARCHIVOS + ["widget.js"])
    assert all((tmp_path / ruta).is_file() for ruta in rutas)
    assert leer_json(tmp_path, f"{API}/indicadores.json")["actualizado"] == "2026-10-12T07:00:00-03:00"


# ---------------------------------------------------------------------------
# Cabeceras de Cloudflare
# ---------------------------------------------------------------------------

def reglas_headers(texto: str) -> list[tuple[str, dict]]:
    reglas: list[tuple[str, dict]] = []
    for linea in texto.splitlines():
        if linea.strip() and not linea.startswith(" "):
            reglas.append((linea.strip(), {}))
        elif linea.strip():
            nombre, valor = linea.split(":", 1)
            reglas[-1][1][nombre.strip()] = valor.strip()
    return reglas


def aplicadas(reglas, ruta: str) -> dict[str, list[str]]:
    """Cabeceras que recibe ``ruta``: Cloudflare aplica todas las reglas que calzan (``*`` = cualquier texto)."""
    resultado: dict[str, list[str]] = {}
    for patron, cabeceras in reglas:
        if re.fullmatch(re.escape(patron).replace(r"\*", ".*"), ruta):
            for nombre, valor in cabeceras.items():
                resultado.setdefault(nombre, []).append(valor)
    return resultado


def test_cabeceras_de_la_api_y_del_widget(sitio):
    reglas = reglas_headers((sitio / "_headers").read_text(encoding="utf-8"))
    por_patron = dict(reglas)
    # Las reglas anteriores se mantienen.
    assert por_patron["/*"] == {"X-Content-Type-Options": "nosniff",
                                "Referrer-Policy": "strict-origin-when-cross-origin",
                                "X-Frame-Options": "SAMEORIGIN"}
    assert por_patron["/estaticos/*"] == {"Cache-Control": "public, max-age=31536000, immutable"}
    assert por_patron["/api/*"] == {"Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=1800"}
    assert por_patron["/widget.js"] == {"Cache-Control": "public, max-age=3600"}
    # Cloudflare uniría dos Cache-Control con una coma: cada ruta debe recibir uno solo.
    for ruta, cache in (("/api/v1/indicadores.json", "public, max-age=1800"),
                        ("/api/v1/feriados/2027.json", "public, max-age=1800"),
                        ("/widget.js", "public, max-age=3600"),
                        ("/estaticos/js/widget-generador.js", "public, max-age=31536000, immutable"),
                        ("/widget/", None)):
        assert aplicadas(reglas, ruta).get("Cache-Control") == ([cache] if cache else None), ruta
    assert aplicadas(reglas, "/api/v1/uf.json")["Access-Control-Allow-Origin"] == ["*"]
    assert "Access-Control-Allow-Origin" not in aplicadas(reglas, "/uf/")


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

def sin_comentarios(codigo: str) -> str:
    return re.sub(r"/\*.*?\*/|(?<![:\\])//[^\n]*", "", codigo, flags=re.S)


def test_widget_en_la_raiz_pequeno_y_es5(sitio):
    widget = sitio / "widget.js"
    assert widget.read_bytes() == (RAIZ / "widget" / "widget.js").read_bytes()
    # Nunca bajo /estaticos/: esa carpeta se guarda en caché por un año.
    assert not list((sitio / "estaticos").rglob("widget.js"))
    contenido = widget.read_bytes()
    assert len(contenido) < 6 * 1024
    texto = contenido.decode("ascii")  # solo ASCII: funciona aunque la página que lo inserta no use UTF-8
    for necesario in ("document.currentScript", "api/v1/indicadores.json", "attachShadow", "createElement('slot')",
                      "prefers-color-scheme", "data-indicadores", "data-tema"):
        assert necesario in texto, necesario
    generador = (sitio / "estaticos" / "js" / "widget-generador.js").read_text(encoding="utf-8")
    for nombre, codigo in (("widget.js", texto), ("widget-generador.js", generador)):
        codigo = sin_comentarios(codigo)
        assert not re.search(r"=>|`|\b(let|const)\s|\.\.\.|\bclass\s+[A-Z]", codigo), f"{nombre} debe ser ES5"


@pytest.mark.skipif(NODE is None, reason="Node.js no está instalado")
def test_widget_y_generador_tienen_sintaxis_valida(sitio):
    for archivo in (sitio / "widget.js", sitio / "estaticos" / "js" / "widget-generador.js"):
        subprocess.run([NODE, "--check", str(archivo)], check=True, capture_output=True, timeout=60)


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

def test_paginas_widget_y_api(sitio):
    widget = (sitio / "widget" / "index.html").read_text(encoding="utf-8")
    api = (sitio / "api" / "index.html").read_text(encoding="utf-8")
    assert "<title>Widget gratis de UF, dólar y UTM para tu sitio web</title>" in widget
    assert "<title>API gratuita de indicadores económicos de Chile (JSON)</title>" in api
    # Código para copiar: enlace de atribución visible, con la marca y rel="nofollow".
    codigo = codigo_de_la_pagina(sitio)
    assert codigo == codigo_widget(cargar_config())
    assert codigo == ('<div class="lucas-claras-widget" data-indicadores="uf,dolar,utm" data-tema="auto">'
                      '<a href="https://lucasclaras.cl/" rel="nofollow">Indicadores de Lucas Claras</a></div>\n'
                      '<script async src="https://lucasclaras.cl/widget.js"></script>')
    assert '<script async src="/widget.js"></script>' in widget  # vista previa en vivo
    assert re.search(r'src="/estaticos/js/widget-generador\.js\?v=\w+"', widget)
    assert 'value="euro"' in widget  # la demo tiene euro
    for ruta in ARCHIVOS:
        assert f'href="/{ruta}"' in api, ruta
    for texto in ("fetch(", "curl -s", "urlopen(", "Access-Control-Allow-Origin", "max-age=1800",
                  'id="condiciones"'):
        assert texto in api, texto
    assert '"@type":"Dataset"' in api
    inicio = (sitio / "index.html").read_text(encoding="utf-8")
    assert '<a href="/widget/">Widget para tu sitio</a>' in inicio
    assert '<a href="/api/">API de indicadores</a>' in inicio


def test_sitio_en_subcarpeta_usa_su_url(tmp_path):
    cfg = copy.deepcopy(cargar_config())
    cfg["sitio"]["url"] = "https://usuario.github.io/lucas-claras"
    cfg["sitio"]["ruta_base"] = "/lucas-claras"
    construir(salida=tmp_path, demo=True, hoy=HOY, cfg=cfg)
    d = leer_json(tmp_path, f"{API}/indicadores.json")
    assert d["documentacion"] == "https://usuario.github.io/lucas-claras/api/"
    assert d["atribucion"]["enlace"] == "https://usuario.github.io/lucas-claras/"
    codigo = codigo_de_la_pagina(tmp_path)
    assert codigo == codigo_widget(cfg)
    assert '<script async src="https://usuario.github.io/lucas-claras/widget.js"></script>' in codigo
    assert 'src="/lucas-claras/widget.js"' in (tmp_path / "widget" / "index.html").read_text(encoding="utf-8")


def test_sin_euro(tmp_path):
    datos = tmp_path / "datos"
    shutil.copytree(DEMO, datos)
    (datos / "series" / "euro.json").unlink()
    salida = tmp_path / "sitio"
    construir(salida=salida, demo=True, hoy=HOY, directorio_datos=datos)
    assert leer_json(salida, f"{API}/indicadores.json")["euro"] is None
    assert 'value="euro"' not in (salida / "widget" / "index.html").read_text(encoding="utf-8")
