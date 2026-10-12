"""Metodología de la UF y la UTM, carga de datos y descarga (sin internet)."""

import datetime as dt
import json

import pytest

from lucas import datos as d
from lucas import fuentes
from lucas.config import cargar_parametros

from .conftest import DATOS_REALES, hay_datos_reales

D = dt.date


def test_periodo_uf():
    assert d.periodo_uf(D(2026, 10, 9)) == (D(2026, 9, 9), D(2026, 10, 9))
    assert d.periodo_uf(D(2026, 10, 10)) == (D(2026, 10, 9), D(2026, 11, 9))
    assert d.periodo_uf(D(2026, 1, 5)) == (D(2025, 12, 9), D(2026, 1, 9))


def test_uf_contra_valor_publicado():
    """UF del 9-10-2026 ($41.130,94) reajustada por el IPC de septiembre (+0,4%):
    la UF del 9-11-2026 publicada fue $41.295,46."""
    assert d.uf_segun_metodologia(D(2026, 11, 9), 41130.94, 0.004) == 41295.46
    assert d.uf_segun_metodologia(D(2026, 10, 12), 41130.94, 0.004) == 41146.83


def test_extender_uf_hasta_el_9_del_mes_siguiente(datos_demo):
    assert max(datos_demo.uf) == D(2026, 10, 12)
    assert max(datos_demo.uf_calculada) == D(2026, 11, 9)
    assert datos_demo.uf_dia(D(2026, 11, 9)) is not None
    assert datos_demo.uf_dia(D(2026, 11, 10)) is None  # falta el IPC de octubre


def test_metodologia_consistente_con_demo(datos_demo):
    comparadas, diferencias = d.comparar_uf_con_metodologia(datos_demo.uf, datos_demo.ipc)
    assert comparadas > 1000
    assert diferencias == []


def test_uf_proyectada_sin_inflacion_es_constante():
    assert d.uf_proyectada(D(2026, 11, 9), 41000.0, 0.0, D(2027, 6, 30)) == 41000.0


def test_uf_proyectada_usa_la_mecanica_oficial():
    mensual = (1.04) ** (1 / 12) - 1
    un_mes = d.uf_proyectada(D(2026, 11, 9), 41000.0, 0.04, D(2026, 12, 9))
    assert un_mes == round(41000 * (1 + mensual), 2)
    doce = d.uf_proyectada(D(2026, 11, 9), 41000.0, 0.04, D(2027, 11, 9))
    assert doce == pytest.approx(41000 * 1.04, abs=0.5)


def test_utm_metodologia():
    assert d.utm_segun_metodologia(71721, 0.006, False) == round(71721 * 1.006)
    assert d.utm_segun_metodologia(64666, -0.005, False) == round(64666 * 0.995)
    assert d.utm_segun_metodologia(64666, -0.005, True) == 64666


def test_frescura_demo(datos_demo):
    errores, advertencias = d.revisar_frescura(datos_demo, D(2026, 10, 12))
    assert errores == []
    errores, _ = d.revisar_frescura(datos_demo, D(2026, 11, 20))
    assert errores  # la UF del 20 de noviembre todavía no se conoce


# --- Validaciones con datos reales (solo corren si existe data/, p. ej. en GitHub Actions) ---

@pytest.mark.skipif(not hay_datos_reales(), reason="sin datos reales descargados")
def test_uf_contra_datos_reales():
    reales = d.cargar_datos(DATOS_REALES)
    comparadas, diferencias = d.comparar_uf_con_metodologia(reales.uf, reales.ipc)
    print(f"UF: {comparadas} valores comparados, {len(diferencias)} diferencias")
    for fecha, oficial, calculado in diferencias[:20]:
        print(f"  {fecha}: oficial {oficial} vs calculado {calculado}")
    assert comparadas > 300
    assert len(diferencias) <= comparadas * 0.001


@pytest.mark.skipif(not hay_datos_reales(), reason="sin datos reales descargados")
def test_utm_contra_datos_reales():
    reales = d.cargar_datos(DATOS_REALES)
    resultados = {}
    for mantener in (False, True):
        comparadas, diferencias = d.comparar_utm_con_metodologia(reales.utm, reales.ipc, mantener)
        resultados[mantener] = diferencias
        print(f"UTM (mantener con IPC negativo={mantener}): {comparadas} meses, {len(diferencias)} diferencias")
        for mes, oficial, calculado in diferencias[:10]:
            print(f"  {mes}: oficial {oficial} vs calculado {calculado}")
    configurado = cargar_parametros().get("utm_se_mantiene_con_ipc_negativo")
    assert resultados[configurado] == [], "Revisa utm_se_mantiene_con_ipc_negativo en parametros/chile.yaml"


