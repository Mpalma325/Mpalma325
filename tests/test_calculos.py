import pytest

from lucas import calculos as c
from lucas.paginas import tabla_impuesto_pesos

from .conftest import UF_12_OCTUBRE_2026, UTM_OCTUBRE_2026


# --- Impuesto único ---------------------------------------------------------

def test_tabla_impuesto_coincide_con_sii_octubre_2026(p):
    """Tabla publicada por el SII para octubre de 2026 (UTM $72.151)."""
    filas = tabla_impuesto_pesos(p, UTM_OCTUBRE_2026)
    assert round(filas[0]["hasta"], 2) == 974038.50  # tramo exento: 13,5 UTM
    rebajas_sii = [0, 38961.54, 125542.74, 323957.99, 803762.14, 1284287.80, 1682561.32, 2800901.82]
    assert [round(f["rebaja"], 2) for f in filas] == rebajas_sii
    assert filas[-1]["hasta"] is None


def test_impuesto_exento_y_continuo_en_los_bordes(p):
    assert c.impuesto_unico(974038, p)["impuesto"] == 0
    for tramo in p["tramos_impuesto"][:-1]:
        borde = tramo["hasta"] * p["utm"]
        abajo = c.impuesto_unico(borde - 1, p)["impuesto"]
        arriba = c.impuesto_unico(borde + 1, p)["impuesto"]
        assert 0 <= arriba - abajo <= 2, borde  # la tabla es continua


def test_impuesto_caso_conocido(p):
    # Base de $1.229.100 cae en el tramo de 4%: 1.229.100 × 0,04 − 0,54 × 72.151 = 10.202,46
    r = c.impuesto_unico(1_229_100, p)
    assert r["impuesto"] == 10202
    assert r["tramo"] == 1


# --- Sueldo líquido ---------------------------------------------------------

def test_sueldo_un_millon(p):
    r = c.sueldo_liquido(1_000_000, p, afp="uno")
    assert r["afp"] == 104_600       # 10,46%
    assert r["salud"] == 70_000      # 7%
    assert r["cesantia"] == 6_000    # 0,6%
    assert r["impuesto"] == 0        # base 819.400 < 974.038,5
    assert r["liquido"] == 819_400


def test_sueldo_con_impuesto(p):
    r = c.sueldo_liquido(1_500_000, p, afp="uno")
    assert (r["afp"], r["salud"], r["cesantia"]) == (156_900, 105_000, 9_000)
    assert r["base_tributable"] == 1_229_100
    assert r["impuesto"] == 10_202
    assert r["liquido"] == 1_218_898


def test_tope_imponible(p):
    tope = 90 * UF_12_OCTUBRE_2026
    r = c.sueldo_liquido(5_000_000, p, afp="uno")
    assert r["tope_aplicado"]
    assert r["imponible"] == pytest.approx(tope)
    assert r["afp"] == round(tope * 0.1046)
    assert r["salud"] == round(tope * 0.07)
    assert r["cesantia"] == 30_000  # bajo el tope de cesantía (135,2 UF)
    # La renta sobre el tope sí paga impuesto
    assert r["base_tributable"] == 5_000_000 - r["afp"] - r["salud"] - r["cesantia"]


def test_plazo_fijo_no_paga_cesantia(p):
    assert c.sueldo_liquido(1_000_000, p, contrato="plazo_fijo")["cesantia"] == 0
    assert c.sueldo_liquido(1_000_000, p, contrato="indefinido_11")["cesantia"] == 0


def test_isapre_cobra_el_plan_pero_solo_rebaja_el_7(p):
    fonasa = c.sueldo_liquido(2_000_000, p, afp="modelo")
    isapre = c.sueldo_liquido(2_000_000, p, afp="modelo", salud="isapre", plan_isapre_uf=5)
    plan = round(5 * UF_12_OCTUBRE_2026)
    assert isapre["salud"] == plan
    assert isapre["salud_adicional"] == plan - 140_000
    assert isapre["base_tributable"] == fonasa["base_tributable"]
    # Plan más barato que el 7%: igual se descuenta el 7%
    barato = c.sueldo_liquido(2_000_000, p, salud="isapre", plan_isapre_uf=1)
    assert barato["salud"] == 140_000


