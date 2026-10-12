"""App instalable (PWA): manifiesto, íconos, service worker y páginas de instalación."""

from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess

import pytest
from PIL import Image

from lucas.app_instalable import manifiesto, service_worker
from lucas.config import cargar_config
from lucas.construir import construir

from .conftest import HOY, RAIZ


@pytest.fixture(scope="module")
def sitio(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio_app")
    construir(salida=salida, demo=True, hoy=HOY)
    return salida


def test_manifiesto_instalable(sitio):
    datos = json.loads((sitio / "manifest.webmanifest").read_text(encoding="utf-8"))
    nombre = cargar_config()["sitio"]["nombre"]
    assert datos["short_name"] == nombre and nombre in datos["name"]
    assert datos["start_url"] == datos["scope"] == datos["id"] == "/"
    assert datos["display"] == "standalone"
    assert datos["lang"] == "es-CL"
    tamanos = {(i["sizes"], i.get("purpose", "any")) for i in datos["icons"]}
    assert {("192x192", "any"), ("512x512", "any"), ("512x512", "maskable")} <= tamanos
    for icono in datos["icons"]:
        archivo = sitio / icono["src"].lstrip("/")
        ancho = int(icono["sizes"].split("x")[0])
        assert Image.open(archivo).size == (ancho, ancho), icono["src"]
    for acceso in datos["shortcuts"]:
        destino = sitio / acceso["url"].lstrip("/") / "index.html"
        assert destino.exists(), acceso["url"]


def test_service_worker_y_cabeceras(sitio):
    sw = (sitio / "sw.js").read_text(encoding="utf-8")
    assert "var BASE = '';" in sw
    precarga = json.loads(re.search(r"var PRECARGA = (\[.*?\]);", sw).group(1))
    for ruta in precarga:
        assert (sitio / ruta.lstrip("/") / "index.html").exists(), ruta
    cabeceras = (sitio / "_headers").read_text(encoding="utf-8")
    assert "/sw.js\n  Cache-Control: no-cache\n" in cabeceras
    node = shutil.which("node")
    if node:  # el service worker debe ser JavaScript válido
        subprocess.run([node, "--check", str(sitio / "sw.js")], check=True, capture_output=True)


def test_paginas_enlazan_el_manifiesto(sitio):
    html = (sitio / "index.html").read_text(encoding="utf-8")
    assert '<link rel="manifest" href="/manifest.webmanifest">' in html
    assert '<html lang="es-CL" data-base="">' in html
    assert 'href="/app/"' in html  # enlace en el pie
    assert '<div class="aviso-sin-conexion" data-sin-conexion role="status" hidden>' in html
    app = (sitio / "app" / "index.html").read_text(encoding="utf-8")
    assert "data-instalar" in app and "Agregar a inicio" in app
    sitemap = (sitio / "sitemap.xml").read_text(encoding="utf-8")
    assert "/app/</loc>" in sitemap and "sin-conexion" not in sitemap
    sin_conexion = (sitio / "sin-conexion" / "index.html").read_text(encoding="utf-8")
    assert '<meta name="robots" content="noindex">' in sin_conexion
    assert 'rel="canonical"' not in sin_conexion
    assert "data-sin-conexion" not in sin_conexion  # la página ya lo dice


def test_app_en_subcarpeta():
    """En GitHub Pages sin dominio, el sitio vive en /repositorio/: la app también."""
    cfg = copy.deepcopy(cargar_config())
    cfg["sitio"]["ruta_base"] = "/saca-la-cuenta"
    datos = manifiesto(cfg)
    assert datos["start_url"] == datos["scope"] == "/saca-la-cuenta/"
    assert all(i["src"].startswith("/saca-la-cuenta/estaticos/img/") for i in datos["icons"])
    sw = service_worker(cfg, "1")
    assert "var BASE = '/saca-la-cuenta';" in sw
    assert '"/saca-la-cuenta/sin-conexion/"' in sw


def test_iconos_del_repositorio():
    for nombre, tamano in (("icono-192.png", 192), ("icono-512.png", 512), ("icono-maskable-512.png", 512),
                           ("apple-touch-icon.png", 180)):
        assert Image.open(RAIZ / "estaticos" / "img" / nombre).size == (tamano, tamano), nombre
