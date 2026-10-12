"""Construye el sitio completo con los datos de demostración y lo revisa como lo haría un buscador."""

from __future__ import annotations

import copy
import datetime as dt
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from lucas.config import cargar_config
from lucas.construir import ErrorConstruccion, construir

from .conftest import DEMO, HOY


class Analizador(HTMLParser):
    def __init__(self):
        super().__init__()
        self.enlaces: list[str] = []
        self.titulo = ""
        self.descripcion = None
        self.canonica = None
        self.robots = None
        self.h1 = 0
        self.jsonld: list[str] = []
        self._en_titulo = False
        self._en_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for clave in ("href", "src"):
            if a.get(clave):
                self.enlaces.append(a[clave])
        if tag == "title" and not self.titulo:  # solo el <title> del <head>, no los de los SVG
            self._en_titulo = True
        elif tag == "meta" and a.get("name") == "description":
            self.descripcion = a.get("content")
        elif tag == "meta" and a.get("name") == "robots":
            self.robots = a.get("content")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonica = a.get("href")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._en_jsonld = True
            self.jsonld.append("")

    def handle_endtag(self, tag):
        if tag == "title":
            self._en_titulo = False
        if tag == "script":
            self._en_jsonld = False

    def handle_data(self, data):
        if self._en_titulo:
            self.titulo += data
        if self._en_jsonld:
            self.jsonld[-1] += data


