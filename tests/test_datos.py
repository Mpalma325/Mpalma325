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
    def falsa_serie(indicador, anio):
        valores = {"uf": 41000.0, "dolar": 950.0, "euro": 1100.0, "utm": 72000.0, "ipc": 0.4}
        return {D(anio, 3, 1): valores[indicador], D(anio, 3, 2): valores[indicador] + 1}, "prueba"

    monkeypatch.setattr(fuentes, "obtener_serie", falsa_serie)
    monkeypatch.setattr(fuentes, "ultimos_indicadores", lambda: {"tpm": {"valor": 4.5}})
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
