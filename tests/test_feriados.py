"""Feriados calculados vs. listas oficiales (gob.cl / Dirección del Trabajo)."""

import datetime as dt

import pytest

from lucas.config import cargar_parametros
from lucas.feriados import (dia_de_los_pueblos_indigenas, dias_habiles_entre, domingo_de_pascua,
                            feriados_nacionales, fines_de_semana_largos, proximos_feriados)

EXTRAS = cargar_parametros().feriados_extra()


def fechas(anio):
    return [f.fecha.isoformat() for f in feriados_nacionales(anio, EXTRAS)]


def test_feriados_2025_oficiales():
    # gob.cl: 18 fechas distintas (incluye las dos vueltas presidenciales)
    assert fechas(2025) == [
        "2025-01-01", "2025-04-18", "2025-04-19", "2025-05-01", "2025-05-21", "2025-06-20",
        "2025-06-29", "2025-07-16", "2025-08-15", "2025-09-18", "2025-09-19", "2025-10-12",
        "2025-10-31", "2025-11-01", "2025-11-16", "2025-12-08", "2025-12-14", "2025-12-25",
    ]


def test_feriados_2026_oficiales():
    assert fechas(2026) == [
        "2026-01-01", "2026-04-03", "2026-04-04", "2026-05-01", "2026-05-21", "2026-06-21",
        "2026-06-29", "2026-07-16", "2026-08-15", "2026-09-18", "2026-09-19", "2026-10-12",
        "2026-10-31", "2026-11-01", "2026-12-08", "2026-12-25",
    ]
    irrenunciables = [f.fecha.isoformat() for f in feriados_nacionales(2026, EXTRAS) if f.irrenunciable]
    assert irrenunciables == ["2026-01-01", "2026-05-01", "2026-09-18", "2026-09-19", "2026-12-25"]


def test_feriados_2027():
    # 17 feriados: el 17 de septiembre por la Ley 20.983, el 28 de junio y el 11 de octubre trasladados
    assert fechas(2027) == [
        "2027-01-01", "2027-03-26", "2027-03-27", "2027-05-01", "2027-05-21", "2027-06-21",
        "2027-06-28", "2027-07-16", "2027-08-15", "2027-09-17", "2027-09-18", "2027-09-19",
        "2027-10-11", "2027-10-31", "2027-11-01", "2027-12-08", "2027-12-25",
    ]


@pytest.mark.parametrize("anio,esperado", [
    (2024, "2024-03-31"), (2025, "2025-04-20"), (2026, "2026-04-05"), (2027, "2027-03-28"),
])
def test_pascua(anio, esperado):
    assert domingo_de_pascua(anio).isoformat() == esperado


@pytest.mark.parametrize("anio,esperado", [
    (2021, "2021-06-21"), (2022, "2022-06-21"), (2023, "2023-06-21"), (2024, "2024-06-20"),
    (2025, "2025-06-20"), (2026, "2026-06-21"), (2027, "2027-06-21"),
])
def test_dia_de_los_pueblos_indigenas(anio, esperado):
    assert dia_de_los_pueblos_indigenas(anio).isoformat() == esperado


@pytest.mark.parametrize("fecha", [
    "2022-10-10",  # 12-oct-2022 cayó miércoles (Ley 19.668)
    "2023-06-26",  # 29-jun-2023 cayó jueves
    "2023-10-09",  # 12-oct-2023 cayó jueves
    "2023-10-27",  # 31-oct-2023 cayó martes (Ley 20.299)
    "2023-01-02",  # 1-ene-2023 cayó domingo (Ley 20.983)
    "2018-09-17",  # 18 y 19 de septiembre en martes y miércoles (Ley 20.215)
    "2019-09-20",  # 18 y 19 de septiembre en miércoles y jueves
    "2021-09-17",  # 18 y 19 de septiembre en sábado y domingo (Ley 20.983)
    "2029-11-02",  # 31-oct-2029 cae miércoles
])
def test_reglas_de_traslado(fecha):
    dia = dt.date.fromisoformat(fecha)
    assert fecha in fechas(dia.year)


def test_no_hay_feriado_adicional_sin_regla():
    assert "2026-09-17" not in fechas(2026)
    assert "2025-09-17" not in fechas(2025)


def test_fines_de_semana_largos_2026():
    largos = fines_de_semana_largos(2026, EXTRAS)
    inicios = [b["inicio"].isoformat() for b in largos]
    assert "2026-04-03" in inicios       # Semana Santa
    assert "2026-09-18" in inicios       # Fiestas Patrias
    assert all(b["dias"] >= 3 for b in largos)


def test_proximos_feriados():
    proximos = proximos_feriados(dt.date(2026, 10, 13), 2, EXTRAS)
    assert [f.fecha.isoformat() for f in proximos] == ["2026-10-31", "2026-11-01"]
    cruza_anio = proximos_feriados(dt.date(2026, 12, 26), 1, EXTRAS)
    assert cruza_anio[0].fecha.isoformat() == "2027-01-01"


def test_dias_habiles():
    # Octubre de 2026: 22 días de lunes a viernes, menos el feriado del lunes 12.
    assert dias_habiles_entre(dt.date(2026, 10, 1), dt.date(2026, 10, 31), EXTRAS) == 21
