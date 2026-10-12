"""Verifica que estaticos/js/calculos.js (navegador) y lucas/calculos.py den lo mismo.

Requiere Node.js; si no está instalado, el test se omite (en GitHub Actions sí corre).
"""

from __future__ import annotations

import datetime as dt
import json
import math
import shutil
import subprocess

import pytest

from lucas import calculos as c
from lucas.config import cargar_parametros
from lucas.feriados import dias_habiles_entre, feriados_nacionales

from .conftest import RAIZ

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js no está instalado")

PROGRAMA = r"""
const L = require(process.argv[1]);
let entrada = '';
process.stdin.on('data', d => entrada += d);
process.stdin.on('end', () => {
  const casos = JSON.parse(entrada);
  const salida = casos.map(caso => L[caso.fn].apply(null, caso.args));
  process.stdout.write(JSON.stringify(salida));
});
"""


def ejecutar_js(casos: list[dict]) -> list:
    resultado = subprocess.run(
        [NODE, "-e", PROGRAMA, str(RAIZ / "estaticos" / "js" / "calculos.js")],
        input=json.dumps(casos), capture_output=True, text=True, check=True, timeout=60)
    return json.loads(resultado.stdout)


def iguales(py, js, ruta="") -> list[str]:
    """Compara recursivamente; los números deben coincidir exactamente o casi (1e-9 relativo)."""
    if isinstance(py, dict):
        errores = []
        for clave, valor in py.items():
            if clave not in js:
                errores.append(f"{ruta}.{clave} falta en JS")
            else:
                errores += iguales(valor, js[clave], f"{ruta}.{clave}")
        return errores
    if isinstance(py, list):
        if len(py) != len(js):
            return [f"{ruta}: largo {len(py)} vs {len(js)}"]
        return [e for i, (a, b) in enumerate(zip(py, js)) for e in iguales(a, b, f"{ruta}[{i}]")]
    if isinstance(py, bool) or py is None or isinstance(py, str):
        return [] if py == js else [f"{ruta}: {py!r} vs {js!r}"]
    if math.isclose(float(py), float(js), rel_tol=1e-9, abs_tol=1e-9):
        return []
    return [f"{ruta}: {py!r} (Python) vs {js!r} (JS)"]


@pytest.fixture(scope="module")
def p():
    return c.contexto_parametros(dt.date(2026, 10, 12), 41146.83, 72151, cargar_parametros())


def test_sueldo_liquido_identico(p):
    casos, esperados = [], []
    opciones = [
        {},
        {"afp": "provida"},
        {"afp": "modelo", "contrato": "plazo_fijo"},
        {"afp": "capital", "salud": "isapre", "plan_isapre_uf": 4.3},
        {"afp": "habitat", "no_imponible": 75_000, "apv": 150_000},
        {"afp": "planvital", "contrato": "indefinido_11", "salud": "isapre", "plan_isapre_uf": 0.5},
    ]
    for bruto in (0, 1, 553_553, 999_999, 1_234_567, 2_000_000, 3_703_215, 5_550_000, 9_876_543, 25_000_000):
        for opcion in opciones:
            casos.append({"fn": "sueldoLiquido", "args": [bruto, p, opcion]})
            esperados.append(c.sueldo_liquido(bruto, p, **opcion))
    for liquido in (400_000, 1_000_000, 2_500_000):
        for opcion in opciones[:3]:
            casos.append({"fn": "brutoParaLiquido", "args": [liquido, p, opcion]})
            esperados.append(c.bruto_para_liquido(liquido, p, **opcion))
    errores = [e for py, js in zip(esperados, ejecutar_js(casos)) for e in iguales(py, js)]
    assert errores == []


def test_otras_calculadoras_identicas(p):
    casos = [
        ("impuestoUnico", [1_229_100, p], c.impuesto_unico(1_229_100, p)),
        ("impuestoUnico", [30_000_000, p], c.impuesto_unico(30_000_000, p)),
        ("gratificacionLegal", [700_000, p], c.gratificacion_legal(700_000, p)),
        ("gratificacionLegal", [2_500_000, p], c.gratificacion_legal(2_500_000, p)),
        ("costoEmpleador", [1_500_000, p, "plazo_fijo", 50_000], c.costo_empleador(1_500_000, p, "plazo_fijo", 50_000)),
        ("honorariosDesdeBruto", [333_333, p], c.honorarios_desde_bruto(333_333, p)),
        ("honorariosDesdeLiquido", [654_321, p], c.honorarios_desde_liquido(654_321, p)),
        ("dividendo", [2400, 0.042, 25], c.dividendo(2400, 0.042, 25)),
        ("simularHipotecario", [4500, 0.1, 0.0455, 30, p, 0.6], c.simular_hipotecario(4500, 0.1, 0.0455, 30, p, 0.6)),
        ("saldosAnuales", [2400, 0.042, 20], c.saldos_anuales(2400, 0.042, 20)),
        ("variacionAcumulada", [[0.004, -0.001, 0.007]], c.variacion_acumulada([0.004, -0.001, 0.007])),
        ("reajustarPorIpc", [480_000, [0.004, 0.003, 0.002]], c.reajustar_por_ipc(480_000, [0.004, 0.003, 0.002])),
        ("proyectarAhorro", [1_000_000, 150_000, 0.06, 15], c.proyectar_ahorro(1_000_000, 150_000, 0.06, 15)),
        ("afpMasBarata", [p], c.afp_mas_barata(p)),
    ]
    resultados = ejecutar_js([{"fn": fn, "args": args} for fn, args, _ in casos])
    errores = [f"{fn}: {e}" for (fn, _, py), js in zip(casos, resultados) for e in iguales(py, js)]
    assert errores == []


def test_dias_habiles_identicos():
    extras = cargar_parametros().feriados_extra()
    feriados = [f.fecha.isoformat() for anio in (2025, 2026, 2027) for f in feriados_nacionales(anio, extras)]
    rangos = [("2026-10-01", "2026-10-31"), ("2025-12-20", "2026-01-10"), ("2026-09-01", "2027-03-31")]
    casos = [{"fn": "contarDiasHabiles", "args": [a, b, feriados, False, True]} for a, b in rangos]
    resultados = ejecutar_js(casos)
    for (a, b), js in zip(rangos, resultados):
        esperado = dias_habiles_entre(dt.date.fromisoformat(a), dt.date.fromisoformat(b), extras)
        assert js["dias"] == esperado, (a, b)
    suma = ejecutar_js([{"fn": "sumarDiasHabiles", "args": ["2026-10-09", 1, feriados, False]}])[0]
    assert suma["fecha"] == "2026-10-13"  # el lunes 12 es feriado