def test_apv_rebaja_impuesto(p):
    sin = c.sueldo_liquido(3_000_000, p)
    con = c.sueldo_liquido(3_000_000, p, apv=200_000)
    assert con["base_tributable"] == sin["base_tributable"] - 200_000
    assert con["impuesto"] < sin["impuesto"]
    assert con["liquido"] == pytest.approx(sin["liquido"] - 200_000 + (sin["impuesto"] - con["impuesto"]))


def test_no_imponible_suma_al_liquido(p):
    base = c.sueldo_liquido(1_000_000, p)
    con = c.sueldo_liquido(1_000_000, p, no_imponible=80_000)
    assert con["liquido"] == base["liquido"] + 80_000


@pytest.mark.parametrize("objetivo", [450_000, 800_000, 1_000_000, 1_234_567, 3_000_000, 9_000_000])
def test_bruto_para_liquido_es_el_inverso(p, objetivo):
    r = c.bruto_para_liquido(objetivo, p, afp="habitat")
    assert r["liquido"] >= objetivo
    assert c.sueldo_liquido(r["bruto"] - 1, p, afp="habitat")["liquido"] < objetivo


def test_afp_mas_barata(p):
    assert c.afp_mas_barata(p) == "uno"


def test_gratificacion_legal(p):
    tope = 4.75 * 553_553 / 12  # IMM desde el 1 de mayo de 2026
    assert c.gratificacion_legal(500_000, p) == 125_000
    assert c.gratificacion_legal(2_000_000, p) == round(tope)


def test_costo_empleador_con_reforma(p):
    r = c.costo_empleador(1_000_000, p)
    assert r["reforma"] == 35_000   # 3,5% desde agosto de 2026 (incluye el SIS)
    assert r["sis"] == 0
    assert r["cesantia"] == 24_000
    assert r["mutual"] == 9_300
    assert r["costo_total"] == 1_068_300


# --- Honorarios ---------------------------------------------------------------

def test_honorarios_2026(p):
    r = c.honorarios_desde_bruto(1_000_000, p)
    assert (r["retencion"], r["liquido"]) == (152_500, 847_500)
    assert c.honorarios_desde_liquido(847_500, p)["bruto"] == 1_000_000


@pytest.mark.parametrize("liquido", [1, 999, 84_750, 123_457, 500_000, 2_345_678])
def test_honorarios_inverso(p, liquido):
    r = c.honorarios_desde_liquido(liquido, p)
    assert r["liquido"] >= liquido
    anterior = c.honorarios_desde_bruto(r["bruto"] - 1, p)
    assert anterior["liquido"] < liquido


def test_retencion_por_anio(params):
    import datetime as dt
    tasas = {anio: params.vigente("retencion_honorarios", dt.date(anio, 6, 1))["tasa"]
             for anio in (2025, 2026, 2027, 2028)}
    assert tasas == {2025: 0.145, 2026: 0.1525, 2027: 0.16, 2028: 0.17}


# --- Crédito hipotecario, IPC y ahorro --------------------------------------------

def test_dividendo_formula():
    assert c.dividendo(1200, 0, 10) == pytest.approx(10)
    cuota = c.dividendo(2400, 0.042, 25)
    assert cuota == pytest.approx(12.9346, abs=1e-4)
    saldos = c.saldos_anuales(2400, 0.042, 25)
    assert len(saldos) == 25
    assert saldos[-1]["saldo"] == pytest.approx(0, abs=1e-6)
    assert sum(s["amortizacion"] for s in saldos) == pytest.approx(2400)


def test_simular_hipotecario(p):
    r = c.simular_hipotecario(3000, 0.2, 0.042, 25, p)
    assert r["pie_uf"] == pytest.approx(600)
    assert r["credito_uf"] == pytest.approx(2400)
    assert r["dividendo_pesos"] == round(r["dividendo_uf"] * UF_12_OCTUBRE_2026)
    assert r["renta_minima"] == round(r["dividendo_pesos"] / 0.25)


def test_ipc_acumulado():
    assert c.variacion_acumulada([0.01, 0.02]) == pytest.approx(0.0302)
    r = c.reajustar_por_ipc(500_000, [0.004, 0.003, -0.001])
    assert r["nuevo_monto"] == round(500_000 * 1.004 * 1.003 * 0.999)


def test_ahorro():
    sin_interes = c.proyectar_ahorro(1_000_000, 100_000, 0, 10)
    assert sin_interes["saldo"] == pytest.approx(13_000_000)
    con_interes = c.proyectar_ahorro(0, 100_000, 0.05, 20)
    assert con_interes["saldo"] > con_interes["aportado"] == pytest.approx(24_000_000)
    assert len(con_interes["serie"]) == 21


