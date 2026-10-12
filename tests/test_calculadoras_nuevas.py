"""Calculadoras de IVA, horas extra y crédito de consumo: casos verificados a mano o contra
ejemplos oficiales, paridad Python/JavaScript y páginas del sitio de demostración."""

from __future__ import annotations

import datetime as dt
import json
import re

import pytest

from lucas import calculos as c
from lucas.construir import construir
from lucas.paginas_calculadoras_extra import enumerar, factor_texto, porcentaje_corto

from .conftest import HOY
from .test_paridad_js import NODE, ejecutar_js, iguales

requiere_node = pytest.mark.skipif(NODE is None, reason="Node.js no está instalado")


# --- IVA ------------------------------------------------------------------------
# Tasa general de 19% (DL 825, art. 14), vigente desde el 1-10-2003 (Ley 19.888).
# Montos en pesos enteros: el IVA de un neto se redondea al peso; al desglosar un
# precio con IVA, el neto es total / 1,19 redondeado y el IVA la diferencia.

def test_iva_vigente(p, params):
    assert p["iva"] == 0.19
    assert params.vigente("iva", dt.date(2003, 10, 1))["tasa"] == 0.19


def test_iva_desde_neto(p):
    assert c.iva_desde_neto(100_000, p) == {"neto": 100_000, "iva": 19_000, "total": 119_000, "tasa": 0.19}
    assert c.iva_desde_neto(1_050, p)["iva"] == 200     # 199,5: la mitad se redondea hacia arriba
    assert c.iva_desde_neto(1_049, p)["iva"] == 199     # 199,31


def test_iva_desde_total(p):
    r = c.iva_desde_total(119_000, p)
    assert (r["neto"], r["iva"], r["total"]) == (100_000, 19_000, 119_000)
    r = c.iva_desde_total(50_000, p)                    # 50.000 / 1,19 = 42.016,81
    assert (r["neto"], r["iva"], r["total"]) == (42_017, 7_983, 50_000)
    r = c.iva_desde_total(1_000, p)                     # 840,34
    assert (r["neto"], r["iva"]) == (840, 160)


@pytest.mark.parametrize("neto", [1, 7, 99, 1_234, 99_999, 1_000_001, 12_345_678])
def test_iva_ida_y_vuelta(p, neto):
    """Desglosar el total de un neto devuelve el mismo neto y el mismo IVA."""
    ida = c.iva_desde_neto(neto, p)
    vuelta = c.iva_desde_total(ida["total"], p)
    assert (vuelta["neto"], vuelta["iva"]) == (ida["neto"], ida["iva"])


# --- Horas extra ------------------------------------------------------------------
# Dirección del Trabajo (https://www.dt.gob.cl/portal/1628/w3-article-95182.html): con
# sueldo mensual y 42 horas, el sueldo se divide por 30, se multiplica por 28 y se divide
# por 168; a eso se suma el 50%, "a igual resultado se llegará si se multiplica el sueldo
# mensual por el factor 0,0083333". Para 45 horas la DT usaba 0,0077777 (Oficio Circular
# N° 4 de 1987). Fechas de la Ley 21.561: 44 h desde el 26-04-2024, 42 h desde el
# 26-04-2026 y 40 h desde el 26-04-2028.

def test_jornada_legal_por_fecha(params):
    def jornada(fecha):
        return params.vigente("jornada_laboral", fecha)["horas_semanales"]

    assert jornada(dt.date(2024, 4, 25)) == 45
    assert jornada(dt.date(2024, 4, 26)) == 44
    assert jornada(dt.date(2026, 4, 25)) == 44
    assert jornada(dt.date(2026, 4, 26)) == 42
    assert jornada(dt.date(2028, 4, 25)) == 42
    assert jornada(dt.date(2028, 4, 26)) == 40


def test_factores_publicados_por_la_dt(p):
    assert (p["jornada_semanal_horas"], p["recargo_horas_extra"]) == (42, 0.5)
    esperados = {45: "0,0077777", 44: "0,0079545", 42: "0,0083333", 40: "0,00875"}
    for jornada, texto in esperados.items():
        assert factor_texto(c.factor_horas_extra(jornada, p)) == texto


