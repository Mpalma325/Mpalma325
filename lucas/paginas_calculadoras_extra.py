"""Calculadoras de IVA, horas extra y crédito de consumo.

Se suman al sitio en ``todas_las_paginas`` (lucas/paginas.py) y sus tarjetas están en la
lista de ``paginas_calculadoras``. Las fórmulas viven al final de ``lucas/calculos.py`` y
de ``estaticos/js/calculos.js``; los parámetros, en los grupos ``iva``, ``jornada_laboral``,
``impuesto_timbres`` y ``credito_consumo`` de ``parametros/chile.yaml``.
"""

from __future__ import annotations

import datetime as dt
import math

from . import calculos
from .construir import Contexto, Pagina
from .formato import fecha_larga, numero, pesos, porcentaje

CALCULADORAS = ("Calculadoras", "/calculadoras/")

# Montos de las tablas de ejemplo. Se pueden cambiar libremente.
NETOS_IVA = [1_000, 5_000, 10_000, 20_000, 50_000, 100_000, 500_000, 1_000_000]
TOTALES_IVA = [1_000, 5_000, 10_000, 50_000, 100_000, 1_000_000]
SUELDOS_HORAS_EXTRA = [600_000, 800_000, 1_000_000, 1_500_000]   # además del sueldo mínimo
MONTOS_CONSUMO = [1_000_000, 3_000_000, 5_000_000, 10_000_000]
PLAZOS_CONSUMO = [12, 24, 36, 48, 60]


def factor_texto(factor: float) -> str:
    """Factor de horas extra con 7 decimales truncados, como lo publica la DT (0,0083333).

    Es la misma regla que ``factorTexto`` en estaticos/js/app.js.
    """
    truncado = math.floor(factor * 1e7 + 1e-6) / 1e7
    return numero(truncado, 7).rstrip("0").rstrip(",")


def porcentaje_corto(fraccion: float) -> str:
    """Porcentaje con hasta 3 decimales, sin ceros sobrantes: ``0,8%`` o ``0,792%``."""
    return numero(fraccion * 100, 3).rstrip("0").rstrip(",") + "%"


def texto_tiempo(anios: int, meses: int, dias: int) -> str:
    """``"3 años, 7 meses, 0 días"``: el mismo texto que ``textoTiempo`` en estaticos/js/app.js
    (así el valor inicial de la página no cambia cuando el JavaScript recalcula)."""
    partes = [f"{anios} {'año' if anios == 1 else 'años'}"] if anios else []
    partes.append(f"{meses} {'mes' if meses == 1 else 'meses'}")
    partes.append(f"{dias} {'día' if dias == 1 else 'días'}")
    return ", ".join(partes)


def leido_del_formulario(valor: float, decimales: int) -> float:
    """El número que lee app.js (``leerNumero``) de un campo cuyo valor inicial es
    ``numero(valor, decimales)``: "4,20" -> 4.2. El resultado inicial de la página se calcula
    con él para que coincida con el del navegador."""
    return float(numero(valor, decimales).replace(".", "").replace(",", "."))


def enumerar(partes: list[str], prefijo: str = "") -> str:
    """``["a", "b", "c"]`` -> ``"a, b y c"``; con ``prefijo="a "``: ``"a, a b y a c"``."""
    if len(partes) == 1:
        return partes[0]
    resto = [prefijo + parte for parte in partes[1:]]
    return ", ".join([partes[0]] + resto[:-1]) + " y " + resto[-1]


def paginas_calculadoras_extra(c: Contexto) -> list[Pagina]:
    return [pagina_iva(c), pagina_horas_extra(c), pagina_credito_consumo(c)]


# ---------------------------------------------------------------------------
# IVA
# ---------------------------------------------------------------------------