@pytest.fixture(scope="module")
def sitio(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio")
    resumen = construir(salida=salida, demo=True, hoy=HOY)
    paginas = {}
    for archivo in salida.rglob("*.html"):
        analizador = Analizador()
        analizador.feed(archivo.read_text(encoding="utf-8"))
        paginas["/" + str(archivo.relative_to(salida)).replace("\\", "/")] = analizador
    return salida, resumen, paginas


def test_genera_las_paginas_clave(sitio):
    salida, resumen, _ = sitio
    assert resumen["paginas"] > 200
    for ruta in ("index.html", "uf/index.html", "uf/proyeccion/index.html", "uf/2026/octubre/index.html",
                 "uf/2026/noviembre/index.html", "uf/1000-uf-en-pesos/index.html", "dolar/index.html",
                 "dolar/100-dolares-en-pesos/index.html", "utm/index.html", "utm/2026/index.html",
                 "ipc/index.html", "impuesto-unico/index.html", "sueldo-minimo/index.html",
                 "sueldo-liquido/1000000/index.html", "calculadoras/sueldo-liquido/index.html",
                 "calculadoras/boleta-honorarios/index.html", "calculadoras/reajuste-arriendo-ipc/index.html",
                 "calculadoras/credito-hipotecario/index.html", "calculadoras/interes-compuesto/index.html",
                 "calculadoras/dias-habiles/index.html", "feriados/index.html", "feriados/2027/index.html",
                 "privacidad/index.html", "404.html", "sitemap.xml", "robots.txt", "_headers", "favicon.ico"):
        assert (salida / ruta).exists(), ruta


def test_sin_enlaces_internos_rotos(sitio):
    salida, _, paginas = sitio
    rotos = []
    for origen, pagina in paginas.items():
        for enlace in pagina.enlaces:
            if enlace.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            ruta = enlace.split("?")[0].split("#")[0]
            destino = salida / ruta.lstrip("/")
            if ruta.endswith("/"):
                destino = destino / "index.html"
            if not destino.exists():
                rotos.append(f"{origen} -> {enlace}")
    assert rotos == []


def test_seo_basico_en_cada_pagina(sitio):
    _, _, paginas = sitio
    titulos: dict[str, str] = {}
    for ruta, pagina in paginas.items():
        assert pagina.titulo.strip(), ruta
        assert len(pagina.titulo) <= 90, (ruta, pagina.titulo)
        assert pagina.descripcion and 50 <= len(pagina.descripcion) <= 230, (ruta, pagina.descripcion)
        assert pagina.canonica and pagina.canonica.startswith("https://"), ruta
        assert pagina.h1 == 1, ruta
        for bloque in pagina.jsonld:
            json.loads(bloque)
        assert pagina.titulo not in titulos, f"título repetido en {ruta} y {titulos.get(pagina.titulo)}"
        titulos[pagina.titulo] = ruta


def test_demo_no_se_indexa(sitio):
    salida, _, paginas = sitio
    assert all(p.robots == "noindex" for p in paginas.values())
    assert "ficticios" in (salida / "index.html").read_text(encoding="utf-8")


def test_sitemap_y_robots(sitio):
    salida, resumen, _ = sitio
    sitemap = (salida / "sitemap.xml").read_text(encoding="utf-8")
    urls = re.findall(r"<loc>(.*?)</loc>", sitemap)
    # todas menos la 404 y /feriados/<año en curso>/, cuya canónica es /feriados/
    assert len(urls) == resumen["paginas"] - 2
    assert "https://lucasclaras.cl/uf/" in urls
    assert "404" not in sitemap
    assert "Sitemap: https://lucasclaras.cl/sitemap.xml" in (salida / "robots.txt").read_text()


def test_valores_en_paginas(sitio):
    salida, _, _ = sitio
    honorarios = (salida / "calculadoras/boleta-honorarios/index.html").read_text(encoding="utf-8")
    assert "15,25%" in honorarios
    feriados = (salida / "feriados/index.html").read_text(encoding="utf-8")
    assert "Encuentro de Dos Mundos" in feriados
    # $1.000.000 bruto no alcanza el tope imponible ni paga impuesto: el líquido no depende de la UF
    sueldo = (salida / "sueldo-liquido/1000000/index.html").read_text(encoding="utf-8")
    assert "$819.400" in sueldo


def test_sitio_en_subcarpeta(tmp_path):
    """GitHub Pages sin dominio propio publica en usuario.github.io/repositorio."""
    cfg = cargar_config()
    cfg = copy.deepcopy(cfg)
    cfg["sitio"]["url"] = "https://usuario.github.io/lucas-claras"
    cfg["sitio"]["ruta_base"] = "/lucas-claras"
    construir(salida=tmp_path, demo=True, hoy=HOY, cfg=cfg)
    html = (tmp_path / "uf" / "index.html").read_text(encoding="utf-8")
    internos = re.findall(r'(?:href|src)="(/[^"]*)"', html)
    assert internos and all(e.startswith("/lucas-claras/") for e in internos)
    assert '<link rel="canonical" href="https://usuario.github.io/lucas-claras/uf/">' in html


def test_ads_txt_y_anuncios(tmp_path):
    cfg = copy.deepcopy(cargar_config())
    cfg["monetizacion"]["adsense"].update(activo=True, publisher_id="ca-pub-1234567890123456",
                                          slots={"uf_superior": "111"})
    construir(salida=tmp_path, demo=True, hoy=HOY, cfg=cfg)
    assert (tmp_path / "ads.txt").read_text() == "google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0\n"
    # En modo demo nunca se cargan anuncios
    assert "adsbygoogle.js" not in (tmp_path / "uf" / "index.html").read_text(encoding="utf-8")


def test_no_publica_datos_demo_como_reales(tmp_path):
    with pytest.raises(ErrorConstruccion):
        construir(salida=tmp_path, demo=False, hoy=HOY, directorio_datos=DEMO)


def test_falla_si_faltan_datos(tmp_path):
    vacio = tmp_path / "vacio"
    (vacio / "series").mkdir(parents=True)
    with pytest.raises(ErrorConstruccion):
        construir(salida=tmp_path / "dist", demo=False, hoy=HOY, directorio_datos=vacio)


def test_sitio_sin_euro(tmp_path):
    """Si no hay datos del euro (el SII no lo publica), sus páginas se omiten sin dejar enlaces rotos."""
    import shutil
    datos = tmp_path / "datos"
    shutil.copytree(DEMO, datos)
    (datos / "series" / "euro.json").unlink()
    salida = tmp_path / "sitio"
    resumen = construir(salida=salida, demo=True, hoy=HOY, directorio_datos=datos)
    assert not (salida / "euro").exists()
    assert any("euro" in a for a in resumen["advertencias"])
    for archivo in salida.rglob("*.html"):
        assert 'href="/euro/' not in archivo.read_text(encoding="utf-8"), archivo
