"""Cálculos financieros y laborales de Chile.

Todas las funciones reciben ``p``: un diccionario plano con los parámetros
vigentes (UF, UTM, topes, tasas...) que arma ``contexto_parametros``. Ese mismo
diccionario se inserta como JSON en cada página y lo usa
``estaticos/js/calculos.js``, que replica estas funciones paso a paso.
``tests/test_paridad_js.py`` verifica que Python y JavaScript den lo mismo.

Si cambias una fórmula aquí, cámbiala también en calculos.js.
"""

from __future__ import annotations

import datetime as dt

from .config import Parametros
from .formato import redondear


# ---------------------------------------------------------------------------
# Parámetros vigentes
# ---------------------------------------------------------------------------

def contexto_parametros(fecha: dt.date, uf: float, utm: float, params: Parametros) -> dict:
    """Arma el diccionario de parámetros vigentes en ``fecha`` (se serializa a JSON)."""
    afp = params.vigente("afp", fecha)
    topes = params.vigente("topes_imponibles", fecha)
    imm = params.vigente("ingreso_minimo", fecha)
    impuesto = params.vigente("impuesto_unico", fecha)
    cesantia = params.vigente("seguro_cesantia", fecha)
    salud = params.vigente("salud", fecha)
    apv = params.vigente("apv", fecha)
    gratificacion = params.vigente("gratificacion", fecha)
    empleador = params.vigente("cotizaciones_empleador", fecha)
    hipotecario = params.vigente("credito_hipotecario", fecha)
    administradoras = afp["administradoras"]
    return {
        "fecha": fecha.isoformat(),
        "uf": float(uf),
        "utm": float(utm),
        "imm": float(imm["monto"]),
        "tope_imponible_uf": float(topes["afp_salud_uf"]),
        "tope_cesantia_uf": float(topes["cesantia_uf"]),
        "tasa_afp": float(afp["cotizacion_obligatoria"]),
        "comisiones_afp": {clave: float(a["comision"]) for clave, a in administradoras.items()},
        "nombres_afp": {clave: a["nombre"] for clave, a in administradoras.items()},
        "salud_obligatoria": float(salud["tasa"]),
        "cesantia_trabajador": {k: float(v) for k, v in cesantia["trabajador"].items()},
        "cesantia_empleador": {k: float(v) for k, v in cesantia["empleador"].items()},
        "tramos_impuesto": [
            {"hasta": (None if t["hasta"] is None else float(t["hasta"])),
             "factor": float(t["factor"]), "rebaja": float(t["rebaja"])}
            for t in impuesto["tramos"]
        ],
        "retencion_honorarios": float(params.vigente("retencion_honorarios", fecha)["tasa"]),
        "tope_apv_mensual_uf": float(apv["tope_mensual_uf"]),
        "gratificacion_tasa": float(gratificacion["tasa"]),
        "gratificacion_tope_imm_anual": float(gratificacion["tope_imm_anual"]),
        "sis": float(empleador["sis"]),
        "mutual_basica": float(empleador["mutual_basica"]),
        "aporte_empleador_reforma": float(empleador["aporte_reforma_pensiones"]),
        "tasa_hipotecaria_referencia": float(hipotecario["tasa_referencia"]),
        "carga_financiera_maxima": float(hipotecario["carga_financiera_maxima"]),
    }


def afp_mas_barata(p: dict) -> str:
    return min(p["comisiones_afp"], key=lambda clave: (p["comisiones_afp"][clave], clave))


# ---------------------------------------------------------------------------
# Remuneraciones
# ---------------------------------------------------------------------------

def impuesto_unico(base: float, p: dict) -> dict:
    """Impuesto Único de Segunda Categoría mensual sobre la base tributable en pesos."""
    utm = p["utm"]
    tramos = p["tramos_impuesto"]
    for indice, tramo in enumerate(tramos):
        hasta = tramo["hasta"]
        if hasta is None or base <= hasta * utm:
            impuesto = base * tramo["factor"] - tramo["rebaja"] * utm
            return {
                "impuesto": max(0.0, redondear(impuesto)),
                "tramo": indice,
                "factor": tramo["factor"],
                "rebaja": tramo["rebaja"],
            }
    raise ValueError("La tabla de impuesto único debe terminar con un tramo sin tope (hasta: null)")


def gratificacion_legal(sueldo_base: float, p: dict) -> float:
    """Gratificación legal mensual (art. 50 del Código del Trabajo): 25% con tope de 4,75 IMM al año."""
    tope = p["gratificacion_tope_imm_anual"] * p["imm"] / 12
    return redondear(min(sueldo_base * p["gratificacion_tasa"], tope))


