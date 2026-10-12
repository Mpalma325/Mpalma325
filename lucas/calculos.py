"""Cálculos financieros y laborales de Chile.

Todas las funciones reciben ``p``: un diccionario plano con los parámetros
vigentes (UF, UTM, topes, tasas...) que arma ``contexto_parametros``. Ese mismo
diccionario se inserta como JSON en cada página y lo usa
``estaticos/js/calculos.js``, que replica estas funciones paso a paso.
``tests/test_paridad_js.py`` verifica que Python y JavaScript den lo mismo.

Si cambias una fórmula aquí, cámbiala también en calculos.js.
"""

from __future__ import annotations

import calendar
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
    indemnizaciones = params.vigente("indemnizaciones", fecha)
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
        "tope_indemnizacion_uf": float(indemnizaciones["tope_remuneracion_uf"]),
        "tope_anios_indemnizacion": int(indemnizaciones["tope_anios"]),
        "feriado_anual_habiles": float(indemnizaciones["feriado_dias_habiles_anuales"]),
        # IVA, horas extra e impuesto de timbres del crédito de consumo
        "iva": float(params.vigente("iva", fecha)["tasa"]),
        "jornada_semanal_horas": float(params.vigente("jornada_laboral", fecha)["horas_semanales"]),
        "recargo_horas_extra": float(params.vigente("jornada_laboral", fecha)["recargo_horas_extra"]),
        "timbres_tasa_mensual": float(params.vigente("impuesto_timbres", fecha)["tasa_mensual"]),
        "timbres_tope": float(params.vigente("impuesto_timbres", fecha)["tope"]),
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
# Finiquito y vacaciones proporcionales
# ---------------------------------------------------------------------------

CAUSALES_CON_INDEMNIZACION = ("necesidades_empresa", "desahucio")
# Contrato por obra o faena terminado por la conclusión de la obra (art. 159 N° 5):
# 2,5 días de remuneración por cada mes trabajado y fracción superior a 15 días, si
# el contrato duró un mes o más (art. 163, agregado por la Ley 21.122).
DIAS_POR_MES_OBRA = 2.5
UN_DIA = dt.timedelta(days=1)


def sumar_meses(fecha: dt.date, meses: int) -> dt.date:
    """Suma meses a una fecha; si el día no existe (31 de febrero) usa el último día del mes."""
    total = fecha.month - 1 + meses
    anio = fecha.year + total // 12
    mes = total % 12 + 1
    return dt.date(anio, mes, min(fecha.day, calendar.monthrange(anio, mes)[1]))