def pagina_iva(c: Contexto) -> Pagina:
    from .paginas import INICIO, _app  # import diferido: paginas importa este módulo

    p = c.p
    tasa = p["iva"]
    vigente = c.params.vigente("iva", c.hoy)
    ejemplo_total = calculos.iva_desde_total(50_000, p)
    ejemplo_neto = calculos.iva_desde_neto(100_000, p)
    ruta = "/calculadoras/iva/"
    descripcion = (f"Calcula el IVA en Chile: agrega el {porcentaje(tasa, 0)} a un monto neto o saca el "
                   "IVA de un precio que ya lo incluye. Neto, IVA y total al instante, redondeados al peso.")
    return Pagina(
        ruta=ruta,
        plantilla="calc_iva.html",
        titulo=f"Calculadora de IVA Chile {c.hoy.year}: agregar o sacar el IVA ({porcentaje(tasa, 0)})",
        descripcion=descripcion,
        h1="Calculadora de IVA",
        migas=[INICIO, CALCULADORAS, ("IVA", ruta)],
        clave="iva",
        calculadora=True,
        prioridad=0.9,
        frecuencia="monthly",
        jsonld=_app(c, "Calculadora de IVA", descripcion, ruta),
        datos_js={"parametros": p},
        faq=[
            ("¿Cómo saco el IVA de un precio?",
             f"Divide el precio por {numero(1 + tasa, 2)} para obtener el monto neto y réstalo del precio: "
             f"la diferencia es el IVA. Por ejemplo, un precio de {pesos(ejemplo_total['total'])} tiene un "
             f"neto de {pesos(ejemplo_total['neto'])} y un IVA de {pesos(ejemplo_total['iva'])}. El neto se "
             "redondea al peso y el IVA se obtiene por diferencia, para que la suma dé el precio exacto."),
            ("¿Cómo calculo el precio con IVA?",
             f"Multiplica el monto neto por {numero(1 + tasa, 2)}, o súmale el {porcentaje(tasa, 0)}. Por "
             f"ejemplo, {pesos(ejemplo_neto['neto'])} neto quedan en {pesos(ejemplo_neto['total'])} con IVA "
             f"({pesos(ejemplo_neto['iva'])} de impuesto)."),
            ("¿Cuánto es el IVA en Chile?",
             f"La tasa general es {porcentaje(tasa, 0)} sobre el precio neto (artículo 14 del DL 825, "
             f"Ley sobre Impuesto a las Ventas y Servicios). Rige desde el {fecha_larga(vigente['desde'])}, "
             f"cuando la {vigente['ley']} la subió desde 18%."),
            ("¿Por qué el IVA no es el 19% del precio final?",
             f"Porque el {porcentaje(tasa, 0)} se calcula sobre el neto, no sobre el total. El IVA que viene "
             f"dentro de un precio con IVA es {numero(tasa * 100)}/{numero(100 + tasa * 100)} del total, es "
             f"decir, cerca de un {porcentaje(tasa / (1 + tasa), 2)}."),
            ("¿Las boletas de honorarios llevan IVA?",
             "No. Los servicios que prestan las personas con boleta de honorarios no pagan IVA; en cambio, "
             f"la boleta tiene una retención de impuesto de {porcentaje(p['retencion_honorarios'], 2)} en "
             f"{c.hoy.year}. Para esos montos usa la calculadora de boleta de honorarios."),
        ],
        contexto={
            "tasa": tasa,
            "vigente": vigente,
            "inicial": ejemplo_neto,
            "desde_neto": [calculos.iva_desde_neto(n, p) for n in NETOS_IVA],
            "desde_total": [calculos.iva_desde_total(t, p) for t in TOTALES_IVA],
            "tasa_honorarios": p["retencion_honorarios"],
        },
    )


# ---------------------------------------------------------------------------
# Horas extra
# ---------------------------------------------------------------------------

def jornadas_legales(c: Contexto) -> list[dict]:
    """Jornadas máximas de la tabla de ``parametros/chile.yaml`` con su factor de horas extra."""
    historial = c.params.historial("jornada_laboral")
    filas = []
    for indice, entrada in enumerate(historial):
        desde = entrada["desde"]
        siguiente = historial[indice + 1]["desde"] if indice + 1 < len(historial) else None
        horas = float(entrada["horas_semanales"])
        factor = calculos.factor_horas_extra(horas, {"recargo_horas_extra": float(entrada["recargo_horas_extra"])})
        filas.append({
            "horas": horas,
            "desde": desde,
            "hasta": siguiente - dt.timedelta(days=1) if siguiente else None,
            "primera": indice == 0,
            "vigente": desde <= c.hoy and (siguiente is None or c.hoy < siguiente),
            "futura": desde > c.hoy,
            "divisor": 4 * horas,
            "factor": factor_texto(factor),
        })
    return filas