# --- Finiquito y vacaciones ------------------------------------------------------

def _feriados():
    import datetime as dt
    from lucas.config import cargar_parametros
    from lucas.feriados import feriados_nacionales
    extras = cargar_parametros().feriados_extra()
    return {f.fecha for anio in (2025, 2026, 2027) for f in feriados_nacionales(anio, extras)}


def test_tiempo_trabajado_y_anios_de_servicio(p):
    import datetime as dt
    D = dt.date
    assert c.tiempo_trabajado(D(2023, 3, 15), D(2026, 10, 12)) == {
        "anios": 3, "meses": 6, "dias": 28, "meses_totales": 42}
    assert c.anios_de_servicio(D(2023, 3, 15), D(2026, 10, 12), p) == 4   # fracción > 6 meses
    assert c.anios_de_servicio(D(2023, 3, 15), D(2026, 9, 14), p) == 3    # justo 3 años y 6 meses
    assert c.anios_de_servicio(D(2026, 1, 1), D(2026, 10, 12), p) == 0    # menos de un año
    assert c.anios_de_servicio(D(2000, 1, 1), D(2026, 10, 12), p) == 11   # tope de 11 años
    assert c.sumar_meses(D(2026, 1, 31), 1) == D(2026, 2, 28)


def test_feriado_proporcional_en_dias_corridos(p):
    import datetime as dt
    D = dt.date
    proporcional = c.feriado_proporcional(D(2023, 3, 15), D(2026, 10, 12), p)
    assert proporcional["desde"] == D(2026, 3, 15)
    assert (proporcional["meses"], proporcional["dias"]) == (6, 28)
    assert proporcional["dias_habiles"] == pytest.approx(1.25 * 6 + 1.25 / 30 * 28)
    # 13 días hábiles desde el martes 13 de octubre de 2026: terminan el jueves 29,
    # con dos fines de semana entre medio (4 días inhábiles).
    conversion = c.dias_corridos_de_feriado(13.6667, D(2026, 10, 12), _feriados())
    assert conversion["hasta"] == D(2026, 10, 29)
    assert conversion["inhabiles"] == 4
    assert conversion["dias_corridos"] == pytest.approx(17.6667)


def test_feriado_cruza_un_feriado_legal(p):
    import datetime as dt
    # Desde el viernes 9 de octubre de 2026: el lunes 12 es feriado y se suma como inhábil.
    conversion = c.dias_corridos_de_feriado(2, dt.date(2026, 10, 9), _feriados())
    assert conversion["hasta"] == dt.date(2026, 10, 14)
    assert conversion["inhabiles"] == 3  # sábado, domingo y el feriado del lunes


def test_finiquito_por_necesidades_de_la_empresa(p):
    import datetime as dt
    r = c.finiquito(dt.date(2023, 3, 15), dt.date(2026, 10, 12), 1_200_000, "necesidades_empresa", p,
                    _feriados(), aviso_dado=False, dias_pendientes=5, dias_por_pagar=12)
    assert r["indemnizacion_anios"] == 4_800_000
    assert r["aviso_previo"] == 1_200_000
    assert r["feriado"] == round((17 + 1.25 * 6 + 1.25 / 30 * 28 + 5 - 13) * 40_000)
    assert r["remuneracion_pendiente"] == 480_000
    assert r["total"] == r["indemnizacion_anios"] + r["aviso_previo"] + r["feriado"] + 480_000


def test_finiquito_renuncia_y_tope(p):
    import datetime as dt
    renuncia = c.finiquito(dt.date(2020, 1, 1), dt.date(2026, 10, 12), 1_000_000, "renuncia", p, _feriados())
    assert renuncia["indemnizacion_anios"] == 0 and renuncia["aviso_previo"] == 0
    alto = c.finiquito(dt.date(2020, 1, 1), dt.date(2026, 10, 12), 6_000_000, "necesidades_empresa", p,
                       _feriados(), aviso_dado=True)
    tope = 90 * UF_12_OCTUBRE_2026
    assert alto["tope_aplicado"]
    assert alto["indemnizacion_anios"] == round(tope * 7)  # 6 años y 9 meses -> 7 años
    assert alto["feriado"] > 0