def tiempo_trabajado(inicio: dt.date, termino: dt.date) -> dict:
    """Años, meses y días entre ``inicio`` y ``termino``, ambos incluidos."""
    hasta = termino + UN_DIA
    meses = 0
    while sumar_meses(inicio, meses + 1) <= hasta:
        meses += 1
    dias = (hasta - sumar_meses(inicio, meses)).days
    return {"anios": meses // 12, "meses": meses % 12, "dias": dias, "meses_totales": meses}


def anios_de_servicio(inicio: dt.date, termino: dt.date, p: dict) -> int:
    """Años para la indemnización: cada año y fracción superior a seis meses (art. 163), con tope."""
    t = tiempo_trabajado(inicio, termino)
    if t["anios"] < 1:
        return 0
    extra = 1 if t["meses"] > 6 or (t["meses"] == 6 and t["dias"] > 0) else 0
    return min(t["anios"] + extra, p["tope_anios_indemnizacion"])


def meses_obra_o_faena(inicio: dt.date, termino: dt.date) -> int:
    """Meses para la indemnización por término de obra: cada mes y fracción superior a 15 días."""
    t = tiempo_trabajado(inicio, termino)
    if t["meses_totales"] < 1:
        return 0
    return t["meses_totales"] + (1 if t["dias"] > 15 else 0)


def feriado_proporcional(inicio: dt.date, termino: dt.date, p: dict) -> dict:
    """Días hábiles de feriado ganados desde el último aniversario del contrato (art. 73)."""
    anios = tiempo_trabajado(inicio, termino)["anios"]
    aniversario = sumar_meses(inicio, 12 * anios)
    t = tiempo_trabajado(aniversario, termino)
    por_mes = p["feriado_anual_habiles"] / 12
    return {
        "desde": aniversario,
        "meses": t["meses"],
        "dias": t["dias"],
        "dias_habiles": por_mes * t["meses"] + por_mes / 30 * t["dias"],
    }


def dias_corridos_de_feriado(dias_habiles: float, termino: dt.date, feriados: set[dt.date]) -> dict:
    """Convierte días hábiles de feriado en días corridos a pagar.

    Desde el día siguiente al término se cuentan los días hábiles (lunes a viernes
    que no sean feriado: el sábado es inhábil para el feriado, art. 69) y se suman
    los sábados, domingos y feriados que queden entre medio. La fracción de día
    se agrega al final.
    """
    enteros = int(dias_habiles)
    fraccion = dias_habiles - enteros
    dia = termino
    corridos = 0
    contados = 0
    while contados < enteros:
        dia += UN_DIA
        corridos += 1
        if dia.weekday() < 5 and dia not in feriados:
            contados += 1
    return {"dias_corridos": corridos + fraccion, "inhabiles": corridos - enteros, "hasta": dia}


def finiquito(inicio: dt.date, termino: dt.date, remuneracion: float, causal: str, p: dict,
              feriados: set[dt.date], aviso_dado: bool = True, dias_pendientes: float = 0.0,
              dias_por_pagar: float = 0.0) -> dict:
    """Montos brutos referenciales de un finiquito.

    - Indemnización por años de servicio y sustitutiva del aviso previo: solo por
      necesidades de la empresa o desahucio (art. 161), con la remuneración topada
      en 90 UF (art. 172).
    - Término de obra o faena (``termino_obra``): 2,5 días por mes trabajado, con el
      mismo tope de remuneración.
    - Feriado: días pendientes más el proporcional, pagados en días corridos.
    - Remuneración de los días trabajados del último mes que aún no se pagan.
    """
    tope = p["tope_indemnizacion_uf"] * p["uf"]
    base = min(remuneracion, tope)
    con_indemnizacion = causal in CAUSALES_CON_INDEMNIZACION
    anios = anios_de_servicio(inicio, termino, p) if con_indemnizacion else 0
    indemnizacion = redondear(base * anios)
    aviso = redondear(base) if con_indemnizacion and not aviso_dado else 0.0
    meses_obra = meses_obra_o_faena(inicio, termino) if causal == "termino_obra" else 0
    indemnizacion_obra = redondear(base / 30 * DIAS_POR_MES_OBRA * meses_obra)
    proporcional = feriado_proporcional(inicio, termino, p)
    habiles = proporcional["dias_habiles"] + dias_pendientes
    conversion = dias_corridos_de_feriado(habiles, termino, feriados)
    valor_dia = remuneracion / 30
    feriado = redondear(conversion["dias_corridos"] * valor_dia)
    remuneracion_pendiente = redondear(dias_por_pagar * valor_dia)
    return {
        "tiempo": tiempo_trabajado(inicio, termino),
        "anios_indemnizacion": anios,
        "tope_aplicado": (con_indemnizacion or causal == "termino_obra") and remuneracion > tope,
        "indemnizacion_anios": indemnizacion,
        "aviso_previo": aviso,
        "meses_obra": meses_obra,
        "indemnizacion_obra": indemnizacion_obra,
        "feriado_proporcional_habiles": proporcional["dias_habiles"],
        "feriado_habiles": habiles,
        "feriado_corridos": conversion["dias_corridos"],
        "feriado_inhabiles": conversion["inhabiles"],
        "feriado": feriado,
        "remuneracion_pendiente": remuneracion_pendiente,
        "total": indemnizacion + aviso + indemnizacion_obra + feriado + remuneracion_pendiente,
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


# ---------------------------------------------------------------------------
# IVA
# ---------------------------------------------------------------------------
# Montos en pesos enteros. El IVA se calcula sobre el neto y se redondea al peso.
# Un precio con IVA incluido se desglosa calculando primero el neto (total ÷ 1,19,
# redondeado) y el IVA como la diferencia, para que neto + IVA sea el total exacto.

def iva_desde_neto(neto: float, p: dict) -> dict:
    """Agrega el IVA a un monto neto (tasa general del DL 825, art. 14)."""
    tasa = p["iva"]
    neto = redondear(neto)
    iva = redondear(neto * tasa)
    return {"neto": neto, "iva": iva, "total": neto + iva, "tasa": tasa}


def iva_desde_total(total: float, p: dict) -> dict:
    """Saca el IVA de un precio que ya lo incluye."""
    tasa = p["iva"]
    total = redondear(total)
    neto = redondear(total / (1 + tasa))
    return {"neto": neto, "iva": total - neto, "total": total, "tasa": tasa}


# ---------------------------------------------------------------------------
# Horas extra
# ---------------------------------------------------------------------------

def factor_horas_extra(jornada: float, p: dict) -> float:
    """Factor que, multiplicado por el sueldo mensual, da el valor de una hora extra.

    Es la fórmula de la Dirección del Trabajo con el recargo incluido: para 42 horas,
    1,5 × 28 / (30 × 4 × 42) = 0,0083333.
    """
    return (1 + p["recargo_horas_extra"]) * 28 / (30 * 4 * jornada)


def horas_extra(sueldo: float, horas: float, jornada: float, p: dict) -> dict:
    """Pago de las horas extra del mes de un trabajador con sueldo mensual (art. 32 del Código del Trabajo).

    - Hora ordinaria según la Dirección del Trabajo: sueldo / 30 × 28 / (4 × jornada semanal).
    - La hora extra lleva un recargo de 50% sobre ese valor.
    - La base es el sueldo convenido, pero no puede ser menor que el ingreso mínimo mensual;
      con una jornada menor que la legal, el mínimo es proporcional a ella (art. 40 bis A y
      dictámenes de la DT). Si ``jornada`` supera la legal vigente (por ejemplo, 44 horas para
      un mes anterior a la rebaja), el mínimo se toma completo.
    """
    minimo = p["imm"] * min(1.0, jornada / p["jornada_semanal_horas"])
    base = max(sueldo, minimo)
    valor_hora = base / 30 * 28 / (4 * jornada)
    valor_extra = valor_hora * (1 + p["recargo_horas_extra"])
    return {
        "sueldo": sueldo,
        "base": base,
        "minimo": minimo,
        "minimo_aplicado": sueldo < minimo,
        "valor_hora": valor_hora,
        "valor_hora_extra": valor_extra,
        "factor": factor_horas_extra(jornada, p),
        "horas": horas,
        "total": redondear(valor_extra * horas),
    }


# ---------------------------------------------------------------------------
# Crédito de consumo
# ---------------------------------------------------------------------------

def tasa_timbres(meses: int, p: dict) -> float:
    """Tasa del impuesto de timbres y estampillas de un crédito a ``meses`` (DL 3.475, art. 1 N° 3):
    0,066% por cada mes o fracción hasta el último vencimiento, con un máximo de 0,8%."""
    return min(p["timbres_tasa_mensual"] * meses, p["timbres_tope"])


def cuota_francesa(capital: float, tasa_mensual: float, meses: int) -> float:
    """Cuota fija mensual (sistema francés).

    (1 + r)^n se calcula multiplicando mes a mes para que JavaScript obtenga exactamente
    el mismo número (``**`` y ``Math.pow`` pueden diferir en el último decimal).
    """
    if tasa_mensual == 0:
        return capital / meses
    factor = 1.0
    for _ in range(meses):
        factor *= 1 + tasa_mensual
    return capital * tasa_mensual * factor / (factor - 1)


def valor_presente(flujos: list[float], tasa_mensual: float) -> float:
    """Valor presente de pagos mensuales; el primero vence al mes 1."""
    total = 0.0
    descuento = 1.0
    for flujo in flujos:
        descuento /= 1 + tasa_mensual
        total += flujo * descuento
    return total


def carga_anual_equivalente(monto_liquido: float, flujos: list[float]) -> float:
    """CAE según la Ley 20.555 y el reglamento de créditos de consumo (DS 43 de 2012).

    Es la tasa que iguala el valor presente de los pagos (cuotas con seguros y gastos) con
    el monto líquido que recibe el consumidor en el mes 0, expresada en base anual con
    capitalización mensual: la tasa mensual multiplicada por 12. Lo que se paga al
    contado al firmar se descuenta del monto líquido.

    Se resuelve por bisección con un número fijo de pasos para que Python y JavaScript
    lleguen al mismo resultado. Si los pagos no superan lo recibido, la CAE es 0.
    """
    if monto_liquido <= 0:
        raise ValueError("Lo que se paga al firmar no puede igualar o superar el monto del crédito")
    bajo, alto = 0.0, 1.0
    while valor_presente(flujos, alto) > monto_liquido and alto < 1e6:
        alto *= 2
    for _ in range(100):
        medio = (bajo + alto) / 2
        if valor_presente(flujos, medio) > monto_liquido:
            bajo = medio
        else:
            alto = medio
    return 12 * (bajo + alto) / 2


def credito_consumo(monto: float, meses: int, tasa_mensual: float, p: dict, seguros: float = 0.0,
                    gastos: float = 0.0, financiar: bool = True) -> dict:
    """Simulación de un crédito de consumo en pesos con cuota fija (sistema francés).

    - ``monto``: lo que quieres recibir (monto líquido).
    - ``tasa_mensual``: tasa de interés mensual en fracción (0.015 = 1,5%).
    - ``seguros``: seguros mensuales que se suman a cada cuota.
    - ``gastos``: gastos y comisiones iniciales (notaría, comisión de apertura...).
    - ``financiar``: True si el impuesto de timbres y los gastos se suman al crédito; False
      si se pagan al contado al firmar.

    El impuesto de timbres se calcula sobre el monto del crédito (el capital del pagaré).
    Si se financia, ese capital lo incluye: monto bruto = (monto + gastos) / (1 − tasa).
    """
    monto = redondear(monto)
    seguros = redondear(seguros)
    gastos = redondear(gastos)
    tasa_impuesto = tasa_timbres(meses, p)
    if financiar:
        bruto = redondear((monto + gastos) / (1 - tasa_impuesto))
        impuesto = bruto - monto - gastos
        al_contado = 0.0
    else:
        bruto = monto
        impuesto = redondear(monto * tasa_impuesto)
        al_contado = impuesto + gastos
    cuota = redondear(cuota_francesa(bruto, tasa_mensual, meses))
    cuota_total = cuota + seguros
    total_cuotas = cuota_total * meses
    costo_total = total_cuotas + al_contado
    return {
        "monto_liquido": monto,
        "monto_bruto": bruto,
        "meses": meses,
        "tasa_mensual": tasa_mensual,
        "tasa_impuesto": tasa_impuesto,
        "impuesto": impuesto,
        "gastos": gastos,
        "al_contado": al_contado,
        "cuota": cuota,
        "seguros": seguros,
        "cuota_total": cuota_total,
        "total_cuotas": total_cuotas,
        "intereses": cuota * meses - bruto,
        "total_seguros": seguros * meses,
        "costo_total": costo_total,
        "sobrecosto": costo_total - monto,
        "cae": carga_anual_equivalente(monto - al_contado, [cuota_total] * meses),
    }
