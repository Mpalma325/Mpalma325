"""Configuración compartida de los tests."""

from __future__ import annotations

import datetime as dt
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from lucas.calculos import contexto_parametros  # noqa: E402
from lucas.config import cargar_parametros  # noqa: E402
from lucas.datos import cargar_datos  # noqa: E402

DEMO = RAIZ / "tests" / "fixtures" / "datos_demo"
DATOS_REALES = RAIZ / "data"
HOY = dt.date(2026, 10, 12)

# Valores reales verificados (fuentes en parametros/chile.yaml y docs/MANTENCION.md):
# UTM de octubre de 2026 (SII, Circular 37/2026) y UF del 12-10-2026, calculada desde
# la UF del 9-10-2026 ($41.130,94) con el IPC de septiembre de 2026 (+0,4%).
UTM_OCTUBRE_2026 = 72151.0
UF_12_OCTUBRE_2026 = 41146.83


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """Ninguna prueba debe depender de internet: las descargas se simulan."""
    def bloqueado(*_, **__):
        raise urllib.error.URLError("red deshabilitada durante las pruebas")

    monkeypatch.setattr(urllib.request, "urlopen", bloqueado)


@pytest.fixture(scope="session")
def params():
    return cargar_parametros()


@pytest.fixture(scope="session")
def p(params):
    """Parámetros vigentes al 12 de octubre de 2026 con UF y UTM reales."""
    return contexto_parametros(HOY, UF_12_OCTUBRE_2026, UTM_OCTUBRE_2026, params)


@pytest.fixture(scope="session")
def datos_demo():
    return cargar_datos(DEMO, mantener_utm_si_ipc_negativo=False)


def hay_datos_reales() -> bool:
    return (DATOS_REALES / "series" / "uf.json").exists()