def test_horas_extra_con_la_formula_de_la_dt(p):
    r = c.horas_extra(600_000, 10, 42, p)
    assert r["valor_hora"] == pytest.approx(600_000 / 30 * 28 / 168)   # $3.333,33
    assert r["valor_hora_extra"] == pytest.approx(5_000)
    assert round(r["valor_hora_extra"]) == round(600_000 * 0.0083333)   # con el factor de la DT
    assert r["total"] == 50_000
    assert not r["minimo_aplicado"]
    assert c.horas_extra(800_000, 10, 42, p)["total"] == 66_667       # 6.666,67 × 10
    assert c.horas_extra(800_000, 1.5, 42, p)["total"] == 10_000


def test_horas_extra_no_se_calculan_bajo_el_minimo(p):
    # Sueldo menor que el ingreso mínimo de $553.553: la base es el mínimo (DT, ORD. N° 4957).
    r = c.horas_extra(400_000, 10, 42, p)
    assert r["minimo_aplicado"] and r["base"] == 553_553
    assert r["valor_hora_extra"] == pytest.approx(553_553 / 30 * 28 / 168 * 1.5)
    # Jornada parcial de 30 horas: mínimo proporcional (art. 40 bis A), 553.553 × 30 / 42 = 395.395
    r = c.horas_extra(300_000, 4, 30, p)
    assert r["minimo_aplicado"]
    assert r["base"] == pytest.approx(395_395)
    assert r["valor_hora"] == pytest.approx(395_395 / 30 * 28 / 120)
    assert not c.horas_extra(450_000, 4, 30, p)["minimo_aplicado"]
    # Una jornada mayor que la legal (meses anteriores a la rebaja) usa el mínimo completo
    assert c.horas_extra(500_000, 1, 44, p)["minimo"] == 553_553


# --- Crédito de consumo ---------------------------------------------------------------
# Impuesto de timbres: 0,066% por mes o fracción con tope de 0,8% (DL 3.475, art. 1 N° 3;
# SII, Circular N° 17 de 2015). CAE: tasa mensual que iguala el valor presente de los
# pagos con el monto líquido recibido en el mes 0, multiplicada por 12 (DS 43 de 2012).

def test_tasa_del_impuesto_de_timbres(p):
    assert c.tasa_timbres(1, p) == pytest.approx(0.00066)
    assert c.tasa_timbres(12, p) == pytest.approx(0.00792)
    assert c.tasa_timbres(13, p) == 0.008
    assert c.tasa_timbres(60, p) == 0.008
    assert [porcentaje_corto(x) for x in (0.00066, 0.00792, 0.008)] == ["0,066%", "0,792%", "0,8%"]


def test_impuesto_financiado_como_en_el_ejemplo_de_la_suseso(p):
    """Ejemplo oficial de la SUSESO (Compendio de la Ley 18.833, 3.7.9): crédito de $1.000.000
    a 12 meses otorgado en 2011, cuando el impuesto era 0,05% por mes con tope de 0,6%, con
    gastos notariales de $420 y $6.400 de intereses proyectados que se suman al crédito: el
    impuesto es $6.077 y el capital inicial $1.012.897 (el impuesto se calcula sobre sí mismo)."""
    tasas_2011 = dict(p, timbres_tasa_mensual=0.0005, timbres_tope=0.006)
    r = c.credito_consumo(1_000_000, 12, 0.012, tasas_2011, gastos=420 + 6_400)
    assert r["impuesto"] == 6_077
    assert r["monto_bruto"] == 1_012_897


def test_cuota_francesa():
    assert c.cuota_francesa(1_200_000, 0, 12) == 100_000
    cerrada = 3_024_194 * 0.015 / (1 - 1.015 ** -36)
    assert c.cuota_francesa(3_024_194, 0.015, 36) == pytest.approx(cerrada, rel=1e-12)