def sueldo_liquido(bruto: float, p: dict, afp: str = "uno", salud: str = "fonasa",
                   plan_isapre_uf: float = 0.0, contrato: str = "indefinido",
                   no_imponible: float = 0.0, apv: float = 0.0) -> dict:
    """Sueldo líquido de un trabajador dependiente a partir de su sueldo bruto imponible.

    - ``bruto``: total de haberes imponibles del mes (sueldo base + gratificación + bonos imponibles).
    - ``no_imponible``: colación, movilización y otras asignaciones no imponibles.
    - ``apv``: ahorro previsional voluntario mensual régimen B (rebaja la base del impuesto).
    """
    uf = p["uf"]
    tope_afp = p["tope_imponible_uf"] * uf
    tope_afc = p["tope_cesantia_uf"] * uf
    imponible = min(bruto, tope_afp)
    imponible_afc = min(bruto, tope_afc)

    tasa_afp = p["tasa_afp"] + p["comisiones_afp"][afp]
    descuento_afp = redondear(imponible * tasa_afp)
    salud_legal = redondear(imponible * p["salud_obligatoria"])
    if salud == "isapre":
        descuento_salud = max(salud_legal, redondear(plan_isapre_uf * uf))
    else:
        descuento_salud = salud_legal
    descuento_afc = redondear(imponible_afc * p["cesantia_trabajador"][contrato])

    # Para el impuesto se rebajan las cotizaciones obligatorias: AFP, el 7% de
    # salud (lo que exceda del 7% en un plan de isapre no se rebaja), el seguro
    # de cesantía y el APV régimen B hasta su tope mensual.
    apv_rebajable = min(apv, redondear(p["tope_apv_mensual_uf"] * uf))
    base_tributable = max(0.0, bruto - descuento_afp - salud_legal - descuento_afc - apv_rebajable)
    impuesto = impuesto_unico(base_tributable, p)

    total_descuentos = descuento_afp + descuento_salud + descuento_afc + impuesto["impuesto"] + apv
    return {
        "bruto": bruto,
        "no_imponible": no_imponible,
        "imponible": imponible,
        "tope_aplicado": bruto > tope_afp,
        "afp": descuento_afp,
        "tasa_afp_total": tasa_afp,
        "salud": descuento_salud,
        "salud_adicional": descuento_salud - salud_legal,
        "cesantia": descuento_afc,
        "apv": apv,
        "base_tributable": base_tributable,
        "impuesto": impuesto["impuesto"],
        "tramo": impuesto["tramo"],
        "tasa_marginal": impuesto["factor"],
        "total_descuentos": total_descuentos,
        "liquido": bruto + no_imponible - total_descuentos,
    }


def bruto_para_liquido(liquido_objetivo: float, p: dict, **opciones) -> dict:
    """Menor sueldo bruto (en pesos enteros) cuyo líquido alcanza ``liquido_objetivo``."""
    bajo, alto = 0, 1000
    while sueldo_liquido(alto, p, **opciones)["liquido"] < liquido_objetivo:
        bajo, alto = alto, alto * 2
    while alto - bajo > 1:
        medio = (bajo + alto) // 2
        if sueldo_liquido(medio, p, **opciones)["liquido"] >= liquido_objetivo:
            alto = medio
        else:
            bajo = medio
    return sueldo_liquido(alto, p, **opciones)


def costo_empleador(bruto: float, p: dict, contrato: str = "indefinido", no_imponible: float = 0.0) -> dict:
    """Costo mensual aproximado para el empleador (sin mutual adicional por riesgo)."""
    uf = p["uf"]
    imponible = min(bruto, p["tope_imponible_uf"] * uf)
    imponible_afc = min(bruto, p["tope_cesantia_uf"] * uf)
    sis = redondear(imponible * p["sis"])
    cesantia = redondear(imponible_afc * p["cesantia_empleador"][contrato])
    mutual = redondear(imponible * p["mutual_basica"])
    reforma = redondear(imponible * p["aporte_empleador_reforma"])
    total = sis + cesantia + mutual + reforma
    return {
        "sis": sis,
        "cesantia": cesantia,
        "mutual": mutual,
        "reforma": reforma,
        "total_cotizaciones": total,
        "costo_total": bruto + no_imponible + total,
    }


# ---------------------------------------------------------------------------
# Boleta de honorarios
# ---------------------------------------------------------------------------

def honorarios_desde_bruto(bruto: float, p: dict) -> dict:
    tasa = p["retencion_honorarios"]
    retencion = redondear(bruto * tasa)
    return {"bruto": bruto, "retencion": retencion, "liquido": bruto - retencion, "tasa": tasa}


