"""Indicadores previsionales del mes (/indicadores-previsionales/).

Cada mes mucha gente busca la tabla de indicadores previsionales de Previred. Esta página
reúne los mismos parámetros que usan las calculadoras (``c.p`` y ``c.params``, es decir,
``parametros/chile.yaml``), en UF y en pesos, cada bloque con su vigencia y su fuente. No
reemplaza el documento oficial de Previred y lo dice claramente; los valores que el sitio
no mantiene (asignación familiar, trabajos pesados, etc.) no se muestran.

Se suma al sitio en ``todas_las_paginas`` (lucas/paginas.py).
"""

from __future__ import annotations

import datetime as dt

from .confianza import FUENTES_OFICIALES, nombre_fuente, proximos_cambios, vigencia
from .construir import Contexto, Pagina
from .datos import Datos, mes_siguiente, primer_dia
from .formato import dia_mes, fecha_larga, mes_anio, mes_de_anio, numero, pesos, redondear
from .fuentes import SII, SII_PAGINAS
from .paginas_calculadoras_extra import porcentaje_corto

RUTA = "/indicadores-previsionales/"

# Tipos de contrato del seguro de cesantía (claves de seguro_cesantia en chile.yaml).
CONTRATOS = {
    "indefinido": "Indefinido",
    "plazo_fijo": "Plazo fijo, obra o faena",
    "indefinido_11": "Indefinido, más de 11 años",
}


def uf_texto(valor: float) -> str:
    """Cantidad de UF sin decimales sobrantes: ``90.0`` → ``'90'``, ``135.2`` → ``'135,2'``."""
    return numero(valor, 2).rstrip("0").rstrip(",")


