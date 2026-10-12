"""Páginas de datos pensadas para buscadores: feriados con direcciones permanentes y su
calendario .ics, tildes y concordancia, menos páginas por monto y con contenido propio,
páginas por año de la UF y del dólar, sitemap con fechas de modificación reales, euro
desactualizado y anuncios debajo de la tabla principal."""

from __future__ import annotations

import copy
import dataclasses
import datetime as dt
import itertools
import json
import re
import shutil
import statistics
from collections import deque
from html.parser import HTMLParser
from pathlib import Path

import pytest

from lucas import calendario, paginas
from lucas.config import cargar_config
from lucas.construir import Pagina, construir, crear_contexto, crear_entorno
from lucas.datos import cargar_datos
from lucas.feriados import (PRIMER_ANIO_FERIADOS, anios_con_pagina, feriados_nacionales,
                            proximo_fin_de_semana_largo)
from lucas.formato import fecha_larga, pesos
from lucas.seo import sitemap_xml

from .conftest import DEMO, HOY

URL = "https://lucasclaras.cl"
DOLAR_DEMO = dt.date(2026, 10, 9)  # último dólar y euro de la demo (el 12 de octubre es feriado)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

class Lector(HTMLParser):
    """Lee una página como un buscador: título, descripción, canónica, JSON-LD, enlaces y texto."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titulo = ""
        self.descripcion = ""
        self.canonica = ""
        self.enlaces: list[str] = []
        self.jsonld: list[str] = []
        self.texto: list[str] = []       # texto visible del <body>
        self.principal: list[str] = []   # texto del <main>, sin migas ni paginadores (<nav>)
        self._ocultos = 0
        self._en_body = self._en_main = self._en_titulo = self._en_jsonld = False
        self._navs = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.enlaces.append(a["href"])
        elif tag == "title" and not self.titulo:  # el <title> del <head>, no los de los SVG
            self._en_titulo = True
        elif tag == "meta" and a.get("name") == "description":
            self.descripcion = a.get("content") or ""
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonica = a.get("href") or ""
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._en_jsonld = True
            self.jsonld.append("")
        if tag in ("script", "style", "svg"):
            self._ocultos += 1
        self._en_body = self._en_body or tag == "body"
        self._en_main = self._en_main or tag == "main"
        self._navs += tag == "nav"

    def handle_endtag(self, tag):
        if tag == "title":
            self._en_titulo = False
        if tag == "script":
            self._en_jsonld = False
        if tag in ("script", "style", "svg"):
            self._ocultos -= 1
        if tag == "main":
            self._en_main = False
        self._navs -= tag == "nav"

    def handle_data(self, data):
        if self._en_titulo:
            self.titulo += data
        if self._en_jsonld:
            self.jsonld[-1] += data
        if self._en_body and not self._ocultos:
            self.texto.append(data)
            if self._en_main and not self._navs:
                self.principal.append(data)

    @property
    def visible(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.texto))

    @property
    def bloques(self) -> list[dict]:
        return [json.loads(b) for b in self.jsonld]

    def migas(self) -> list[tuple[str, str]]:
        lista = next(b for b in self.bloques if b["@type"] == "BreadcrumbList")
        return [(e["name"], e["item"]) for e in lista["itemListElement"]]


def archivo_de(salida: Path, ruta: str) -> Path:
    return salida / ruta.lstrip("/") / "index.html" if ruta.endswith("/") else salida / ruta.lstrip("/")


def leer(salida: Path, ruta: str) -> Lector:
    lector = Lector()
    lector.feed(archivo_de(salida, ruta).read_text(encoding="utf-8"))
    return lector


def html(salida: Path, ruta: str) -> str:
    return archivo_de(salida, ruta).read_text(encoding="utf-8")


def lastmods(salida: Path) -> dict[str, str]:
    sitemap = (salida / "sitemap.xml").read_text(encoding="utf-8")
    return {loc.removeprefix(URL): fecha
            for loc, fecha in re.findall(r"<loc>(.*?)</loc><lastmod>(.*?)</lastmod>", sitemap)}


def tejas(texto: str, n: int = 5) -> set[tuple[str, ...]]:
    """5-gramas de palabras con los números reemplazados por "#"."""
    palabras = [("#" if re.search(r"\d", p) else p.strip(".,"))
                for p in re.findall(r"[\wáéíóúüñ$%.,+-]+", texto.lower())]
    palabras = [p for p in palabras if p]
    return {tuple(palabras[i:i + n]) for i in range(len(palabras) - n + 1)}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b)


def similitud_promedio(salida: Path, rutas: list[str]) -> float:
    conjuntos = [tejas(" ".join(leer(salida, r).principal)) for r in rutas]
    return statistics.mean(jaccard(a, b) for a, b in itertools.combinations(conjuntos, 2))


def revisar_seo_basico(salida: Path) -> None:
    """Las reglas de tests/test_construir.py en un sitio construido con otros datos."""
    titulos = set()
    for archivo in salida.rglob("*.html"):
        texto = archivo.read_text(encoding="utf-8")
        pagina = Lector()
        pagina.feed(texto)
        assert pagina.titulo and len(pagina.titulo) <= 90, (archivo, pagina.titulo)
        assert 50 <= len(pagina.descripcion) <= 230, (archivo, pagina.descripcion)
        assert len(re.findall(r"<h1[ >]", texto)) == 1, archivo
        assert pagina.titulo not in titulos, archivo
        titulos.add(pagina.titulo)


def profundidades(salida: Path) -> dict[str, int]:
    """Clics desde la portada hasta cada página, siguiendo los enlaces internos."""
    distancia = {"/": 0}
    cola = deque(["/"])
    while cola:
        ruta = cola.popleft()
        for enlace in leer(salida, ruta).enlaces:
            destino = enlace.split("#")[0].split("?")[0]
            if destino.startswith("/") and destino.endswith("/") and destino not in distancia:
                if archivo_de(salida, destino).exists():
                    distancia[destino] = distancia[ruta] + 1
                    cola.append(destino)
    return distancia


@pytest.fixture(scope="module")
def sitio(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio_seo")
    resumen = construir(salida=salida, demo=True, hoy=HOY)
    return salida, resumen


@pytest.fixture(scope="module")
def contexto(params):
    datos = cargar_datos(DEMO, params.get("utm_se_mantiene_con_ipc_negativo", True))
    return crear_contexto(cargar_config(), params, datos, HOY, dt.datetime(2026, 10, 12, 7, 0))


def serie_demo(nombre: str) -> dict[dt.date, float]:
    crudo = json.loads((DEMO / "series" / f"{nombre}.json").read_text(encoding="utf-8"))
    return {dt.date.fromisoformat(f): v for f, v in crudo.items()}


# ---------------------------------------------------------------------------
# 1. Feriados con direcciones permanentes
# ---------------------------------------------------------------------------

def test_feriados_una_pagina_por_anio_desde_2025(sitio):
    salida, _ = sitio
    assert PRIMER_ANIO_FERIADOS == 2025
    assert anios_con_pagina(HOY) == [2025, 2026, 2027]
    for anio in (2025, 2026, 2027):
        assert archivo_de(salida, f"/feriados/{anio}/").exists(), anio
    assert not archivo_de(salida, "/feriados/2024/").exists()
    assert not archivo_de(salida, "/feriados/2028/").exists()
    assert leer(salida, "/feriados/").titulo.startswith("Feriados 2026 en Chile")


def test_feriados_del_anio_en_curso_con_canonica_a_la_principal(sitio):
    salida, _ = sitio
    assert leer(salida, "/feriados/2026/").canonica == f"{URL}/feriados/"
    for ruta in ("/feriados/", "/feriados/2025/", "/feriados/2027/"):
        assert leer(salida, ruta).canonica == URL + ruta
    fechas = lastmods(salida)
    assert {"/feriados/", "/feriados/2025/", "/feriados/2027/"} <= set(fechas)
    assert "/feriados/2026/" not in fechas
    # Los enlaces internos van a la canónica: nadie enlaza la copia del año en curso.
    for ruta in ("/", "/feriados/", "/feriados/2025/", "/feriados/2027/", "/calculadoras/dias-habiles/"):
        assert "/feriados/2026/" not in leer(salida, ruta).enlaces, ruta


def test_preguntas_frecuentes_solo_en_la_principal(sitio):
    salida, _ = sitio
    tipos = {ruta: [b["@type"] for b in leer(salida, ruta).bloques]
             for ruta in ("/feriados/", "/feriados/2025/", "/feriados/2026/", "/feriados/2027/")}
    assert "FAQPage" in tipos["/feriados/"]
    assert all("FAQPage" not in t for r, t in tipos.items() if r != "/feriados/")
    assert "Preguntas frecuentes" not in leer(salida, "/feriados/2027/").visible


def test_enlaces_entre_anios(sitio):
    salida, _ = sitio
    esperados = {
        "/feriados/": {"/feriados/2025/", "/feriados/2027/"},
        "/feriados/2025/": {"/feriados/", "/feriados/2027/"},
        "/feriados/2026/": {"/feriados/", "/feriados/2025/", "/feriados/2027/"},
        "/feriados/2027/": {"/feriados/", "/feriados/2025/"},
    }
    for ruta, destinos in esperados.items():
        assert destinos <= set(leer(salida, ruta).enlaces), ruta


def test_proximo_fin_de_semana_largo(sitio):
    salida, _ = sitio
    principal = leer(salida, "/feriados/").visible
    assert ("Próximo fin de semana largo: 3 días, del viernes 25 de diciembre al domingo 27 de "
            "diciembre (Navidad)") in principal
    assert "Próximo fin de semana largo" not in leer(salida, "/feriados/2027/").visible
    # Busca también en el año siguiente e incluye el que empieza hoy.
    assert proximo_fin_de_semana_largo(dt.date(2026, 12, 26))["inicio"] == dt.date(2027, 1, 1)
    assert proximo_fin_de_semana_largo(dt.date(2026, 12, 25))["inicio"] == dt.date(2026, 12, 25)


def test_al_cambiar_el_anio_no_se_pierde_ninguna_pagina(contexto):
    """El 1 de enero de 2027, /feriados/2027/ pasa a ser la copia de /feriados/ y /feriados/2026/
    queda como un año pasado más: ninguna dirección deja de existir."""
    enero = dataclasses.replace(contexto, hoy=dt.date(2027, 1, 5))
    lista = {p.ruta: p for p in paginas.paginas_feriados(enero)}
    assert list(lista) == ["/feriados/", "/feriados/2025/", "/feriados/2026/", "/feriados/2027/",
                           "/feriados/2028/"]
    assert lista["/feriados/2027/"].canonica == "/feriados/" and not lista["/feriados/2027/"].en_sitemap
    assert lista["/feriados/2026/"].canonica is None and lista["/feriados/2026/"].en_sitemap
    assert [r for r, p in lista.items() if p.faq] == ["/feriados/"]
    assert lista["/feriados/2026/"].modificada == dt.date(2027, 1, 1)   # fija desde que terminó
    assert lista["/feriados/2025/"].modificada == paginas.REVISION_FERIADOS
    assert lista["/feriados/2028/"].modificada == dt.date(2027, 1, 1)   # desde que se publicó
    # En octubre de 2026 las mismas fechas del año pasado no cambian de un día para otro.
    hoy = {p.ruta: p.modificada for p in paginas.paginas_feriados(contexto)}
    manana = {p.ruta: p.modificada
              for p in paginas.paginas_feriados(dataclasses.replace(contexto, hoy=HOY + dt.timedelta(days=1)))}
    assert hoy["/feriados/2025/"] == manana["/feriados/2025/"]
    assert hoy["/feriados/2027/"] == manana["/feriados/2027/"]
    assert (hoy["/feriados/"], manana["/feriados/"]) == (HOY, HOY + dt.timedelta(days=1))  # pasó el feriado


def lineas_ics(texto: str) -> list[str]:
    """Despliega las líneas plegadas (RFC 5545, 3.1)."""
    return texto.replace("\r\n ", "").split("\r\n")[:-1]


def test_calendario_ics_valido(sitio, params):
    salida, _ = sitio
    uids = set()
    for anio in anios_con_pagina(HOY):
        crudo = (salida / "feriados" / f"{anio}.ics").read_bytes()
        texto = crudo.decode("utf-8")
        assert texto.endswith("\r\n") and texto.count("\n") == texto.count("\r\n"), "solo CRLF"
        assert all(len(linea.encode("utf-8")) <= 75 for linea in texto.split("\r\n")), "líneas de 75 octetos"
        lineas = lineas_ics(texto)
        assert lineas[:2] == ["BEGIN:VCALENDAR", "VERSION:2.0"] and lineas[-1] == "END:VCALENDAR"
        assert any(linea.startswith("PRODID:") for linea in lineas)
        eventos = re.findall(r"BEGIN:VEVENT\r\n(.*?)END:VEVENT", "\r\n".join(lineas) + "\r\n", re.S)
        feriados = feriados_nacionales(anio, params.feriados_extra())
        assert len(eventos) == len(feriados)
        for evento, feriado in zip(eventos, feriados):
            campos = dict(linea.split(":", 1) for linea in evento.strip().split("\r\n"))
            assert re.fullmatch(r"\d{8}T\d{6}Z", campos["DTSTAMP"])
            assert campos["DTSTART;VALUE=DATE"] == f"{feriado.fecha:%Y%m%d}"
            assert campos["DTEND;VALUE=DATE"] == f"{feriado.fecha + dt.timedelta(days=1):%Y%m%d}"
            assert campos["SUMMARY"] == feriado.nombre.replace(",", "\\,")
            assert campos["UID"].endswith("@lucasclaras.cl") and campos["UID"] not in uids
            uids.add(campos["UID"])
    assert 'href="/feriados/2026.ics"' in html(salida, "/feriados/")
    assert "Agregar a mi calendario" in leer(salida, "/feriados/2025/").visible


def test_ics_escapa_pliega_y_usa_hora_utc():
    linea = "DESCRIPTION:" + "Día de las Iglesias Evangélicas y Protestantes; año, ñandú. " * 3
    plegada = calendario._plegar(linea)
    assert all(len(parte.encode("utf-8")) <= 75 for parte in plegada.split("\r\n"))
    assert plegada.replace("\r\n ", "") == linea
    assert calendario._escapar("a,b;c\\d\ne") == "a\\,b\\;c\\\\d\\ne"
    texto = calendario.calendario_feriados(2026, [], cargar_config(), dt.datetime(2026, 10, 12, 7, 0))
    assert "DTSTAMP:20261012T100000Z" in texto  # 07:00 en Chile (horario de verano, UTC-3)
    assert "UID:20261012-encuentro-de-dos-mundos@lucasclaras.cl" in texto


# ---------------------------------------------------------------------------
# 2. Tildes y concordancia
# ---------------------------------------------------------------------------

def test_dolares_con_tilde_en_todos_los_textos(sitio):
    salida, _ = sitio
    rutas = ["/dolar/", "/dolar/2025/", "/dolar/2025/octubre/"] + [
        f"/dolar/{m}-dolares-en-pesos/" for m in paginas.MONTOS_DOLAR]
    for ruta in rutas:
        pagina = leer(salida, ruta)
        textos = [pagina.titulo, pagina.descripcion, pagina.visible] + [n for n, _ in pagina.migas()]
        assert not [t for t in textos if re.search(r"\bdolares\b", t, re.I)], ruta
    monto = leer(salida, "/dolar/100-dolares-en-pesos/")
    assert monto.titulo.startswith("100 dólares en pesos chilenos hoy: ")
    assert monto.descripcion.startswith("100 dólares equivalen a ")
    assert monto.migas()[-1] == ("100 dólares en pesos", f"{URL}/dolar/100-dolares-en-pesos/")
    assert "<h1>100 dólares en pesos chilenos</h1>" in html(salida, "/dolar/100-dolares-en-pesos/")
    assert '<label for="dolar-origen">Dólares (US$)</label>' in html(salida, "/dolar/")


def test_concordancia_en_singular(sitio):
    salida, _ = sitio
    uf = leer(salida, "/uf/").visible
    assert re.search(r"Hoy 1 UF equivale a \$[\d.]+,\d{2} pesos chilenos", uf)
    assert "Hoy 1 dólar equivale a $" in leer(salida, "/dolar/").visible
    assert "Hoy 1 euro equivale a $" in leer(salida, "/euro/").visible
    for archivo in salida.rglob("*.html"):
        texto = archivo.read_text(encoding="utf-8")
        assert not re.search(r"\b1 (UF equivalen|dólares|euros|dolares)\b", texto), archivo


def test_menos_de_10_unidades_con_centavos(sitio, contexto):
    salida, _ = sitio
    dos = leer(salida, "/uf/2-uf-en-pesos/")
    esperado = pesos(2 * contexto.uf_hoy, 2)
    assert dos.titulo == f"2 UF en pesos hoy: {esperado}" and re.search(r",\d{2}$", esperado)
    assert f"Hoy, 2 UF equivalen a {esperado} pesos chilenos" in dos.visible
    assert leer(salida, "/uf/10-uf-en-pesos/").titulo == f"10 UF en pesos hoy: {pesos(10 * contexto.uf_hoy)}"
    assert f'data-uf-monto="3">{pesos(3 * contexto.uf_hoy, 2)}<' in html(salida, "/uf/")


# ---------------------------------------------------------------------------
# 3. Menos páginas casi idénticas y más contenido propio
# ---------------------------------------------------------------------------

def test_montos_con_pagina_propia(sitio):
    salida, _ = sitio
    assert paginas.MONTOS_UF == [2, 3, 5, 10, 15, 20, 30, 50, 100, 200, 300, 500, 1000, 1500, 2000,
                                 2500, 3000, 3500, 4000, 5000, 6000, 8000, 10000]
    assert paginas.MONTOS_DOLAR == [10, 20, 50, 100, 200, 300, 500, 1000, 2000, 5000, 10000]
    assert sorted(int(p.parent.name.split("-")[0]) for p in salida.glob("uf/*-uf-en-pesos/index.html")) \
        == paginas.MONTOS_UF
    assert sorted(int(p.parent.name.split("-")[0]) for p in salida.glob("dolar/*-dolares-en-pesos/index.html")) \
        == paginas.MONTOS_DOLAR
    assert not list(salida.glob("euro/*-en-pesos"))
    assert not archivo_de(salida, "/uf/1-uf-en-pesos/").exists()
    assert not archivo_de(salida, "/dolar/1-dolares-en-pesos/").exists()


def test_tablas_de_conversiones_frecuentes(sitio):
    salida, _ = sitio
    euro = html(salida, "/euro/")
    valor_euro = serie_demo("euro")[DOLAR_DEMO]
    for monto in (10, 50, 100, 500, 1000, 5000):
        texto = f"{monto:,}".replace(",", ".")
        assert f"<td>{texto} euros</td><td class=\"num\">{pesos(monto * valor_euro)}</td>" in euro, monto
    assert "-euros-en-pesos/" not in euro
    dolar = html(salida, "/dolar/")
    valor_dolar = serie_demo("dolar")[DOLAR_DEMO]
    for monto in paginas.MONTOS_DOLAR:
        texto = f"{monto:,}".replace(",", ".")
        assert (f'<a href="/dolar/{monto}-dolares-en-pesos/">{texto} dólares en pesos</a></td>'
                f'<td class="num">{pesos(monto * valor_dolar)}</td>') in dolar, monto


def test_paginas_de_monto_con_contenido_propio(sitio, contexto):
    salida, _ = sitio
    usos = {2: "planes de salud de isapre", 15: "Un arriendo de 15 UF", 50: "Tope imponible mensual de AFP y salud",
            100: "supera el tope imponible", 300: "300 UF para el pie de una vivienda",
            1500: "departamentos pequeños y viviendas económicas",
            5000: "departamentos y casas de las grandes ciudades"}
    for monto, texto in usos.items():
        assert texto in leer(salida, f"/uf/{monto}-uf-en-pesos/").visible, monto
    assert "el dividendo sería" in leer(salida, "/uf/5000-uf-en-pesos/").visible
    assert "el dividendo sería" not in leer(salida, "/uf/300-uf-en-pesos/").visible
    # Variación en 12 meses de la UF, con el valor de hace un año.
    uf_hace_un_anio = contexto.datos.uf_dia(dt.date(2025, 10, 12))
    assert (f"El 12 de octubre de 2025, 1.000 UF equivalían a {pesos(1000 * uf_hace_un_anio)}. "
            f"Hoy son {pesos(1000 * contexto.uf_hoy)}") in leer(salida, "/uf/1000-uf-en-pesos/").visible
    # Dólar: variación en 12 meses y máximo y mínimo del año.
    dolar = {f: v for f, v in serie_demo("dolar").items() if f <= HOY}
    del_anio = {f: v for f, v in dolar.items() if f.year == 2026}
    maximo = max(del_anio, key=del_anio.get)
    minimo = min(del_anio, key=del_anio.get)
    hace_un_anio = max(f for f in dolar if f <= dt.date(2025, 10, 9))
    texto = leer(salida, "/dolar/100-dolares-en-pesos/").visible
    assert (f"El {fecha_larga(hace_un_anio)}, 100 dólares equivalían a {pesos(100 * dolar[hace_un_anio])}"
            in texto)
    assert (f"En 2026, el mismo monto llegó a {pesos(100 * del_anio[maximo])} el {fecha_larga(maximo)}"
            in texto)
    assert f"y bajó a {pesos(100 * del_anio[minimo])} el {fecha_larga(minimo)}" in texto
    assert "compras en tiendas internacionales" in texto
    assert "una diferencia de $5 por dólar" in leer(salida, "/dolar/5000-dolares-en-pesos/").visible


def test_paginas_de_monto_menos_parecidas(sitio):
    """Jaccard de 5-gramas con los números reemplazados. Antes de este cambio el promedio era
    0,77 entre las páginas de UF y 1,00 (idénticas) entre las del dólar y las del euro."""
    salida, _ = sitio
    uf = [f"/uf/{m}-uf-en-pesos/" for m in paginas.MONTOS_UF]
    dolar = [f"/dolar/{m}-dolares-en-pesos/" for m in paginas.MONTOS_DOLAR]
    assert similitud_promedio(salida, uf) < 0.6
    assert similitud_promedio(salida, dolar) < 0.8
    # Páginas de tramos distintos ya no comparten la mayor parte del texto.
    chica, grande = (tejas(" ".join(leer(salida, r).principal))
                     for r in ("/uf/2-uf-en-pesos/", "/uf/5000-uf-en-pesos/"))
    assert jaccard(chica, grande) < 0.5


# ---------------------------------------------------------------------------
# 4. Páginas por año de la UF y del dólar
# ---------------------------------------------------------------------------

def test_paginas_por_anio(sitio):
    salida, _ = sitio
    uf, dolar = leer(salida, "/uf/"), leer(salida, "/dolar/")
    for anio in (2023, 2024, 2025, 2026):
        assert leer(salida, f"/uf/{anio}/").titulo == f"Valor UF {anio}: tabla mensual"
        assert leer(salida, f"/dolar/{anio}/").titulo == f"Dólar observado {anio}: promedio mensual"
        assert f"/uf/{anio}/" in uf.enlaces and f"/dolar/{anio}/" in dolar.enlaces
    assert leer(salida, "/uf/2025/").migas() == [("Inicio", f"{URL}/"), ("UF", f"{URL}/uf/"),
                                                 ("2025", f"{URL}/uf/2025/")]
    meses = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
             "octubre", "noviembre", "diciembre")
    for seccion in ("uf", "dolar"):
        enlaces = leer(salida, f"/{seccion}/2025/").enlaces
        assert [e for e in enlaces if re.fullmatch(rf"/{seccion}/2025/[a-z]+/", e)] == \
            [f"/{seccion}/2025/{mes}/" for mes in meses]


def test_valores_de_las_tablas_anuales(sitio, contexto):
    salida, _ = sitio
    uf = contexto.datos.uf_completa()
    fila = re.search(r'<a href="/uf/2025/octubre/">Octubre</a></td>(.*?)</tr>', html(salida, "/uf/2025/")).group(1)
    assert re.findall(r'<td class="num">([^<]*)</td>', fila)[:3] == [
        pesos(uf[dt.date(2025, 10, d)], 2) for d in (1, 9, 31)]
    assert "Variación del año" in leer(salida, "/uf/2025/").visible
    assert "Variación en lo que va de 2026" in leer(salida, "/uf/2026/").visible
    dias = {f: v for f, v in serie_demo("dolar").items() if (f.year, f.month) == (2025, 10)}
    fila = re.search(r'<a href="/dolar/2025/octubre/">Octubre</a></td>(.*?)</tr>',
                     html(salida, "/dolar/2025/")).group(1)
    assert re.findall(r'<td class="num">([^<]*)</td>', fila) == [
        pesos(sum(dias.values()) / len(dias), 2), pesos(max(dias.values()), 2),
        pesos(min(dias.values()), 2), pesos(dias[max(dias)], 2)]


def test_migas_de_los_meses(sitio):
    salida, _ = sitio
    assert [n for n, _ in leer(salida, "/uf/2025/octubre/").migas()] == ["Inicio", "UF", "2025", "Octubre"]
    assert leer(salida, "/uf/2025/octubre/").migas()[2] == ("2025", f"{URL}/uf/2025/")
    assert [n for n, _ in leer(salida, "/dolar/2025/octubre/").migas()] == ["Inicio", "Dólar", "2025", "Octubre"]


def test_meses_antiguos_a_tres_clics_de_la_portada(sitio):
    salida, _ = sitio
    distancia = profundidades(salida)
    meses = [r for r in distancia if re.fullmatch(r"/(uf|dolar)/\d{4}/[a-z]+/", r)]
    assert len(meses) == len(list(salida.glob("uf/*/*/index.html"))) + len(list(salida.glob("dolar/*/*/index.html")))
    assert max(distancia[r] for r in meses) <= 3


def test_paginas_por_anio_con_datos_desde_2018(tmp_path):
    """Con datos reales hay años desde 2018: cada uno tiene su página y queda a pocos clics."""
    datos = tmp_path / "datos"
    shutil.copytree(DEMO, datos)
    for nombre, solo_habiles, base in (("uf", False, 26800.0), ("dolar", True, 600.0)):
        ruta = datos / "series" / f"{nombre}.json"
        serie = json.loads(ruta.read_text(encoding="utf-8"))
        primero, dia, i = dt.date.fromisoformat(min(serie)), dt.date(2018, 1, 1), 0
        while dia < primero:
            if not solo_habiles or dia.weekday() < 5:
                serie[dia.isoformat()] = round(base + i * 0.5, 2)
                i += 1
            dia += dt.timedelta(days=1)
        ruta.write_text(json.dumps(dict(sorted(serie.items()))), encoding="utf-8")
    salida = tmp_path / "sitio"
    construir(salida=salida, demo=True, hoy=HOY, directorio_datos=datos)
    for seccion in ("uf", "dolar"):
        anios = [a for a in range(2018, 2027) if archivo_de(salida, f"/{seccion}/{a}/").exists()]
        assert anios == list(range(2018, 2027)), seccion
        assert {f"/{seccion}/{a}/" for a in anios} <= set(leer(salida, f"/{seccion}/").enlaces)
    assert "entre el 1 de enero de 2018 y el 31 de diciembre de 2018" in leer(salida, "/uf/2018/").descripcion
    distancia = profundidades(salida)
    assert distancia["/dolar/2018/enero/"] <= 3 and distancia["/uf/2018/enero/"] <= 3
    revisar_seo_basico(salida)


# ---------------------------------------------------------------------------
# 5. Sitemap
# ---------------------------------------------------------------------------

def test_sitemap_solo_con_lastmod(sitio):
    salida, _ = sitio
    sitemap = (salida / "sitemap.xml").read_text(encoding="utf-8")
    assert "<changefreq>" not in sitemap and "<priority>" not in sitemap
    assert sitemap.count("<url>") == len(lastmods(salida))
    assert all(fecha <= HOY.isoformat() for fecha in lastmods(salida).values())


def test_sitemap_omite_paginas_no_indexables_y_canonicas_ajenas():
    cfg = cargar_config()
    comunes = {"plantilla": "x.html", "titulo": "x", "descripcion": "x"}
    lista = [Pagina(ruta="/a/", modificada=dt.date(2026, 1, 1), **comunes),
             Pagina(ruta="/b/", indexar=False, **comunes),
             Pagina(ruta="/c/", canonica="/a/", **comunes),
             Pagina(ruta="/d/", en_sitemap=False, **comunes),
             Pagina(ruta="/e/", modificada=dt.date(2030, 1, 1), **comunes),
             Pagina(ruta="/f/", **comunes)]
    sitemap = sitemap_xml(cfg, lista, HOY)
    assert re.findall(r"<loc>(.*?)</loc><lastmod>(.*?)</lastmod>", sitemap) == [
        (f"{URL}/a/", "2026-01-01"), (f"{URL}/e/", HOY.isoformat()), (f"{URL}/f/", HOY.isoformat())]


def test_lastmod_por_tipo_de_pagina(sitio):
    salida, _ = sitio
    fechas = lastmods(salida)
    dolar = serie_demo("dolar")
    esperado = {
        "/": HOY, "/uf/": HOY, "/uf/1000-uf-en-pesos/": HOY, "/uf/2-uf-en-pesos/": HOY,
        "/dolar/": DOLAR_DEMO, "/dolar/100-dolares-en-pesos/": DOLAR_DEMO, "/euro/": DOLAR_DEMO,
        "/uf/2025/octubre/": dt.date(2025, 10, 31),
        "/uf/2026/octubre/": HOY,                      # destaca el día de hoy
        "/uf/2026/noviembre/": dt.date(2026, 10, 9),   # sus valores se conocen desde el IPC de septiembre
        "/dolar/2025/octubre/": max(f for f in dolar if (f.year, f.month) == (2025, 10)),
        "/dolar/2026/octubre/": DOLAR_DEMO,
        "/uf/2025/": dt.date(2025, 12, 31), "/uf/2026/": dt.date(2026, 10, 9),
        "/dolar/2025/": max(f for f in dolar if f.year == 2025), "/dolar/2026/": DOLAR_DEMO,
        "/utm/": dt.date(2026, 10, 1), "/impuesto-unico/": dt.date(2026, 10, 1),
        "/utm/2026/": dt.date(2026, 10, 1), "/utm/2025/": dt.date(2025, 12, 1),
        "/ipc/": dt.date(2026, 10, 8),
        "/feriados/": HOY,                             # hoy es feriado: cambió la tabla
        "/feriados/2025/": paginas.REVISION_FERIADOS, "/feriados/2027/": paginas.REVISION_FERIADOS,
        "/acerca/": dt.date(2026, 10, 12),
        "/calculadoras/": HOY,                         # sin fecha propia: hoy, como antes
    }
    assert {ruta: fechas[ruta] for ruta in esperado} == {r: f.isoformat() for r, f in esperado.items()}


def test_lastmod_no_cambia_si_la_pagina_no_cambia(contexto):
    """Al día siguiente solo cambian las fechas de las páginas que de verdad cambian."""
    manana = dataclasses.replace(contexto, hoy=HOY + dt.timedelta(days=1),
                                 uf_hoy=contexto.datos.uf_dia(HOY + dt.timedelta(days=1)))

    def fechas(c):
        lista = paginas.paginas_uf(c) + paginas.paginas_divisas(c) + paginas.paginas_feriados(c)
        return {p.ruta: p.modificada for p in lista}

    antes, despues = fechas(contexto), fechas(manana)
    cambian = {r for r in antes if antes[r] != despues[r]}
    assert {"/uf/", "/uf/2026/octubre/", "/feriados/", "/feriados/2026/"} <= cambian
    assert not [r for r in cambian if r.startswith(("/dolar/", "/euro/", "/uf/2025/", "/feriados/2025/"))]
    assert "/uf/2026/" not in cambian and "/uf/2026/noviembre/" not in cambian


# ---------------------------------------------------------------------------
# 6. Detalles: meses incompletos, euro desactualizado y anuncios
# ---------------------------------------------------------------------------

def test_mes_incompleto_no_promete_la_tabla_completa(sitio):
    salida, _ = sitio
    noviembre = leer(salida, "/uf/2026/noviembre/").descripcion
    assert "Tabla completa" not in noviembre
    assert noviembre.endswith("Por ahora se conocen los valores hasta el 9 de noviembre.")
    assert leer(salida, "/uf/2025/octubre/").descripcion.endswith("Tabla completa día a día.")
    # La demo empieza el 9 de enero de 2023: tampoco es la tabla completa del mes.
    enero = leer(salida, "/uf/2023/enero/")
    assert enero.descripcion.endswith("Tabla día a día desde el 9 de enero.")
    assert "Los siguientes se sabrán" not in enero.visible


def test_euro_desactualizado_mantiene_su_pagina_con_aviso(tmp_path):
    datos = tmp_path / "datos"
    shutil.copytree(DEMO, datos)
    ruta = datos / "series" / "euro.json"
    serie = {f: v for f, v in json.loads(ruta.read_text(encoding="utf-8")).items() if f <= "2026-08-31"}
    ruta.write_text(json.dumps(serie), encoding="utf-8")
    ultimo = dt.date.fromisoformat(max(serie))
    salida = tmp_path / "sitio"
    resumen = construir(salida=salida, demo=True, hoy=HOY, directorio_datos=datos)
    euro = leer(salida, "/euro/")
    assert f"No hemos podido actualizar el euro desde el {fecha_larga(ultimo)}" in euro.visible
    assert f"Con el último valor publicado, del {fecha_larga(ultimo)}, 1 euro equivalía a $" in euro.visible
    assert "Hoy 1 euro" not in euro.visible and "hoy" not in euro.titulo
    assert "último valor" in euro.titulo and euro.titulo.endswith(f"({fecha_larga(ultimo)})")
    assert lastmods(salida)["/euro/"] == ultimo.isoformat()
    assert any("/euro/ muestra el último valor" in a for a in resumen["advertencias"])
    # La portada, la API y el widget no muestran un euro viejo como si fuera de hoy.
    assert 'href="/euro/"' not in html(salida, "/")
    assert json.loads((salida / "api/v1/indicadores.json").read_text(encoding="utf-8"))["euro"] is None
    # La página sigue enlazada desde la del dólar.
    assert "/euro/" in leer(salida, "/dolar/").enlaces
    revisar_seo_basico(salida)


@pytest.mark.parametrize("ruta,bloque", [
    ("/uf/2025/octubre/", "uf_mes_superior"),
    ("/dolar/2025/octubre/", "dolar_mes"),
    ("/feriados/", "feriados_superior"),
])
def test_anuncios_debajo_de_la_tabla_principal(contexto, ruta, bloque):
    c = copy.copy(contexto)
    c.datos = copy.copy(contexto.datos)
    c.datos.meta = {k: v for k, v in contexto.datos.meta.items() if k != "demo"}  # fuera del modo demo
    cfg = copy.deepcopy(cargar_config())
    cfg["monetizacion"]["adsense"].update(activo=True, publisher_id="ca-pub-1234567890123456",
                                          slots={"uf_mes_superior": "1", "dolar_mes": "2",
                                                 "feriados_superior": "3"})
    entorno = crear_entorno(cfg, c, {})
    lista = paginas.paginas_uf(c) + paginas.paginas_divisas(c) + paginas.paginas_feriados(c)
    pagina = next(p for p in lista if p.ruta == ruta)
    texto = entorno.get_template(pagina.plantilla).render(pagina=pagina, jsonld=[], **pagina.contexto)
    slot = cfg["monetizacion"]["adsense"]["slots"][bloque]
    assert f'data-ad-slot="{slot}"' in texto
    assert texto.index("</table>") < texto.index("adsbygoogle\" style"), "el anuncio va después de la tabla"