def pagina_horas_extra(c: Contexto) -> Pagina:
    from .paginas import INICIO, _app  # import diferido: paginas importa este módulo

    p = c.p
    jornada = p["jornada_semanal_horas"]
    recargo = p["recargo_horas_extra"]
    vigente = c.params.vigente("jornada_laboral", c.hoy)
    jornadas = jornadas_legales(c)
    actual = next(j for j in jornadas if j["vigente"])
    anterior = jornadas[jornadas.index(actual) - 1] if jornadas.index(actual) > 0 else None
    proximas = [j for j in jornadas if j["futura"]]
    factor = factor_texto(calculos.factor_horas_extra(jornada, p))
    minimo = calculos.horas_extra(p["imm"], 10, jornada, p)
    ejemplos = [calculos.horas_extra(s, 10, jornada, p) for s in [p["imm"]] + SUELDOS_HORAS_EXTRA]
    ruta = "/calculadoras/horas-extra/"
    descripcion = (f"Calcula cuánto te deben pagar por horas extra con la fórmula de la Dirección del "
                   f"Trabajo y la jornada de {numero(jornada)} horas: valor de la hora, recargo de "
                   f"{porcentaje(recargo, 0)} y total del mes.")
    rebajas = jornadas[1:]
    faq_ley = (f"La Ley 21.561 rebaja la jornada máxima de forma gradual: de {numero(jornadas[0]['horas'])} a "
               + enumerar([f"{numero(j['horas'])} horas el {fecha_larga(j['desde'])}" for j in rebajas], "a ")
               + ". Con menos horas, cada hora vale más: el factor de la hora extra es "
               + enumerar([f"{j['factor']} con {numero(j['horas'])} horas" for j in rebajas]) + ".")
    return Pagina(
        ruta=ruta,
        plantilla="calc_horas_extra.html",
        titulo=f"Calculadora de horas extra {c.hoy.year}: valor hora con jornada de {numero(jornada)} horas",
        descripcion=descripcion,
        h1="Calculadora de horas extra",
        migas=[INICIO, CALCULADORAS, ("Horas extra", ruta)],
        clave="sueldo",
        calculadora=True,
        prioridad=0.9,
        frecuencia="weekly",
        jsonld=_app(c, "Calculadora de horas extra", descripcion, ruta),
        datos_js={"parametros": p},
        faq=[
            ("¿Cómo se calcula el valor de la hora extra?",
             f"Según la Dirección del Trabajo, con sueldo mensual se divide el sueldo por 30, se multiplica "
             f"por 28 y se divide por {numero(4 * jornada)} (4 veces la jornada semanal de "
             f"{numero(jornada)} horas). Eso da la hora ordinaria; la hora extra vale "
             f"{porcentaje(recargo, 0)} más. Es lo mismo que multiplicar el sueldo por {factor}."),
            ("¿Cuánto vale la hora extra con el sueldo mínimo?",
             f"Con el ingreso mínimo de {pesos(p['imm'])} y la jornada de {numero(jornada)} horas, la hora "
             f"ordinaria vale {pesos(minimo['valor_hora'])} y la hora extra {pesos(minimo['valor_hora_extra'])}. "
             f"Diez horas extra suman {pesos(minimo['total'])}."),
            ("¿Cuántas horas extra se pueden trabajar?",
             "Como máximo 2 por día, y solo para atender necesidades o situaciones temporales de la empresa. "
             "El pacto debe constar por escrito y durar como máximo tres meses, aunque se puede renovar. Si "
             "trabajas más allá de tu jornada con conocimiento del empleador, esas horas igual se pagan como "
             "extra aunque no haya pacto."),
            ("¿Las horas extra se calculan sobre el sueldo total?",
             "No. Se calculan sobre el sueldo convenido (el sueldo base y otros pagos fijos que la ley "
             "considera sueldo), no sobre comisiones ni bonos variables. Si ese sueldo es menor que el "
             "ingreso mínimo, se calculan sobre el ingreso mínimo, proporcional a tus horas si tu jornada "
             "es parcial."),
            ("¿Qué cambia con la ley de 40 horas?", faq_ley),
            ("¿Puedo cambiar las horas extra por días libres?",
             "Sí. Desde la Ley 21.561 puedes acordar por escrito con tu empleador compensar horas extra con "
             "días adicionales de feriado, hasta cinco días hábiles al año, que debes usar dentro de los seis "
             "meses siguientes."),
        ],
        contexto={
            "jornada": jornada,
            "recargo": recargo,
            "vigente": vigente,
            "jornadas": jornadas,
            "anterior": anterior,
            "proximas": proximas,
            "factor": factor,
            "inicial": calculos.horas_extra(800_000, 10, jornada, p),
            "ejemplos": ejemplos,
            "imm": p["imm"],
        },
    )


# ---------------------------------------------------------------------------
# Crédito de consumo
# ---------------------------------------------------------------------------