def test_credito_de_consumo_de_tres_millones(p):
    r = c.credito_consumo(3_000_000, 36, 0.015, p)
    assert (r["impuesto"], r["monto_bruto"]) == (24_194, 3_024_194)   # 3.000.000 / 0,992
    assert r["cuota"] == r["cuota_total"] == 109_332
    assert r["total_cuotas"] == r["costo_total"] == 109_332 * 36
    assert r["intereses"] == 109_332 * 36 - 3_024_194
    assert r["sobrecosto"] == 109_332 * 36 - 3_000_000
    assert round(r["cae"] * 100, 2) == 18.58
    # La CAE iguala el valor presente de las cuotas con lo que se recibe
    assert c.valor_presente([r["cuota_total"]] * 36, r["cae"] / 12) == pytest.approx(3_000_000, abs=1e-4)


def test_cae_sin_costos_es_la_tasa_mensual_por_12(p):
    sin_impuesto = dict(p, timbres_tasa_mensual=0.0, timbres_tope=0.0)
    r = c.credito_consumo(1_000_000, 12, 0.012, sin_impuesto)
    assert r["impuesto"] == 0
    assert r["cae"] == pytest.approx(0.144, abs=5e-5)   # solo difiere por el redondeo de la cuota


def test_seguros_y_gastos_suben_la_cae(p):
    base = c.credito_consumo(3_000_000, 36, 0.015, p)
    seguros = c.credito_consumo(3_000_000, 36, 0.015, p, seguros=5_000)
    gastos = c.credito_consumo(3_000_000, 36, 0.015, p, gastos=50_000)
    assert base["cae"] < seguros["cae"] and base["cae"] < gastos["cae"]
    assert seguros["cuota_total"] == base["cuota"] + 5_000
    assert seguros["costo_total"] == (base["cuota"] + 5_000) * 36
    assert gastos["monto_bruto"] == round(3_050_000 / 0.992)


def test_impuesto_y_gastos_al_contado(p):
    r = c.credito_consumo(3_000_000, 36, 0.015, p, gastos=10_000, financiar=False)
    assert (r["impuesto"], r["monto_bruto"], r["al_contado"]) == (24_000, 3_000_000, 34_000)
    assert r["costo_total"] == r["total_cuotas"] + 34_000
    # Lo que se paga al firmar se descuenta del monto recibido
    vp = c.valor_presente([r["cuota_total"]] * 36, r["cae"] / 12)
    assert vp == pytest.approx(3_000_000 - 34_000, abs=1e-4)


def test_cae_exige_un_monto_liquido_positivo():
    with pytest.raises(ValueError):
        c.carga_anual_equivalente(0, [100.0] * 12)


def test_enumerar():
    assert enumerar(["a"]) == "a"
    assert enumerar(["a", "b", "c"]) == "a, b y c"
    assert enumerar(["44", "42", "40"], "a ") == "44, a 42 y a 40"


# --- Paridad con JavaScript -----------------------------------------------------------

