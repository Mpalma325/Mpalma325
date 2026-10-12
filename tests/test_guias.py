"""Guías (contenido/guias/*.md): validación, render y páginas generadas."""

from __future__ import annotations

import copy
import datetime as dt
import json
import re

import markdown
import pytest
import yaml
from jinja2 import Environment, StrictUndefined
from markupsafe import escape

from lucas import guias
from lucas.__main__ import main
from lucas.config import cargar_config
from lucas.construir import ErrorConstruccion, construir
from lucas.guias import (CONFIG_EXTENSIONES, EXTENSIONES, MARCAS_JINJA, archivos_de_guias,
                         cargar_guias, contexto_de_revision, guias_destacadas, ordenar,
                         revisar_todas, separar, variables_de)

from .conftest import HOY

JSONLD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


@pytest.fixture(scope="module")
def contexto():
    """Contexto y entorno Jinja del sitio con los datos de demostración."""
    return contexto_de_revision(demo=True, hoy=HOY)


@pytest.fixture(scope="module")
def revisiones(contexto):
    c, entorno = contexto
    return revisar_todas(archivos_de_guias(), c, entorno)


@pytest.fixture(scope="module")
def sitio(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio_guias")
    resumen = construir(salida=salida, demo=True, hoy=HOY)
    c, entorno = contexto_de_revision(demo=True, hoy=HOY)
    return salida, resumen, cargar_guias(c, entorno)


def texto_guia(cuerpo: str | None = None, **campos) -> str:
    """Una guía válida; ``campos`` reemplaza (o con None, quita) campos del front matter."""
    datos = {
        "titulo": "Guía de prueba ({{ hoy.year }})",
        "descripcion": "Descripción de prueba con el largo suficiente para cumplir las reglas del "
                       "validador de guías de Lucas Claras.",
        "h1": "Guía de prueba",
        "resumen": "Resumen de la guía de prueba.",
        "publicada": dt.date(2026, 10, 1),
        "revisada": dt.date(2026, 10, 12),
        "categoria": "trabajo",
        "calculadoras": ["/calculadoras/sueldo-liquido/"],
        "fuentes": [{"nombre": "Código del Trabajo", "url": "https://www.bcn.cl/leychile/navegar?idNorma=207436"},
                    {"nombre": "AFC Chile", "url": "https://www.afc.cl/"}],
        "faq": [{"pregunta": "¿Cuánto es el sueldo mínimo?",
                 "respuesta": "Hoy el ingreso mínimo mensual es de {{ p.imm|pesos }} brutos."},
                {"pregunta": "¿Dónde se calcula el líquido?",
                 "respuesta": "En la calculadora de sueldo líquido, con los parámetros vigentes."}],
    }
    for clave, valor in campos.items():
        if valor is None:
            datos.pop(clave)
        else:
            datos[clave] = valor
    if cuerpo is None:
        relleno = " ".join(["palabra"] * 180)
        cuerpo = "\n".join(f"## Sección {n}\n\n{relleno}\n" for n in (1, 2, 3))
    return "---\n" + yaml.safe_dump(datos, allow_unicode=True, sort_keys=False) + "---\n" + cuerpo


# ---------------------------------------------------------------------------
# Las guías del repositorio
# ---------------------------------------------------------------------------

def test_todas_las_guias_del_repo_validan(revisiones):
    assert revisiones, "no hay guías en contenido/guias/"
    for r in revisiones:
        assert r.errores == [], (r.archivo.name, r.errores)
        guia = r.guia
        textos = [guia.titulo, guia.descripcion, guia.h1, guia.resumen, str(guia.html)]
        textos += [parte for pregunta in guia.faq for parte in pregunta]
        for texto in textos:
            assert not any(marca in texto for marca in MARCAS_JINJA), (r.archivo.name, texto[:80])
        assert guia.indice, r.archivo.name


def test_render_igual_que_el_validador(contexto):
    """El cuerpo se procesa con el entorno del sitio, pero con el manejo de espacios del
    validador de referencia (sin trim_blocks): el HTML debe ser idéntico."""
    c, entorno = contexto
    referencia = Environment(undefined=StrictUndefined, autoescape=True)
    referencia.filters.update(entorno.filters)
    referencia.globals["ruta"] = lambda destino: destino
    variables = variables_de(c)
    for r in revisar_todas(archivos_de_guias(), c, entorno):
        _, cuerpo, _ = separar(r.archivo.read_text(encoding="utf-8"))
        esperado = markdown.markdown(referencia.from_string(cuerpo).render(**variables),
                                     extensions=EXTENSIONES, extension_configs=CONFIG_EXTENSIONES)
        # El sitio además envuelve cada tabla en una caja desplazable.
        esperado = esperado.replace("<table>", '<div class="tabla-desplazable"><table>').replace(
            "</table>", "</table></div>")
        assert r.html == esperado, r.archivo.name


def test_tabla_con_for_no_se_corta():
    """Las guías usan el manejo de espacios del validador (sin trim_blocks): el salto de línea
    después de {% endfor %} se mantiene y la tabla termina antes del texto que sigue."""
    c, entorno = contexto_de_revision(demo=True, hoy=HOY)
    plantilla = "| a |\n|---|\n{% for x in [1, 2] -%}\n| {{ x }} |\n{% endfor %}\nfin"
    salida = guias.entorno_de_guias(entorno).from_string(plantilla).render()
    assert salida == "| a |\n|---|\n| 1 |\n| 2 |\n\nfin"


# ---------------------------------------------------------------------------
# Páginas generadas
# ---------------------------------------------------------------------------

def test_indice_y_paginas_de_guias(sitio):
    salida, resumen, lista = sitio
    indice = (salida / "guias" / "index.html").read_text(encoding="utf-8")
    assert "/guias/" in resumen["rutas"]
    for guia in lista:
        html = (salida / "guias" / guia.slug / "index.html").read_text(encoding="utf-8")
        assert guia.ruta in resumen["rutas"]
        assert f'href="{guia.ruta}"' in indice and escape(guia.resumen) in indice
        assert f"<h1>{escape(guia.h1)}</h1>" in html
        assert f"<title>{escape(guia.titulo)}</title>" in html
        assert "Actualizado el" in html and "En esta guía" in html and "Calcúlalo" in html
        for fuente in guia.fuentes:
            assert f'href="{escape(fuente["url"])}"' in html
        for pregunta, _ in guia.faq:
            assert escape(pregunta) in html
        articulo = html.split('<article class="guia">')[1].split("</article>")[0]  # sin el JSON-LD
        assert not any(marca in articulo for marca in MARCAS_JINJA), guia.slug
        # Cada guía aparece en la sección de su categoría del índice
        seccion = indice.split(f'id="{guia.categoria}"')[1].split("</section>")[0]
        assert f'href="{guia.ruta}"' in seccion


def test_navegacion_lleva_a_las_guias(sitio):
    salida, _, lista = sitio
    inicio = (salida / "index.html").read_text(encoding="utf-8")
    calculadoras = (salida / "calculadoras" / "index.html").read_text(encoding="utf-8")
    assert inicio.count('href="/guias/"') >= 3  # menú, pie y bloque de guías destacadas
    for pagina in (inicio, calculadoras):
        assert any(f'href="{g.ruta}"' in pagina for g in lista)


def test_jsonld_article(sitio):
    salida, _, lista = sitio
    for guia in lista:
        html = (salida / "guias" / guia.slug / "index.html").read_text(encoding="utf-8")
        bloques = [json.loads(b) for b in JSONLD.findall(html)]
        tipos = [b["@type"] for b in bloques]
        assert tipos.count("Article") == 1 and "BreadcrumbList" in tipos and "FAQPage" in tipos
        articulo = next(b for b in bloques if b["@type"] == "Article")
        assert articulo["@context"] == "https://schema.org"
        assert articulo["headline"] == guia.h1
        assert articulo["description"] == guia.descripcion
        assert articulo["datePublished"] == guia.publicada.isoformat()
        assert articulo["dateModified"] == guia.revisada.isoformat()
        assert articulo["inLanguage"] == "es-CL"
        for rol in ("author", "publisher"):
            assert articulo[rol]["@type"] == "Organization" and articulo[rol]["name"] == "Lucas Claras"
        canonica = f"https://lucasclaras.cl{guia.ruta}"
        assert f'<link rel="canonical" href="{canonica}">' in html
        assert articulo["mainEntityOfPage"] == {"@type": "WebPage", "@id": canonica}
        assert articulo["image"].startswith("https://")
        migas = next(b for b in bloques if b["@type"] == "BreadcrumbList")["itemListElement"]
        assert [m["name"] for m in migas] == ["Inicio", "Guías", guia.h1]
        faq = next(b for b in bloques if b["@type"] == "FAQPage")["mainEntity"]
        assert len(faq) == len(guia.faq)


def test_guias_en_subcarpeta(tmp_path):
    """ruta() dentro de las guías usa la base del sitio (GitHub Pages sin dominio propio)."""
    cfg = copy.deepcopy(cargar_config())
    cfg["sitio"]["url"] = "https://usuario.github.io/lucas-claras"
    cfg["sitio"]["ruta_base"] = "/lucas-claras"
    construir(salida=tmp_path, demo=True, hoy=HOY, cfg=cfg)
    paginas = list((tmp_path / "guias").rglob("index.html"))
    assert len(paginas) > 1
    for archivo in paginas:
        internos = re.findall(r'(?:href|src)="(/[^"]*)"', archivo.read_text(encoding="utf-8"))
        assert internos and all(e.startswith("/lucas-claras/") for e in internos), archivo


def test_sitemap_con_fecha_de_revision(sitio):
    salida, _, lista = sitio
    sitemap = (salida / "sitemap.xml").read_text(encoding="utf-8")
    assert "<loc>https://lucasclaras.cl/guias/</loc>" in sitemap
    for guia in lista:
        assert (f"<loc>https://lucasclaras.cl{guia.ruta}</loc><lastmod>{guia.revisada.isoformat()}</lastmod>"
                in sitemap)


def test_enlaces_de_calculadoras_existen(sitio):
    salida, resumen, lista = sitio
    for guia in lista:
        html = (salida / "guias" / guia.slug / "index.html").read_text(encoding="utf-8")
        for destino in guia.calculadoras:
            assert (salida / destino.lstrip("/") / "index.html").exists(), (guia.slug, destino)
            assert f'href="{destino}"' in html
    assert not [a for a in resumen["advertencias"] if "no existe en el sitio" in a]


# ---------------------------------------------------------------------------
# Errores claros
# ---------------------------------------------------------------------------

def test_guia_rota_detiene_la_construccion(tmp_path, monkeypatch):
    carpeta = tmp_path / "guias"
    carpeta.mkdir()
    (carpeta / "guia-rota.md").write_text(texto_guia(h1=None), encoding="utf-8")
    monkeypatch.setattr(guias, "DIRECTORIO", carpeta)
    with pytest.raises(ErrorConstruccion) as error:
        construir(salida=tmp_path / "dist", demo=True, hoy=HOY)
    mensaje = str(error.value)
    assert "guia-rota.md" in mensaje and "falta el campo obligatorio 'h1'" in mensaje
    assert not (tmp_path / "dist").exists()


def test_error_de_plantilla_indica_la_linea_del_archivo(tmp_path, contexto):
    c, entorno = contexto
    relleno = " ".join(["palabra"] * 180)
    cuerpo = f"## Uno\n\n{relleno}\n\n## Dos\n\nEl valor es {{{{ variable_inexistente }}}}.\n\n## Tres\n\n{relleno}\n"
    texto = texto_guia(cuerpo=cuerpo)
    linea = texto.splitlines().index("El valor es {{ variable_inexistente }}.") + 1
    (tmp_path / "guia-con-error.md").write_text(texto, encoding="utf-8")
    with pytest.raises(ErrorConstruccion) as error:
        cargar_guias(c, entorno, tmp_path)
    assert f"línea {linea} del archivo" in str(error.value)
    assert "variable_inexistente" in str(error.value)


@pytest.mark.parametrize("campos, problema", [
    ({"revisada": dt.date(2026, 9, 1)}, "revisada es anterior a publicada"),
    ({"categoria": "deportes"}, "categoria 'deportes'"),
    ({"titulo": "Un título larguísimo que pasa con creces los setenta caracteres permitidos en una guía"},
     "máx. 70"),
    ({"fuentes": [{"nombre": "Una sola", "url": "https://www.afc.cl/"}]}, "al menos 2 fuentes"),
    ({"faq": [{"pregunta": "Sin signos", "respuesta": "Una respuesta con más de cuarenta caracteres."},
              {"pregunta": "¿Bien?", "respuesta": "Otra respuesta con más de cuarenta caracteres."}]},
     "entre '¿' y '?'"),
    ({"calculadoras": ["calculadoras/sin-barra"]}, "ruta de calculadora inválida"),
])
def test_reglas_del_validador(tmp_path, contexto, campos, problema):
    c, entorno = contexto
    (tmp_path / "guia.md").write_text(texto_guia(**campos), encoding="utf-8")
    with pytest.raises(ErrorConstruccion, match=re.escape(problema)):
        cargar_guias(c, entorno, tmp_path)


def test_cuerpo_con_enlace_interno_sin_ruta(tmp_path, contexto):
    c, entorno = contexto
    relleno = " ".join(["palabra"] * 180)
    cuerpo = "\n".join(f"## S{n}\n\n{relleno}\n" for n in (1, 2, 3)) + "\n[UF](/uf/)\n"
    (tmp_path / "guia.md").write_text(texto_guia(cuerpo=cuerpo), encoding="utf-8")
    with pytest.raises(ErrorConstruccion, match="enlace interno sin ruta"):
        cargar_guias(c, entorno, tmp_path)


def test_titulo_repetido_y_archivos_ignorados(tmp_path, contexto):
    c, entorno = contexto
    for nombre in ("una.md", "otra.md", "_borrador.md", "LEEME.md"):
        (tmp_path / nombre).write_text(texto_guia(), encoding="utf-8")
    assert [a.name for a in archivos_de_guias(tmp_path)] == ["otra.md", "una.md"]
    with pytest.raises(ErrorConstruccion, match="título repetido"):
        cargar_guias(c, entorno, tmp_path)


def test_avisos_no_detienen_la_construccion(tmp_path, contexto):
    c, entorno = contexto
    (tmp_path / "guia.md").write_text(texto_guia(campo_raro="x"), encoding="utf-8")
    revision, = revisar_todas(archivos_de_guias(tmp_path), c, entorno)
    assert revision.errores == []
    assert any("campo desconocido 'campo_raro'" in a for a in revision.avisos)
    assert any("palabras (ideal" in a for a in revision.avisos)


def test_revisada_se_compara_con_la_fecha_real(tmp_path, contexto, monkeypatch):
    """El sitio de demostración tiene fecha fija: una guía revisada después igual se acepta."""
    c, entorno = contexto
    (tmp_path / "guia.md").write_text(texto_guia(revisada=dt.date(2027, 1, 15)), encoding="utf-8")
    monkeypatch.setattr(guias, "hoy_chile", lambda: dt.date(2027, 2, 1))
    assert len(cargar_guias(c, entorno, tmp_path)) == 1
    monkeypatch.setattr(guias, "hoy_chile", lambda: dt.date(2027, 1, 10))
    with pytest.raises(ErrorConstruccion, match="revisada es posterior a hoy"):
        cargar_guias(c, entorno, tmp_path)


# ---------------------------------------------------------------------------
# Comando, variables y orden
# ---------------------------------------------------------------------------

def test_comando_guias(tmp_path, capsys):
    assert main(["guias", "--demo", "--hoy", HOY.isoformat()]) == 0
    assert ", 0 errores." in capsys.readouterr().out
    rota = tmp_path / "rota.md"
    rota.write_text(texto_guia(calculadoras=["/calculadoras/no-existe/"], categoria="deportes"), encoding="utf-8")
    assert main(["guias", "--demo", "--hoy", HOY.isoformat(), str(rota)]) == 1
    salida = capsys.readouterr().out
    assert "[ERROR] rota.md" in salida and "categoria 'deportes'" in salida


def test_comando_guias_avisa_calculadoras_inexistentes(tmp_path, capsys):
    guia = tmp_path / "guia.md"
    guia.write_text(texto_guia(calculadoras=["/calculadoras/no-existe/"]), encoding="utf-8")
    assert main(["guias", "--demo", "--hoy", HOY.isoformat(), str(guia)]) == 0
    assert "la página /calculadoras/no-existe/ no existe en el sitio" in capsys.readouterr().out


def test_variables_de_las_guias(contexto):
    c, _ = contexto
    variables = variables_de(c)
    assert set(variables) == {"p", "uf_hoy", "utm_hoy", "hoy", "dolar", "calc", "sitio", "feriados"}
    feriados = variables["feriados"]
    assert {f.year for f in feriados} == {HOY.year - 2, HOY.year - 1, HOY.year, HOY.year + 1}
    assert dt.date(HOY.year, 9, 18) in feriados and dt.date(HOY.year + 1, 1, 1) in feriados


def test_jinja_completo_en_el_cuerpo(tmp_path, contexto):
    """Macros, desempaquetado de tuplas, set y cálculos con feriados, como en las guías de finiquito."""
    c, entorno = contexto
    relleno = " ".join(["palabra"] * 180)
    cuerpo = (
        "{% macro fila(nombre, valor) -%}\n| {{ nombre }} | {{ valor|pesos }} |\n{%- endmacro %}\n"
        "{% set f = calc.finiquito(calc.sumar_meses(hoy, -43), hoy, 1200000, 'necesidades_empresa', p, "
        "feriados, aviso_dado=False) %}\n"
        f"## Uno\n\n{relleno}\n\n| Concepto | Monto |\n|---|---:|\n"
        "{% for nombre, valor in [('Indemnización', f.indemnizacion_anios), ('Feriado', f.feriado)] -%}\n"
        "{{ fila(nombre, valor) }}\n{% endfor %}\n"
        f"## Dos\n\n{relleno}\n\n## Tres\n\n{relleno}\n"
    )
    (tmp_path / "guia.md").write_text(texto_guia(cuerpo=cuerpo), encoding="utf-8")
    guia, = cargar_guias(c, entorno, tmp_path)
    assert "<td>Indemnización</td>" in guia.html and "<td>Feriado</td>" in guia.html


def _guia(slug: str, categoria: str, orden: int | None, titulo: str) -> guias.Guia:
    return guias.Guia(slug=slug, archivo=None, titulo=titulo, descripcion="", h1=titulo, resumen="",
                      publicada=HOY, revisada=HOY, categoria=categoria, orden=orden, calculadoras=[],
                      fuentes=[], faq=[], html="", indice=[], palabras=1000)


def test_orden_y_destacadas():
    lista = [_guia("b", "trabajo", None, "¿Qué es el finiquito?"), _guia("a", "trabajo", 20, "Zeta"),
             _guia("c", "trabajo", 10, "Beta"), _guia("d", "indicadores", None, "Álgebra de la UF"),
             _guia("e", "trabajo", None, "Cómo leer tu liquidación")]
    # Primero las que tienen "orden"; después alfabético sin tildes ni signos iniciales.
    assert [g.slug for g in ordenar(lista)] == ["c", "a", "d", "e", "b"]
    assert [g.slug for g in guias_destacadas(lista, 3)] == ["c", "d", "a"]