def honorarios_desde_liquido(liquido: float, p: dict) -> dict:
    """Monto bruto que hay que emitir en la boleta para recibir ``liquido``."""
    tasa = p["retencion_honorarios"]
    bruto = redondear(liquido / (1 - tasa))
    while bruto - redondear(bruto * tasa) < liquido:
        bruto += 1
    while bruto > 0 and (bruto - 1) - redondear((bruto - 1) * tasa) >= liquido:
        bruto -= 1
    return honorarios_desde_bruto(bruto, p)


# ---------------------------------------------------------------------------
# Crédito hipotecario
# ---------------------------------------------------------------------------

def dividendo(monto: float, tasa_anual: float, anios: float) -> float:
    """Cuota mensual de un crédito a tasa fija (sistema francés). Tasa mensual = tasa anual / 12."""
    n = round(anios * 12)
    r = tasa_anual / 12
    if r == 0:
        return monto / n
    return monto * r / (1 - (1 + r) ** -n)


def simular_hipotecario(valor_uf: float, pie: float, tasa_anual: float, anios: float, p: dict,
                        seguros_uf: float = 0.0) -> dict:
    """Simulación de crédito hipotecario en UF. ``pie`` es la fracción del valor (0.2 = 20%)."""
    pie_uf = valor_uf * pie
    credito_uf = valor_uf - pie_uf
    cuota_uf = dividendo(credito_uf, tasa_anual, anios)
    total_cuotas_uf = cuota_uf * round(anios * 12)
    dividendo_total_uf = cuota_uf + seguros_uf
    dividendo_pesos = redondear(dividendo_total_uf * p["uf"])
    return {
        "pie_uf": pie_uf,
        "credito_uf": credito_uf,
        "dividendo_uf": cuota_uf,
        "dividendo_total_uf": dividendo_total_uf,
        "dividendo_pesos": dividendo_pesos,
        "intereses_uf": total_cuotas_uf - credito_uf,
        "total_pagado_uf": total_cuotas_uf,
        "renta_minima": redondear(dividendo_pesos / p["carga_financiera_maxima"]),
    }


def saldos_anuales(credito: float, tasa_anual: float, anios: float) -> list[dict]:
    """Saldo adeudado, intereses y amortización de cada año del crédito."""
    n = round(anios * 12)
    r = tasa_anual / 12
    cuota = dividendo(credito, tasa_anual, anios)
    saldo = credito
    filas = []
    intereses_anio = amortizacion_anio = 0.0
    for mes in range(1, n + 1):
        interes = saldo * r
        amortizacion = cuota - interes
        saldo -= amortizacion
        intereses_anio += interes
        amortizacion_anio += amortizacion
        if mes % 12 == 0 or mes == n:
            filas.append({
                "anio": (mes + 11) // 12,
                "intereses": intereses_anio,
                "amortizacion": amortizacion_anio,
                "saldo": max(0.0, saldo),
            })
            intereses_anio = amortizacion_anio = 0.0
    return filas


# ---------------------------------------------------------------------------
# IPC, ahorro y conversiones
# ---------------------------------------------------------------------------

def variacion_acumulada(variaciones: list[float]) -> float:
    """Variación compuesta de una lista de variaciones mensuales (en fracción: 0.004 = 0,4%)."""
    factor = 1.0
    for variacion in variaciones:
        factor *= 1 + variacion
    return factor - 1


def reajustar_por_ipc(monto: float, variaciones: list[float]) -> dict:
    variacion = variacion_acumulada(variaciones)
    nuevo = redondear(monto * (1 + variacion))
    return {"variacion": variacion, "nuevo_monto": nuevo, "diferencia": nuevo - monto}


def proyectar_ahorro(inicial: float, aporte_mensual: float, tasa_anual: float, anios: float) -> dict:
    """Interés compuesto con aportes al final de cada mes. ``tasa_anual`` es efectiva anual."""
    r = (1 + tasa_anual) ** (1 / 12) - 1
    saldo = float(inicial)
    aportado = float(inicial)
    serie = [{"anio": 0, "saldo": saldo, "aportado": aportado}]
    meses = round(anios * 12)
    for mes in range(1, meses + 1):
        saldo = saldo * (1 + r) + aporte_mensual
        aportado += aporte_mensual
        if mes % 12 == 0 or mes == meses:
            serie.append({"anio": mes / 12, "saldo": saldo, "aportado": aportado})
    return {"saldo": saldo, "aportado": aportado, "ganancia": saldo - aportado, "serie": serie}


def convertir(monto: float, tasa: float, decimales: int = 0) -> float:
    return redondear(monto * tasa, decimales)