def pagina_credito_consumo(c: Contexto) -> Pagina:
    from .paginas import INICIO, _app  # import diferido: paginas importa este módulo

    p = c.p
    tasa = float(c.params.vigente("credito_consumo", c.hoy)["tasa_mensual_ejemplo"])
    inicial = calculos.credito_consumo(3_000_000, 36, tasa, p)
    al_contado = calculos.credito_consumo(3_000_000, 36, tasa, p, financiar=False)
    cuotas = [{"monto": monto,
               "cuotas": [calculos.credito_consumo(monto, meses, tasa, p)["cuota_total"] for meses in PLAZOS_CONSUMO]}
              for monto in MONTOS_CONSUMO]
    por_plazo = [calculos.credito_consumo(inicial["monto_liquido"], meses, tasa, p) for meses in PLAZOS_CONSUMO]
    ruta = "/calculadoras/credito-consumo/"
    descripcion = ("Simula tu crédito de consumo: cuota mensual, CAE (carga anual equivalente), intereses "
                   "y costo total, con impuesto de timbres, seguros y gastos. Gratis y sin registro.")
    return Pagina(
        ruta=ruta,
        plantilla="calc_credito_consumo.html",
        titulo=f"Simulador de crédito de consumo {c.hoy.year}: cuota, CAE y costo total",
        descripcion=descripcion,
        h1="Simulador de crédito de consumo",
        migas=[INICIO, CALCULADORAS, ("Crédito de consumo", ruta)],
        clave="consumo",
        calculadora=True,
        prioridad=0.9,
        frecuencia="monthly",
        jsonld=_app(c, "Simulador de crédito de consumo", descripcion, ruta),
        datos_js={"parametros": p},
        faq=[
            ("¿Qué es la CAE?",
             "La carga anual equivalente es un porcentaje que muestra el costo de un crédito en un año, "
             "cualquiera sea su plazo: incluye los intereses, los seguros, los gastos y el impuesto. Desde la "
             "Ley 20.555, toda publicidad de créditos que muestre una tasa o una cuota debe informarla. Sirve "
             "para comparar ofertas: a igual monto y plazo, el crédito con menor CAE es el más barato."),
            ("¿Por qué la CAE es más alta que la tasa de interés?",
             f"Porque suma todos los costos, no solo los intereses. Un crédito de {pesos(3_000_000)} a 36 "
             f"meses con una tasa de {porcentaje(tasa, 2)} mensual ({porcentaje(tasa * 12, 2)} al año) tiene "
             f"una CAE de {porcentaje(inicial['cae'], 2)} solo por el impuesto de timbres; los seguros y "
             "gastos la suben aún más."),
            ("¿Cómo se calcula la CAE?",
             "Se busca la tasa mensual con la que el valor presente de todas las cuotas (con seguros y "
             "gastos) es igual al monto líquido que recibes, y se multiplica por 12. Es el método del "
             "reglamento de información al consumidor de créditos de consumo (DS 43 de 2012). Lo que pagues "
             "al contado al firmar se descuenta de lo que recibes."),
            ("¿Cuánto es el impuesto de timbres y estampillas de un crédito?",
             f"{porcentaje_corto(p['timbres_tasa_mensual'])} del monto por cada mes de plazo, con un máximo "
             f"de {porcentaje_corto(p['timbres_tope'])}, que se alcanza desde los 13 meses. En un crédito de "
             f"{pesos(3_000_000)} a 36 meses son {pesos(al_contado['impuesto'])} si lo pagas al contado, o "
             f"{pesos(inicial['impuesto'])} si se suma al crédito, porque entonces el monto del crédito "
             "incluye el propio impuesto."),
            ("¿Hay una tasa máxima para los créditos de consumo?",
             "Sí. No se pueden pactar intereses por sobre la tasa máxima convencional (TMC), que publica la "
             "Comisión para el Mercado Financiero (CMF) y depende del monto y el plazo del crédito. Revisa "
             "la TMC vigente en el sitio de la CMF antes de firmar."),
        ],
        contexto={
            "tasa": tasa,
            "inicial": inicial,
            "al_contado": al_contado,
            "plazos": PLAZOS_CONSUMO,
            "cuotas": cuotas,
            "por_plazo": por_plazo,
            "tasa_impuesto_texto": porcentaje_corto(inicial["tasa_impuesto"]),
            "timbres_mensual": porcentaje_corto(p["timbres_tasa_mensual"]),
            "timbres_tope": porcentaje_corto(p["timbres_tope"]),
            "timbres_12": porcentaje_corto(calculos.tasa_timbres(12, p)),
        },
    )