@requiere_node
def test_calculadoras_nuevas_identicas_en_javascript(p):
    sin_impuesto = dict(p, timbres_tasa_mensual=0.0, timbres_tope=0.0)
    casos = []
    for neto in (0, 1, 1_049, 1_050, 99_999.6, 123_456_789):
        casos.append(("ivaDesdeNeto", [neto, p], c.iva_desde_neto(neto, p)))
    for total in (1, 1_000, 50_000, 119_000, 987_654_321):
        casos.append(("ivaDesdeTotal", [total, p], c.iva_desde_total(total, p)))
    for sueldo, horas, jornada in ((600_000, 10, 42), (400_000, 3.5, 42), (300_000, 4, 30),
                                   (2_345_678, 17.25, 44), (553_553, 52, 40), (1_000_000, 0, 45)):
        casos.append(("horasExtra", [sueldo, horas, jornada, p], c.horas_extra(sueldo, horas, jornada, p)))
        casos.append(("factorHorasExtra", [jornada, p], c.factor_horas_extra(jornada, p)))
    for meses in (1, 12, 13, 36, 120):
        casos.append(("tasaTimbres", [meses, p], c.tasa_timbres(meses, p)))
    escenarios = [
        (3_000_000, 36, 0.015, p, 0, 0, True),
        (3_000_000, 36, 0.015, p, 4_500, 25_000, False),
        (1_000_000, 12, 0.012, sin_impuesto, 0, 0, True),
        (750_000, 1, 0.03, p, 0, 0, True),
        (12_345_678, 60, 0.0099, p, 12_000, 150_000, True),
        (500_000, 24, 0.0, p, 1_000, 0, True),
        (2_000_000, 48, 0.2, p, 0, 0, False),
    ]
    for monto, meses, tasa, parametros, seguros, gastos, financiar in escenarios:
        casos.append(("creditoConsumo", [monto, meses, tasa, parametros, seguros, gastos, financiar],
                      c.credito_consumo(monto, meses, tasa, parametros, seguros, gastos, financiar)))
    casos.append(("cuotaFrancesa", [3_024_194, 0.015, 36], c.cuota_francesa(3_024_194, 0.015, 36)))
    casos.append(("valorPresente", [[109_332] * 36, 0.0154], c.valor_presente([109_332] * 36, 0.0154)))
    casos.append(("cargaAnualEquivalente", [1_000_000, [100_000.0] * 12],
                  c.carga_anual_equivalente(1_000_000, [100_000.0] * 12)))
    resultados = ejecutar_js([{"fn": fn, "args": args} for fn, args, _ in casos])
    errores = [f"{fn}: {e}" for (fn, _, py), js in zip(casos, resultados) for e in iguales(py, js)]
    assert errores == []
    # El solver de la CAE y la cuota usan las mismas operaciones: el resultado es idéntico
    for (fn, _, py), js in zip(casos, resultados):
        if fn == "creditoConsumo":
            assert (js["cae"], js["cuota"]) == (py["cae"], py["cuota"])


# --- Sitio de demostración --------------------------------------------------------------

RUTAS = ("/calculadoras/iva/", "/calculadoras/horas-extra/", "/calculadoras/credito-consumo/")


@pytest.fixture(scope="module")
def sitio(tmp_path_factory):
    salida = tmp_path_factory.mktemp("sitio_calculadoras_nuevas")
    construir(salida=salida, demo=True, hoy=HOY)
    return salida


def leer(sitio, ruta: str) -> str:
    return (sitio / ruta.strip("/") / "index.html").read_text(encoding="utf-8")


def test_paginas_nuevas_con_valores_iniciales(sitio):
    iva = leer(sitio, "/calculadoras/iva/")
    assert 'data-calculadora="iva"' in iva
    assert "$119.000" in iva and "$19.000" in iva            # 100.000 neto
    assert "$42.017" in iva and "$7.983" in iva               # 50.000 con IVA incluido
    horas = leer(sitio, "/calculadoras/horas-extra/")
    assert 'data-calculadora="horas_extra"' in horas
    assert all(f in horas for f in ("0,0077777", "0,0079545", "0,0083333", "0,00875"))
    assert "$66.667" in horas                                 # 10 horas extra con $800.000
    assert "$4.613" in horas                                  # hora extra con el sueldo mínimo
    consumo = leer(sitio, "/calculadoras/credito-consumo/")
    assert 'data-calculadora="consumo"' in consumo
    assert "$109.332" in consumo and "18,58%" in consumo and "$24.194" in consumo
    assert 'href="https://www.cmfchile.cl/"' in consumo


def test_paginas_nuevas_son_calculadoras_completas(sitio):
    for ruta in RUTAS:
        html = leer(sitio, ruta)
        assert 'aria-live="polite"' in html and "data-compartir" in html, ruta
        assert "js/calculos.js" in html, ruta
        datos = json.loads(re.search(r'id="datos-pagina">(.*?)</script>', html).group(1))
        p = datos["parametros"]
        assert (p["iva"], p["jornada_semanal_horas"], p["timbres_tope"]) == (0.19, 42, 0.008), ruta
        tipos = [json.loads(b)["@type"] for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)]
        assert {"WebApplication", "BreadcrumbList", "FAQPage"} <= set(tipos), ruta


def test_enlaces_a_las_paginas_nuevas(sitio):
    indice = leer(sitio, "/calculadoras/")
    portada = (sitio / "index.html").read_text(encoding="utf-8")   # el pie de página
    for ruta in RUTAS:
        assert f'href="{ruta}"' in indice, ruta
        assert f'href="{ruta}"' in portada, ruta
