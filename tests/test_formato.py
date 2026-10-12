import datetime as dt

from lucas import formato as f


def test_redondear_mitad_hacia_arriba():
    assert f.redondear(2.5) == 3  # round() de Python daría 2 (redondeo bancario)
    assert f.redondear(0.125, 2) == 0.13
    assert f.redondear(-2.5) == -3
    assert f.redondear(141234.4648) == 141234


def test_numero_y_pesos():
    assert f.numero(1234567) == "1.234.567"
    assert f.numero(1234567.891, 2) == "1.234.567,89"
    assert f.numero(999) == "999"
    assert f.numero(0) == "0"
    assert f.numero(-1500) == "-1.500"
    assert f.pesos(39485.651, 2) == "$39.485,65"
    assert f.pesos(819400) == "$819.400"
    assert f.pesos(-6000) == "-$6.000"
    assert f.pesos(None) == "—"


def test_porcentaje():
    assert f.porcentaje(0.0127, 2) == "1,27%"
    assert f.porcentaje(0.004, 1, signo=True) == "+0,4%"
    assert f.porcentaje(-0.005, 1, signo=True) == "-0,5%"
    assert f.porcentaje(0.1525, 2) == "15,25%"


def test_fechas():
    fecha = dt.date(2026, 10, 12)
    assert f.fecha_larga(fecha) == "12 de octubre de 2026"
    assert f.fecha_con_dia(fecha) == "lunes 12 de octubre de 2026"
    assert f.fecha_corta(fecha) == "12-10-2026"
    assert f.dia_mes(fecha) == "12 de octubre"
    assert f.mes_anio(2026, 10) == "octubre 2026"
    assert f.mes_de_anio(2026, 9) == "septiembre de 2026"
    assert f.dia_semana(dt.date(2026, 10, 18)) == "domingo"


def test_monto_corto():
    assert f.monto_corto(1_000_000) == "1 millón"
    assert f.monto_corto(1_500_000) == "1,5 millones"
    assert f.monto_corto(800_000) == "800 mil"
    assert f.monto_corto(10_000_000) == "10 millones"