def paginas_previsionales(c: Contexto) -> list[Pagina]:
    from .paginas import INICIO, tabla_impuesto_pesos  # import diferido: paginas importa este módulo
    p, params, hoy = c.p, c.params, c.hoy
    nombre_mes = mes_anio(hoy.year, hoy.month)          # "octubre 2026"

    # p["uf_topes"] es la UF del último día del mes (o la última publicada si aún no se conoce).
    fin_de_mes = mes_siguiente(primer_dia(hoy)) - dt.timedelta(days=1)
    fecha_uf = Datos.ultimo(c.datos.uf_completa(), fin_de_mes)[0]
    uf = p["uf_topes"]

    def fuente(grupo: str) -> dict:
        url = str(params[grupo].get("fuente") or "")
        return {"url": url, "nombre": nombre_fuente(url)}

    def tope(nombre: str, cantidad_uf: float) -> dict:
        return {"nombre": nombre, "uf": cantidad_uf, "pesos": redondear(cantidad_uf * uf)}

    topes = [tope("AFP y salud", p["tope_imponible_uf"]),
             tope("Seguro de cesantía", p["tope_cesantia_uf"])]
    imm = params.vigente("ingreso_minimo", hoy)
    minimos = [("Trabajadores de 18 a 65 años", p["imm"])]
    if imm.get("menores_18_mayores_65"):
        minimos.append(("Menores de 18 y mayores de 65 años", imm["menores_18_mayores_65"]))
    if imm.get("no_remuneracional"):
        minimos.append(("Para fines no remuneracionales", imm["no_remuneracional"]))
    afps = [{"nombre": p["nombres_afp"][clave], "comision": comision, "total": p["tasa_afp"] + comision}
            for clave, comision in sorted(p["comisiones_afp"].items(), key=lambda x: (x[1], x[0]))]
    cesantia = [{"contrato": CONTRATOS.get(clave, clave), "trabajador": p["cesantia_trabajador"][clave],
                 "empleador": empleador, "total": p["cesantia_trabajador"][clave] + empleador}
                for clave, empleador in p["cesantia_empleador"].items()]
    apv = params.vigente("apv", hoy)
    gratificacion_anual = p["gratificacion_tope_imm_anual"] * p["imm"]
    sis_desde = vigencia(params, "cotizaciones_empleador", hoy, ("sis",))
    url_utm = f"{SII}/{SII_PAGINAS['utm'].format(anio=hoy.year)}"
    barata = afps[0]

    faq = [
        ("¿Qué son los indicadores previsionales?",
         "Son los valores con que se calculan las cotizaciones de cada mes: UF y UTM, topes "
         "imponibles, ingreso mínimo, tasas y comisiones de las AFP, seguro de cesantía y aportes "
         "del empleador. Previred los publica cada mes en un documento que es la referencia para "
         "declarar y pagar las cotizaciones."),
        (f"¿Cuál es el tope imponible de {nombre_mes}?",
         f"Para AFP y salud es de {uf_texto(topes[0]['uf'])} UF, es decir {pesos(topes[0]['pesos'])} "
         f"con la UF del {fecha_larga(fecha_uf)} ({pesos(uf, 2)}). Para el seguro de cesantía es de "
         f"{uf_texto(topes[1]['uf'])} UF ({pesos(topes[1]['pesos'])})."),
        ("¿Con qué UF se calculan los topes imponibles?",
         "Con la UF del último día del mes de la remuneración (artículo 16 del DL 3.500), igual que "
         "en el documento de Previred. Por eso el tope en pesos cambia cada mes aunque el tope en UF "
         "sea el mismo." + ("" if fecha_uf == fin_de_mes else
                             " Mientras esa UF no se publica, aquí usamos la última conocida.")),
        ("¿Qué AFP cobra la comisión más baja?",
         f"{barata['nombre']}, con {porcentaje_corto(barata['comision'])} de la remuneración "
         f"imponible: su descuento total es {porcentaje_corto(barata['total'])} "
         f"({porcentaje_corto(p['tasa_afp'])} para tu cuenta más la comisión)."),
        ("¿Quién paga el SIS?",
         (f"El empleador. Desde el {fecha_larga(sis_desde['desde'])}, el Seguro de Invalidez y "
          "Sobrevivencia va incluido en el aporte del empleador de la reforma de pensiones "
          f"(Ley 21.735), que es de {porcentaje_corto(p['aporte_empleador_reforma'])} de la "
          "remuneración imponible.") if p["sis"] == 0 else
         (f"El empleador, con una tasa de {porcentaje_corto(p['sis'])} de la remuneración "
          "imponible, además del aporte de la reforma de pensiones.")),
        ("¿Dónde está el documento oficial?",
         "En el sitio de Previred, que publica cada mes los indicadores previsionales, y en la "
         "Superintendencia de Pensiones, que publica los topes, la tasa del SIS y las comisiones "
         "vigentes. Esta página es un resumen de referencia."),
    ]
    descripcion = (f"Indicadores previsionales de {mes_de_anio(hoy.year, hoy.month)}: UF del "
                   f"{dia_mes(fecha_uf)} {pesos(uf, 2)}, UTM {pesos(p['utm'])}, tope imponible de "
                   f"{uf_texto(topes[0]['uf'])} UF ({pesos(topes[0]['pesos'])}), comisiones de AFP, "
                   "seguro de cesantía y tabla del impuesto único.")
    return [Pagina(
        ruta=RUTA,
        plantilla="indicadores_previsionales.html",
        titulo=f"Indicadores previsionales {nombre_mes}: topes, AFP, SIS y más",
        descripcion=descripcion,
        h1=f"Indicadores previsionales {nombre_mes}",
        migas=[INICIO, ("Indicadores previsionales", RUTA)],
        faq=faq,
        clave="sueldo",
        prioridad=0.9,
        frecuencia="weekly",
        contexto={
            "pct": porcentaje_corto,
            "uf_texto": uf_texto,
            "fin_de_mes": fin_de_mes,
            "fecha_uf": fecha_uf,
            "uf_calculada": fecha_uf not in c.datos.uf,
            "uf": uf,
            "utm": p["utm"],
            "uta": 12 * p["utm"],
            "url_utm": url_utm,
            "topes": topes,
            "vigencia_topes": vigencia(params, "topes_imponibles", hoy),
            "fuente_topes": fuente("topes_imponibles"),
            "imm": imm,
            "minimos": minimos,
            "vigencia_imm": vigencia(params, "ingreso_minimo", hoy),
            "fuente_imm": fuente("ingreso_minimo"),
            "gratificacion_anual": gratificacion_anual,
            "gratificacion_mensual": gratificacion_anual / 12,
            "gratificacion_tasa": p["gratificacion_tasa"],
            "gratificacion_tope_imm": p["gratificacion_tope_imm_anual"],
            "fuente_gratificacion": fuente("gratificacion"),
            "afps": afps,
            "tasa_afp": p["tasa_afp"],
            "salud": p["salud_obligatoria"],
            "vigencia_afp": vigencia(params, "afp", hoy),
            "fuente_afp": fuente("afp"),
            "vigencia_salud": vigencia(params, "salud", hoy),
            "fuente_salud": fuente("salud"),
            "sis": p["sis"],
            "aporte": p["aporte_empleador_reforma"],
            "mutual": p["mutual_basica"],
            "vigencia_aporte": vigencia(params, "cotizaciones_empleador", hoy,
                                        ("aporte_reforma_pensiones", "sis")),
            "vigencia_mutual": vigencia(params, "cotizaciones_empleador", hoy, ("mutual_basica",)),
            "fuente_empleador": fuente("cotizaciones_empleador"),
            "proximos_aportes": [e for e in proximos_cambios(params, "cotizaciones_empleador", hoy)
                                 if e.get("aporte_reforma_pensiones") not in (None, p["aporte_empleador_reforma"])],
            "cesantia": cesantia,
            "vigencia_cesantia": vigencia(params, "seguro_cesantia", hoy),
            "fuente_cesantia": fuente("seguro_cesantia"),
            "apv_mensual_uf": p["tope_apv_mensual_uf"],
            "apv_anual_uf": apv["tope_anual_uf"],
            "apv_bonificacion": apv["bonificacion_regimen_a"],
            "apv_bonificacion_utm": apv["tope_bonificacion_utm"],
            "vigencia_apv": vigencia(params, "apv", hoy),
            "fuente_apv": fuente("apv"),
            "honorarios": p["retencion_honorarios"],
            "vigencia_honorarios": vigencia(params, "retencion_honorarios", hoy),
            "fuente_honorarios": fuente("retencion_honorarios"),
            "proximos_honorarios": proximos_cambios(params, "retencion_honorarios", hoy),
            "tabla_impuesto": tabla_impuesto_pesos(p, p["utm"]),
            "vigencia_impuesto": vigencia(params, "impuesto_unico", hoy),
            "fuente_impuesto": fuente("impuesto_unico"),
            "oficiales": FUENTES_OFICIALES,
        },
    )]