# --- Descarga (con la red simulada) ---

def test_numero_chileno():
    assert fuentes.numero_chileno("39.485,65") == 39485.65
    assert fuentes.numero_chileno("0,4") == 0.4


def test_filtra_valores_fuera_de_rango():
    validos, descartados = fuentes.filtrar_valores_validos("dolar", {D(2026, 1, 1): 950.0, D(2026, 1, 2): 0.0})
    assert list(validos) == [D(2026, 1, 1)]
    assert len(descartados) == 1


def test_oculta_claves_en_errores():
    assert "secreta" not in fuentes._ocultar_claves("https://x/uf/2026?apikey=secreta&formato=json")


def test_serie_mindicador(monkeypatch):
    respuesta = {"serie": [{"fecha": "2026-10-12T03:00:00.000Z", "valor": 41146.83},
                           {"fecha": "2026-06-15T04:00:00.000Z", "valor": 40000.5}]}
    monkeypatch.setattr(fuentes, "descargar_json", lambda url: respuesta)
    assert fuentes.serie_mindicador("uf", 2026) == {D(2026, 10, 12): 41146.83, D(2026, 6, 15): 40000.5}


def test_actualizar_fusiona_y_escribe(tmp_path, monkeypatch):
    def falsa_serie(indicador, anio, *_):
        valores = {"uf": 41000.0, "dolar": 950.0, "euro": 1100.0, "utm": 72000.0, "ipc": 0.4}
        return {D(anio, 3, 1): valores[indicador], D(anio, 3, 2): valores[indicador] + 1}, "prueba"

    monkeypatch.setattr(fuentes, "obtener_serie", falsa_serie)
    monkeypatch.setattr(fuentes, "ultimos_indicadores", lambda **_: {"tpm": {"valor": 4.5}})
    resumen = fuentes.actualizar(tmp_path, anio_inicio=2025, hoy=D(2026, 10, 12), pausa=0)
    assert resumen["series"]["uf"]["total"] == 4      # 2 días × 2 años
    assert resumen["series"]["utm"]["total"] == 2     # series mensuales: un valor por mes
    uf = json.loads((tmp_path / "series" / "uf.json").read_text())
    assert uf["2026-03-01"] == 41000.0
    meta = json.loads((tmp_path / "meta.json").read_text())
    assert "actualizado" in meta and "demo" not in meta
    # Segunda pasada: solo descarga el año en curso y no duplica
    resumen = fuentes.actualizar(tmp_path, anio_inicio=2025, hoy=D(2026, 10, 12), pausa=0)
    assert resumen["series"]["uf"]["total"] == 4
    assert resumen["series"]["uf"]["cambios"] == 0


def test_actualizar_deja_de_insistir_si_la_fuente_esta_caida(tmp_path, monkeypatch):
    llamadas = []

    def caida(indicador, anio, *_):
        llamadas.append((indicador, anio))
        raise fuentes.ErrorDescarga("sin respuesta")

    monkeypatch.setattr(fuentes, "obtener_serie", caida)
    monkeypatch.setattr(fuentes, "ultimos_indicadores", lambda **_: {})
    resumen = fuentes.actualizar(tmp_path, anio_inicio=2018, hoy=D(2026, 10, 12), pausa=0)
    # Por cada indicador se intentan solo los años más recientes antes de rendirse
    assert len(llamadas) == fuentes.MAX_FALLAS_SEGUIDAS * 5
    assert llamadas[0] == ("uf", 2026)
    assert all(info["total"] == 0 for info in resumen["series"].values())


# --- Respaldo SII (HTML simulado con la estructura de sus tablas) ---

HTML_UF = """
<table id="table_export"><thead><tr><th>Día</th><th>Ene</th><th>Feb</th><th>Mar</th></tr></thead>
<tbody>
<tr><th>1</th><td>39.727,06</td><td>39.800,12</td><td>&nbsp;</td></tr>
<tr><th>31</th><td>39.900,00</td><td></td><td>40.001,50</td></tr>
</tbody></table>
"""

# Estructura real de sii.cl/valores_y_fechas/utm/utm2026.htm (encabezado en dos filas)
HTML_UTM = """
<table>
<tr><th rowspan="2">2026</th><th rowspan="2">UTM (1)</th><th rowspan="2">UTA (2)</th>
    <th>Indice de Precios al Consumidor</th><th colspan="3">Variación Porcentual</th></tr>
<tr><th>Valor en puntos (6)</th><th>Mensual (3)</th><th>Acumulado 2026 (4)</th><th>Ultimos 12 meses (5)</th></tr>
<tr><td>Enero</td><td>69.751</td><td>837.012</td><td>109,71</td><td>0,4</td><td>0,4</td><td>2,8</td></tr>
<tr><td>Febrero</td><td>69.960</td><td>839.520</td><td>109,60</td><td>-0,1</td><td>0,3</td><td>2,6</td></tr>
<tr><td>Noviembre</td><td>72.440</td><td>869.280</td><td></td><td></td><td></td><td></td></tr>
<tr><td>Diciembre</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</table>
"""

# Estructura real de las tablas por mes de sii.cl (UF y dólar)
HTML_MES = """
<table><tr><th colspan="6">Octubre</th></tr>
<tr><th>1</th><td>41.065,38</td><th>11</th><td>41.141,53</td><th>21</th><td>41.194,55</td></tr>
<tr><th>2</th><td>41.073,57</td><th>12</th><td>41.146,83</td><th>22</th><td></td></tr>
</table>
"""


def test_lee_grilla_diaria_del_sii():
    serie = fuentes.serie_diaria_sii(HTML_UF, 2026)
    assert serie == {D(2026, 1, 1): 39727.06, D(2026, 2, 1): 39800.12,
                     D(2026, 1, 31): 39900.0, D(2026, 3, 31): 40001.5}


def test_lee_tabla_por_mes_del_sii():
    serie = fuentes.serie_diaria_sii(HTML_MES, 2026)
    assert serie == {D(2026, 10, 1): 41065.38, D(2026, 10, 11): 41141.53, D(2026, 10, 21): 41194.55,
                     D(2026, 10, 2): 41073.57, D(2026, 10, 12): 41146.83}


def test_lee_tabla_de_utm_e_ipc_del_sii():
    assert fuentes.serie_mensual_sii(HTML_UTM, 2026, "utm") == {
        D(2026, 1, 1): 69751.0, D(2026, 2, 1): 69960.0, D(2026, 11, 1): 72440.0}
    assert fuentes.serie_mensual_sii(HTML_UTM, 2026, "ipc") == {D(2026, 1, 1): 0.4, D(2026, 2, 1): -0.1}


def test_detecta_cambio_de_formato_en_la_tabla_de_utm():
    roto = HTML_UTM.replace("837.012", "1.234")
    with pytest.raises(fuentes.ErrorDescarga):
        fuentes.serie_mensual_sii(roto, 2026, "utm")


def test_el_sii_es_la_fuente_principal(monkeypatch):
    monkeypatch.setattr(fuentes, "descargar_texto", lambda url, **_: HTML_UF)
    monkeypatch.setattr(fuentes, "serie_mindicador", lambda *_, **__: pytest.fail("no debería consultarse"))
    serie, fuente = fuentes.obtener_serie("uf", 2026, set())
    assert fuente == "sii.cl" and serie[D(2026, 1, 1)] == 39727.06


def test_si_el_sii_falla_usa_mindicador(monkeypatch):
    def sii_caido(url, **_):
        raise fuentes.ErrorDescarga(f"No se pudo descargar {url}: timeout")

    monkeypatch.delenv("CMF_API_KEY", raising=False)
    monkeypatch.setattr(fuentes, "descargar_texto", sii_caido)
    monkeypatch.setattr(fuentes, "serie_mindicador", lambda *_, **__: {D(2026, 1, 1): 39731.79})
    caidas = set()
    serie, fuente = fuentes.obtener_serie("uf", 2026, caidas)
    assert fuente == "mindicador.cl" and caidas == {"sii.cl"}


def test_euro_sin_mindicador_ni_cmf_no_tiene_fuente(monkeypatch):
    monkeypatch.delenv("CMF_API_KEY", raising=False)
    with pytest.raises(fuentes.SinFuente):
        fuentes.obtener_serie("euro", 2026, {"mindicador.cl"})


def test_indicador_sin_fuente_no_corta_la_descarga(tmp_path, monkeypatch):
    """Sin mindicador ni CMF, el euro no tiene fuente: eso no debe detener la UTM ni el IPC."""
    def obtener(indicador, anio, caidas=None):
        if indicador == "euro":
            raise fuentes.SinFuente("Ninguna fuente disponible publica euro")
        return {D(anio, 1, 1): {"uf": 41000.0, "dolar": 950.0, "utm": 72000.0, "ipc": 0.3}[indicador]}, "sii.cl"

    monkeypatch.setattr(fuentes, "obtener_serie", obtener)
    monkeypatch.setattr(fuentes, "ultimos_indicadores", lambda **_: {})
    resumen = fuentes.actualizar(tmp_path, anio_inicio=2018, hoy=D(2026, 10, 12), pausa=0)
    assert resumen["series"]["euro"]["total"] == 0
    assert resumen["series"]["utm"]["total"] == 9 and resumen["series"]["ipc"]["total"] == 9
