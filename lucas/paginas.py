"""Definición de todas las páginas del sitio: textos para buscadores, datos y plantilla.

Cada función ``paginas_*`` recibe el ``Contexto`` (datos, parámetros, fecha) y
devuelve una lista de ``Pagina``. Para agregar una sección nueva: crea su
función aquí, su plantilla en ``plantillas/`` y súmala en ``todas_las_paginas``.
"""

from __future__ import annotations

import datetime as dt

from . import calculos, seo
from .construir import Contexto, Pagina
from .datos import (Datos, dias_del_mes, mes_anterior, mes_siguiente, periodo_uf, primer_dia,
                    uf_proyectada)
from .feriados import (feriados_nacionales, feriados_regionales, fines_de_semana_largos,
                       proximos_feriados)
from .formato import (capitalizar, dia_mes, fecha_con_dia, fecha_larga, mes_anio, mes_de_anio,
                      monto_corto, nombre_mes, numero, pesos, porcentaje, redondear)
from .graficos import grafico_barras, grafico_linea

# Montos con página propia ("1000 UF en pesos", "100 dólares en pesos", etc.).
# Son búsquedas frecuentes en Google. Puedes agregar o quitar montos libremente.
MONTOS_UF = [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 150, 200, 250, 300, 400,
             500, 600, 700, 800, 900, 1000, 1200, 1500, 1800, 2000, 2200, 2500, 2800, 3000,
             3200, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000]
MONTOS_DOLAR = [1, 5, 10, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200, 250, 300, 350,
                400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 2500, 3000, 5000, 10000]
MONTOS_EURO = [1, 10, 20, 50, 100, 200, 300, 500, 1000, 2000, 5000]
SUELDOS = [600000, 700000, 750000, 800000, 850000, 900000, 1000000, 1100000, 1200000, 1300000,
           1400000, 1500000, 1600000, 1700000, 1800000, 2000000, 2200000, 2500000, 2800000,
           3000000, 3500000, 4000000, 4500000, 5000000, 6000000, 7000000, 8000000, 10000000]

INICIO = ("Inicio", "/")


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def ruta_mes(seccion: str, fecha: dt.date) -> str:
    return f"/{seccion}/{fecha.year}/{nombre_mes(fecha.month)}/"


def meses_de(serie: dict[dt.date, float]) -> list[dt.date]:
    return sorted({primer_dia(f) for f in serie})


def un_anio_antes(fecha: dt.date) -> dt.date:
    try:
        return fecha.replace(year=fecha.year - 1)
    except ValueError:  # 29 de febrero
        return fecha.replace(year=fecha.year - 1, day=28)


def valor_cercano(serie: dict[dt.date, float], fecha: dt.date) -> tuple[dt.date, float] | None:
    """Último valor disponible en o antes de ``fecha`` (para series con días sin dato)."""
    return Datos.ultimo(serie, fecha)


def ventana(serie: dict[dt.date, float], desde: dt.date, hasta: dt.date | None = None) -> dict[str, float]:
    return {f.isoformat(): v for f, v in sorted(serie.items())
            if f >= desde and (hasta is None or f <= hasta)}


def variacion(actual: float | None, anterior: float | None) -> float | None:
    if actual is None or not anterior:
        return None
    return actual / anterior - 1


def ipc_12_meses(c: Contexto, hasta: dt.date | None = None) -> float | None:
    hasta = hasta or c.ipc[0]
    meses = []
    mes = hasta
    for _ in range(12):
        if mes not in c.datos.ipc:
            return None
        meses.append(c.datos.ipc[mes])
        mes = mes_anterior(mes)
    return calculos.variacion_acumulada(meses)


def ipc_en_el_anio(c: Contexto, hasta: dt.date | None = None) -> float | None:
    hasta = hasta or c.ipc[0]
    meses = [v for f, v in c.datos.ipc.items() if f.year == hasta.year and f <= hasta]
    return calculos.variacion_acumulada(meses) if meses else None


def vecinos(lista: list, actual) -> list:
    """Hasta 8 elementos cercanos a ``actual`` en ``lista`` (para enlaces internos)."""
    i = lista.index(actual)
    return [x for x in lista[max(0, i - 4): i + 5] if x != actual]


def _app(c: Contexto, nombre: str, descripcion: str, ruta: str) -> list[dict]:
    return [seo.jsonld_aplicacion(c.cfg, nombre, descripcion, ruta)]


# ---------------------------------------------------------------------------
# Inicio
# ---------------------------------------------------------------------------

def paginas_inicio(c: Contexto) -> list[Pagina]:
    hoy = c.hoy
    uf_anio = c.datos.uf_dia(un_anio_antes(hoy))
    dolar_anterior = Datos.anterior(c.datos.dolar, c.dolar[0])
    euro_anterior = Datos.anterior(c.datos.euro, c.euro[0])
    utm_anterior = c.datos.utm_mes(mes_anterior(hoy))
    otros = []
    for codigo, nombre, unidad in (("tpm", "Tasa de política monetaria", "%"),
                                   ("libra_cobre", "Cobre (libra)", "US$"),
                                   ("imacec", "IMACEC", "%"),
                                   ("tasa_desempleo", "Tasa de desempleo", "%"),
                                   ("bitcoin", "Bitcoin", "US$")):
        item = c.datos.ultimos.get(codigo)
        if item:
            otros.append({"nombre": nombre, "unidad": unidad, "valor": item["valor"], "fecha": item["fecha"]})
    return [Pagina(
        ruta="/",
        plantilla="inicio.html",
        titulo=f"UF, dólar y UTM hoy + calculadoras para Chile | {c.cfg['sitio']['nombre']}",
        descripcion=(f"Valor de la UF hoy ({pesos(c.uf_hoy, 2)}), dólar observado, euro, UTM e IPC "
                     "actualizados a diario. Calculadoras gratis de sueldo líquido, boletas de "
                     "honorarios, arriendo por IPC y crédito hipotecario."),
        h1="Indicadores económicos y calculadoras para Chile",
        prioridad=1.0,
        contexto={
            "uf_variacion_anual": variacion(c.uf_hoy, uf_anio),
            "dolar_variacion": variacion(c.dolar[1], dolar_anterior[1] if dolar_anterior else None),
            "euro_variacion": variacion(c.euro[1], euro_anterior[1] if euro_anterior else None),
            "utm_variacion": variacion(c.utm_hoy, utm_anterior),
            "euro_valor": c.euro[1],
            "ipc_mes": c.ipc[0],
            "ipc_valor": c.ipc[1],
            "ipc_12m": ipc_12_meses(c),
            "proximos_feriados": proximos_feriados(hoy, 3, c.feriados_extra),
            "otros": otros,
            "uf_manana": c.datos.uf_dia(hoy + dt.timedelta(days=1)),
        },
        datos_js={"uf": ventana(c.datos.uf_completa(), hoy - dt.timedelta(days=3))},
        jsonld=seo.jsonld_sitio(c.cfg),
    )]


# ---------------------------------------------------------------------------
# UF
# ---------------------------------------------------------------------------

FAQ_UF = [
    ("¿Qué es la UF?",
     "La Unidad de Fomento (UF) es una unidad de cuenta reajustable según la inflación, creada en "
     "Chile en 1967. Se usa para expresar créditos hipotecarios, arriendos, planes de isapre, "
     "seguros y otros contratos de largo plazo, de modo que mantengan su valor real en el tiempo."),
    ("¿Quién calcula el valor de la UF?",
     "El Banco Central de Chile. La UF se reajusta día a día entre el día 10 de cada mes y el día "
     "9 del mes siguiente, de acuerdo con la variación del IPC del mes anterior que publica el INE."),
    ("¿Por qué se conoce el valor de la UF por adelantado?",
     "Porque depende de un dato que ya se publicó: el IPC. Cuando el INE informa el IPC (cerca del "
     "día 8 de cada mes), quedan determinados los valores diarios de la UF hasta el día 9 del mes "
     "siguiente."),
    ("¿La UF puede bajar?",
     "Sí. Si el IPC de un mes es negativo, la UF baja levemente durante el período siguiente."),
    ("¿Cómo convierto UF a pesos?",
     "Multiplica la cantidad de UF por el valor de la UF del día. Por ejemplo, 10 UF equivalen a "
     "10 veces el valor diario de la UF. Puedes usar el conversor de esta página."),
]


def paginas_uf(c: Contexto) -> list[Pagina]:
    hoy = c.hoy
    uf = c.datos.uf_completa()
    ultimo_conocido = max(uf)
    _, fin_periodo = periodo_uf(hoy)
    proximos = [(f, v) for f, v in uf.items() if hoy <= f <= ultimo_conocido]
    hace_un_anio = un_anio_antes(hoy)
    puntos_anio = [(f, v) for f, v in uf.items() if hace_un_anio <= f <= ultimo_conocido]
    meses = meses_de(uf)
    anio_actual = [m for m in meses if m.year == hoy.year]
    base, _ = periodo_uf(hoy)
    ipc_vigente = c.datos.ipc.get(mes_anterior(base))
    paginas = [Pagina(
        ruta="/uf/",
        plantilla="uf.html",
        titulo=f"Valor UF hoy {dia_mes(hoy)}: {pesos(c.uf_hoy, 2)}",
        descripcion=(f"La UF hoy, {fecha_con_dia(hoy)}, vale {pesos(c.uf_hoy, 2)}. Revisa los "
                     f"valores de la UF hasta el {fecha_larga(ultimo_conocido)}, el gráfico del "
                     "último año y convierte UF a pesos al instante."),
        h1="Valor UF hoy",
        migas=[INICIO, ("UF", "/uf/")],
        faq=FAQ_UF,
        prioridad=1.0,
        clave="uf",
        contexto={
            "proximos": proximos,
            "ultimo_conocido": ultimo_conocido,
            "fin_periodo": fin_periodo,
            "ipc_vigente": ipc_vigente,
            "mes_ipc_vigente": mes_anterior(base),
            "grafico": grafico_linea(puntos_anio, "Valor de la UF en los últimos 12 meses", decimales=0),
            "variacion_anual": variacion(c.uf_hoy, uf.get(hace_un_anio)),
            "meses_anio": anio_actual,
            "primeros_meses": [min(m for m in meses if m.year == anio)
                               for anio in sorted({m.year for m in meses}, reverse=True) if anio != hoy.year],
            "montos": MONTOS_UF,
        },
        datos_js={"uf": ventana(uf, hoy - dt.timedelta(days=3))},
    )]

    # Archivo mensual: "Valor UF octubre 2026"
    for mes in meses:
        dias = [(f, v) for f, v in uf.items() if primer_dia(f) == mes]
        if not dias:
            continue
        completo = len(dias) == dias_del_mes(mes.year, mes.month)
        previo = mes_anterior(mes)
        siguiente = mes_siguiente(mes)
        ipc_primera = c.datos.ipc.get(mes_anterior(previo))   # días 1 al 9
        ipc_segunda = c.datos.ipc.get(previo)                 # días 10 al fin de mes
        es_futuro = mes > primer_dia(hoy)
        paginas.append(Pagina(
            ruta=ruta_mes("uf", mes),
            plantilla="uf_mes.html",
            titulo=f"Valor UF {mes_anio(mes.year, mes.month)}: tabla diaria",
            descripcion=(f"Valores diarios de la UF en {mes_de_anio(mes.year, mes.month)}: "
                         f"el {dia_mes(dias[0][0])} vale {pesos(dias[0][1], 2)} y el "
                         f"{dia_mes(dias[-1][0])} {pesos(dias[-1][1], 2)}. Tabla completa día a día."),
            h1=f"Valor UF {mes_anio(mes.year, mes.month)}",
            migas=[INICIO, ("UF", "/uf/"), (f"UF {mes_anio(mes.year, mes.month)}", ruta_mes("uf", mes))],
            clave="uf",
            prioridad=0.8 if mes.year >= hoy.year else 0.4,
            frecuencia="daily" if mes >= mes_anterior(hoy) else "yearly",
            modificada=min(hoy, dias[-1][0]) if mes >= mes_anterior(hoy) else dias[-1][0],
            contexto={
                "mes": mes,
                "dias": dias,
                "completo": completo,
                "es_futuro": es_futuro,
                "variacion_mes": variacion(dias[-1][1], c.datos.uf_dia(previo.replace(day=dias_del_mes(previo.year, previo.month)))),
                "ipc_primera": ipc_primera,
                "ipc_segunda": ipc_segunda,
                "mes_ipc_primera": mes_anterior(previo),
                "mes_ipc_segunda": previo,
                "calculados": {f for f, _ in dias if f in c.datos.uf_calculada},
                "anterior": previo if previo in meses else None,
                "siguiente": siguiente if siguiente in meses else None,
                "meses_del_anio": [m for m in meses if m.year == mes.year],
            },
        ))

    # Montos: "1000 UF en pesos"
    primeros_de_mes = []
    mes = primer_dia(hoy)
    for _ in range(12):
        valor = uf.get(mes)
        if valor:
            primeros_de_mes.append((mes, valor))
        mes = mes_anterior(mes)
    tasa = c.p["tasa_hipotecaria_referencia"]
    for monto in MONTOS_UF:
        ejemplo = None
        if monto >= 500:
            ejemplo = calculos.simular_hipotecario(monto, 0.2, tasa, 25, c.p)
        paginas.append(Pagina(
            ruta=f"/uf/{monto}-uf-en-pesos/",
            plantilla="uf_monto.html",
            titulo=f"{numero(monto)} UF en pesos hoy: {pesos(monto * c.uf_hoy)}",
            descripcion=(f"{numero(monto)} UF equivalen hoy, {fecha_larga(hoy)}, a "
                         f"{pesos(monto * c.uf_hoy)} pesos chilenos. Mira cuánto valdrán en los "
                         "próximos días y en los últimos 12 meses."),
            h1=f"{numero(monto)} UF en pesos chilenos",
            migas=[INICIO, ("UF", "/uf/"), (f"{numero(monto)} UF en pesos", f"/uf/{monto}-uf-en-pesos/")],
            clave="uf",
            prioridad=0.7,
            contexto={
                "monto": monto,
                "proximos": proximos,
                "historia": primeros_de_mes,
                "ejemplo": ejemplo,
                "tasa_referencia": tasa,
                "vecinos": vecinos(MONTOS_UF, monto),
            },
            datos_js={"uf": ventana(uf, hoy - dt.timedelta(days=3)), "monto": monto},
        ))
    return paginas


def paginas_uf_proyeccion(c: Contexto) -> list[Pagina]:
    """UF proyectada: los valores ya conocidos más tres escenarios de inflación."""
    hoy = c.hoy
    uf = c.datos.uf_completa()
    ultimo = max(uf)
    base = max(f for f in uf if f.day == 9)
    uf_base = uf[base]
    ultimos_12 = [c.datos.ipc[m] for m in sorted(c.datos.ipc)[-12:]]
    central = calculos.variacion_acumulada(ultimos_12)
    escenarios = {"baja": max(central - 0.01, -0.02), "central": central, "alta": central + 0.01}

    def proyectar(fecha: dt.date) -> dict:
        if fecha in uf:
            return {"fecha": fecha, "conocida": True, **{k: uf[fecha] for k in escenarios}}
        return {"fecha": fecha, "conocida": False,
                **{k: uf_proyectada(base, uf_base, inflacion, fecha) for k, inflacion in escenarios.items()}}

    filas = []
    fecha = primer_dia(hoy).replace(day=9)
    if fecha < hoy:
        fecha = mes_siguiente(fecha).replace(day=9)
    for _ in range(13):
        filas.append(proyectar(fecha))
        fecha = mes_siguiente(fecha).replace(day=9)
    cierre = dt.date(hoy.year, 12, 31) if hoy.month < 12 else dt.date(hoy.year + 1, 12, 31)
    cierre_anio = proyectar(cierre)
    historia = [(f, v) for f, v in uf.items() if un_anio_antes(hoy) <= f <= ultimo]
    proyeccion = [(f["fecha"], f["central"]) for f in filas if f["fecha"] > ultimo]
    return [Pagina(
        ruta="/uf/proyeccion/",
        plantilla="uf_proyeccion.html",
        titulo=f"UF proyectada {hoy.year}-{hoy.year + 1}: cuánto valdrá la UF mes a mes",
        descripcion=(f"Proyección de la UF para los próximos 12 meses: al {fecha_larga(cierre)} "
                     f"llegaría a cerca de {pesos(cierre_anio['central'])} en el escenario central. "
                     f"Valores oficiales conocidos hasta el {fecha_larga(ultimo)}."),
        h1="UF proyectada: ¿cuánto valdrá la UF?",
        migas=[INICIO, ("UF", "/uf/"), ("UF proyectada", "/uf/proyeccion/")],
        clave="uf",
        prioridad=0.9,
        frecuencia="weekly",
        faq=[
            (f"¿Cuánto valdrá la UF en diciembre de {cierre.year}?",
             f"Si la inflación se mantiene como en los últimos 12 meses, la UF del {fecha_larga(cierre)} "
             f"sería de unos {pesos(cierre_anio['central'])}, en un rango de "
             f"{pesos(cierre_anio['baja'])} a {pesos(cierre_anio['alta'])} según nuestros escenarios."),
            ("¿Por qué no se puede saber con exactitud?",
             "Porque la UF depende del IPC de cada mes, que se conoce recién cuando lo publica el "
             "INE. Por eso solo los valores hasta el día 9 del mes siguiente son definitivos."),
            ("¿Cada cuánto se actualiza esta proyección?",
             "Automáticamente, cada vez que se publica un nuevo IPC: los escenarios se recalculan con "
             "la inflación de los últimos 12 meses."),
        ],
        contexto={
            "filas": filas,
            "ultimo_oficial": ultimo,
            "cierre_anio": cierre_anio,
            "anual_central": escenarios["central"],
            "anual_baja": escenarios["baja"],
            "anual_alta": escenarios["alta"],
            "grafico": grafico_linea(historia, "UF de los últimos 12 meses y proyección central",
                                     decimales=0, con_dia=False, proyeccion=proyeccion),
        },
    )]


# ---------------------------------------------------------------------------
# Dólar y euro
# ---------------------------------------------------------------------------

FAQ_DOLAR = [
    ("¿Qué es el dólar observado?",
     "Es el tipo de cambio que publica el Banco Central de Chile cada día hábil, calculado con las "
     "operaciones de compra y venta de dólares del mercado formal del día hábil anterior. Es el "
     "valor de referencia para contratos, declaraciones de impuestos y aduanas."),
    ("¿Por qué el dólar de mi banco o casa de cambio es distinto?",
     "Bancos y casas de cambio aplican su propio precio de compra y de venta, con un margen "
     "sobre el dólar observado. Para operaciones reales, consulta siempre el valor de tu "
     "institución."),
    ("¿Hay dólar observado los fines de semana?",
     "No. El Banco Central lo publica solo en días hábiles. En fines de semana y feriados se "
     "considera el último valor publicado."),
    ("¿Cómo convierto dólares a pesos chilenos?",
     "Multiplica la cantidad de dólares por el valor del dólar observado. Para convertir pesos a "
     "dólares, divide el monto en pesos por ese mismo valor."),
]


def _paginas_divisa(c: Contexto, clave: str, nombre: str, plural: str, simbolo: str,
                    montos: list[int], con_archivo: bool, faq: list) -> list[Pagina]:
    hoy = c.hoy
    serie = getattr(c.datos, clave)
    fecha, valor = Datos.ultimo(serie, hoy)
    anterior = Datos.anterior(serie, fecha)
    hace_un_anio = valor_cercano(serie, un_anio_antes(fecha))
    ultimos_30 = [(f, v) for f, v in serie.items() if f <= hoy][-30:]
    puntos_anio = [(f, v) for f, v in serie.items() if un_anio_antes(hoy) <= f <= hoy]
    del_anio = [v for f, v in serie.items() if f.year == hoy.year and f <= hoy]
    meses = [m for m in meses_de(serie) if m <= primer_dia(hoy)]
    ruta_base = f"/{clave}/"
    titulo_nombre = capitalizar(nombre)
    paginas = [Pagina(
        ruta=ruta_base,
        plantilla="divisa.html",
        titulo=f"{titulo_nombre} hoy en Chile: {pesos(valor, 2)} ({dia_mes(fecha)})",
        descripcion=(f"El {nombre} observado hoy en Chile vale {pesos(valor, 2)} "
                     f"({fecha_larga(fecha)}). Revisa su variación, el gráfico del último año, "
                     f"los valores de los últimos 30 días y convierte {plural} a pesos."),
        h1=f"{titulo_nombre} hoy en Chile",
        migas=[INICIO, (titulo_nombre, ruta_base)],
        faq=faq,
        prioridad=0.9,
        clave=clave,
        contexto={
            "divisa": {"clave": clave, "nombre": nombre, "plural": plural, "simbolo": simbolo},
            "fecha": fecha,
            "valor": valor,
            "variacion": variacion(valor, anterior[1] if anterior else None),
            "anterior": anterior,
            "variacion_anual": variacion(valor, hace_un_anio[1] if hace_un_anio else None),
            "ultimos_30": list(reversed(ultimos_30)),
            "maximo_anio": max(del_anio) if del_anio else None,
            "minimo_anio": min(del_anio) if del_anio else None,
            "promedio_anio": sum(del_anio) / len(del_anio) if del_anio else None,
            "grafico": grafico_linea(puntos_anio, f"{titulo_nombre} observado en los últimos 12 meses",
                                     decimales=0),
            "meses": list(reversed(meses))[:24] if con_archivo else [],
            "montos": montos,
        },
    )]

    if con_archivo:
        for mes in meses:
            dias = [(f, v) for f, v in serie.items() if primer_dia(f) == mes and f <= hoy]
            if not dias:
                continue
            valores = [v for _, v in dias]
            previo, siguiente = mes_anterior(mes), mes_siguiente(mes)
            paginas.append(Pagina(
                ruta=ruta_mes(clave, mes),
                plantilla="divisa_mes.html",
                titulo=f"{titulo_nombre} observado {mes_anio(mes.year, mes.month)}: valores y promedio",
                descripcion=(f"{titulo_nombre} observado en {mes_de_anio(mes.year, mes.month)}: "
                             f"promedio {pesos(sum(valores) / len(valores), 2)}, máximo "
                             f"{pesos(max(valores), 2)} y mínimo {pesos(min(valores), 2)}. "
                             "Tabla con el valor de cada día hábil."),
                h1=f"{titulo_nombre} observado {mes_anio(mes.year, mes.month)}",
                migas=[INICIO, (titulo_nombre, ruta_base),
                       (mes_anio(mes.year, mes.month), ruta_mes(clave, mes))],
                clave=clave,
                prioridad=0.6 if mes.year >= hoy.year else 0.3,
                frecuencia="daily" if mes == primer_dia(hoy) else "yearly",
                modificada=dias[-1][0],
                contexto={
                    "divisa": {"clave": clave, "nombre": nombre, "plural": plural},
                    "mes": mes,
                    "dias": dias,
                    "promedio": sum(valores) / len(valores),
                    "maximo": max(dias, key=lambda d: d[1]),
                    "minimo": min(dias, key=lambda d: d[1]),
                    "en_curso": mes == primer_dia(hoy),
                    "anterior": previo if previo in meses else None,
                    "siguiente": siguiente if siguiente in meses else None,
                },
            ))

    for monto in montos:
        ruta = f"/{clave}/{monto}-{plural}-en-pesos/"
        paginas.append(Pagina(
            ruta=ruta,
            plantilla="divisa_monto.html",
            titulo=f"{numero(monto)} {plural} en pesos chilenos hoy: {pesos(monto * valor)}",
            descripcion=(f"{numero(monto)} {plural} equivalen a {pesos(monto * valor)} pesos "
                         f"chilenos según el {nombre} observado del {fecha_larga(fecha)} "
                         f"({pesos(valor, 2)}). Revisa cómo ha cambiado en el último año."),
            h1=f"{numero(monto)} {plural} en pesos chilenos",
            migas=[INICIO, (titulo_nombre, ruta_base), (f"{numero(monto)} {plural} en pesos", ruta)],
            clave=clave,
            prioridad=0.6,
            contexto={
                "divisa": {"clave": clave, "nombre": nombre, "plural": plural, "simbolo": simbolo},
                "monto": monto,
                "fecha": fecha,
                "valor": valor,
                "ultimos": list(reversed(ultimos_30))[:10],
                "hace_un_anio": hace_un_anio,
                "vecinos": vecinos(montos, monto),
            },
        ))
    return paginas


def paginas_divisas(c: Contexto) -> list[Pagina]:
    faq_euro = [
        ("¿De dónde sale el valor del euro?",
         "Es el tipo de cambio del euro en pesos chilenos que publica el Banco Central de Chile "
         "cada día hábil, a partir del dólar observado y la paridad del euro."),
        ("¿Cómo convierto euros a pesos chilenos?",
         "Multiplica la cantidad de euros por el valor del euro del día. Las casas de cambio y "
         "bancos aplican además su propio margen."),
    ]
    return (_paginas_divisa(c, "dolar", "dólar", "dolares", "US$", MONTOS_DOLAR, True, FAQ_DOLAR)
            + _paginas_divisa(c, "euro", "euro", "euros", "€", MONTOS_EURO, False, faq_euro))


# ---------------------------------------------------------------------------
# UTM, impuesto único e IPC
# ---------------------------------------------------------------------------

def tabla_impuesto_pesos(p: dict, utm: float) -> list[dict]:
    filas = []
    desde = 0.0
    for tramo in p["tramos_impuesto"]:
        hasta = None if tramo["hasta"] is None else tramo["hasta"] * utm
        filas.append({
            "desde": desde,
            "hasta": hasta,
            "factor": tramo["factor"],
            "rebaja": tramo["rebaja"] * utm,
            "tasa_efectiva_max": (None if hasta is None
                                  else (hasta * tramo["factor"] - tramo["rebaja"] * utm) / hasta),
        })
        desde = hasta or desde
    return filas


def paginas_utm_impuesto_ipc(c: Contexto) -> list[Pagina]:
    hoy = c.hoy
    utm = c.datos.utm_completa()
    mes_actual = primer_dia(hoy)
    proximo_mes = mes_siguiente(hoy)
    utm_proximo = utm.get(proximo_mes)
    anios = sorted({m.year for m in utm}, reverse=True)
    paginas = [Pagina(
        ruta="/utm/",
        plantilla="utm.html",
        titulo=f"UTM {mes_anio(hoy.year, hoy.month)}: {pesos(c.utm_hoy)} | Valor UTM y UTA",
        descripcion=(f"La UTM de {mes_de_anio(hoy.year, hoy.month)} es {pesos(c.utm_hoy)} y la "
                     f"UTA {pesos(c.utm_hoy * 12)}. Tabla de la UTM {hoy.year}, conversor de UTM "
                     "a pesos y para qué se usa."),
        h1=f"UTM {mes_anio(hoy.year, hoy.month)}",
        migas=[INICIO, ("UTM", "/utm/")],
        prioridad=0.9,
        frecuencia="weekly",
        clave="utm",
        faq=[
            ("¿Qué es la UTM?",
             "La Unidad Tributaria Mensual (UTM) es una unidad de cuenta que se usa para "
             "determinar impuestos, multas, aranceles y otros montos fijados por ley. Su valor "
             "cambia cada mes según la inflación."),
            ("¿Cómo se reajusta la UTM?",
             "Cada mes se reajusta según la variación del IPC de dos meses antes. Por ejemplo, "
             "la UTM de noviembre es la de octubre reajustada por el IPC de septiembre."),
            ("¿Qué es la UTA?",
             "La Unidad Tributaria Anual (UTA) equivale a 12 veces la UTM del mes. Se usa para "
             "obligaciones tributarias anuales, como algunos límites de la Operación Renta."),
        ],
        contexto={
            "utm_proximo": utm_proximo,
            "proximo_mes": proximo_mes,
            "proximo_calculado": proximo_mes in c.datos.utm_calculada,
            "tabla": [(m, v) for m, v in utm.items() if m.year == hoy.year],
            "ipc_de": {m: c.datos.ipc.get(mes_anterior(mes_anterior(m))) for m in utm},
            "anios": anios,
        },
    )]
    for anio in anios:
        filas = [(m, v) for m, v in utm.items() if m.year == anio]
        paginas.append(Pagina(
            ruta=f"/utm/{anio}/",
            plantilla="utm_anio.html",
            titulo=f"UTM {anio}: valores de la UTM y UTA mes a mes",
            descripcion=(f"Tabla con el valor de la UTM y la UTA de cada mes de {anio}, con el "
                         "IPC usado en cada reajuste."),
            h1=f"UTM {anio}",
            migas=[INICIO, ("UTM", "/utm/"), (f"UTM {anio}", f"/utm/{anio}/")],
            prioridad=0.6 if anio >= hoy.year else 0.3,
            frecuencia="monthly" if anio >= hoy.year else "yearly",
            clave="utm",
            contexto={
                "anio": anio,
                "filas": filas,
                "ipc_de": {m: c.datos.ipc.get(mes_anterior(mes_anterior(m))) for m, _ in filas},
                "calculados": {m for m, _ in filas if m in c.datos.utm_calculada},
                "anios": anios,
            },
        ))

    tablas = [{"mes": mes_actual, "utm": c.utm_hoy, "filas": tabla_impuesto_pesos(c.p, c.utm_hoy)}]
    if utm_proximo:
        tablas.append({"mes": proximo_mes, "utm": utm_proximo,
                       "filas": tabla_impuesto_pesos(c.p, utm_proximo)})
    paginas.append(Pagina(
        ruta="/impuesto-unico/",
        plantilla="impuesto_unico.html",
        titulo=f"Tabla impuesto único {mes_anio(hoy.year, hoy.month)} (segunda categoría)",
        descripcion=(f"Tabla del Impuesto Único de Segunda Categoría de "
                     f"{mes_de_anio(hoy.year, hoy.month)} en pesos: tramos, factor y cantidad a "
                     f"rebajar con la UTM de {pesos(c.utm_hoy)}. Exento hasta "
                     f"{pesos(13.5 * c.utm_hoy)} de renta líquida imponible."),
        h1=f"Tabla de impuesto único {mes_anio(hoy.year, hoy.month)}",
        migas=[INICIO, ("Impuesto único", "/impuesto-unico/")],
        prioridad=0.8,
        frecuencia="weekly",
        clave="sueldo",
        faq=[
            ("¿A quién se le aplica el impuesto único de segunda categoría?",
             "A los trabajadores dependientes (con contrato) y pensionados. Lo retiene y paga el "
             "empleador cada mes, sobre la remuneración después de descontar las cotizaciones "
             "obligatorias de AFP, salud y seguro de cesantía."),
            ("¿Cómo se calcula con la tabla?",
             "Busca el tramo que corresponde a tu base imponible, multiplícala por el factor y "
             "resta la cantidad a rebajar. El resultado es el impuesto del mes."),
            ("¿Desde qué sueldo se paga impuesto?",
             f"Este mes, la base tributable está exenta hasta {pesos(13.5 * c.utm_hoy)} "
             "(13,5 UTM). Como la base es el sueldo menos cotizaciones, el sueldo bruto exento es "
             "algo mayor."),
        ],
        contexto={"tablas": tablas},
    ))

    meses_ipc = sorted(c.datos.ipc)
    ultimos_24 = [(m, c.datos.ipc[m]) for m in meses_ipc[-24:]]
    acumulado_12 = []
    for m in meses_ipc[-24:]:
        acumulado_12.append((m, ipc_12_meses(c, m)))
    paginas.append(Pagina(
        ruta="/ipc/",
        plantilla="ipc.html",
        titulo=f"IPC {mes_anio(c.ipc[0].year, c.ipc[0].month)}: {porcentaje(c.ipc[1], 1, True)} | IPC Chile",
        descripcion=(f"El IPC de {mes_de_anio(c.ipc[0].year, c.ipc[0].month)} fue "
                     f"{porcentaje(c.ipc[1], 1, True)}. Inflación acumulada en 12 meses: "
                     f"{porcentaje(ipc_12_meses(c), 1)}. Tabla de los últimos 24 meses y gráfico."),
        h1="IPC en Chile: variación mensual e inflación",
        migas=[INICIO, ("IPC", "/ipc/")],
        prioridad=0.8,
        frecuencia="weekly",
        clave="ipc",
        faq=[
            ("¿Qué es el IPC?",
             "El Índice de Precios al Consumidor (IPC) mide la variación mensual de los precios "
             "de una canasta de bienes y servicios que consumen los hogares. Lo publica el "
             "Instituto Nacional de Estadísticas (INE)."),
            ("¿Cuándo se publica el IPC?",
             "El INE publica el IPC de cada mes alrededor del día 8 del mes siguiente."),
            ("¿Para qué sirve el IPC?",
             "Se usa para medir la inflación y para reajustar la UF, la UTM, arriendos, pensiones "
             "alimenticias, deudas y muchos contratos."),
        ],
        contexto={
            "ultimos_24": list(reversed(ultimos_24)),
            "acumulado_12": dict(acumulado_12),
            "ipc_12m": ipc_12_meses(c),
            "ipc_anio": ipc_en_el_anio(c),
            "grafico": grafico_barras([(m, v * 100) for m, v in ultimos_24],
                                      "Variación mensual del IPC en los últimos 24 meses"),
        },
    ))
    return paginas


# ---------------------------------------------------------------------------
# Sueldo líquido
# ---------------------------------------------------------------------------

FAQ_SUELDO = [
    ("¿Qué es el sueldo líquido?",
     "Es lo que efectivamente recibes en tu cuenta: el sueldo bruto más las asignaciones no "
     "imponibles (colación, movilización), menos los descuentos legales de AFP, salud, seguro de "
     "cesantía e impuesto único."),
    ("¿Qué descuentos se hacen al sueldo bruto?",
     "La cotización de AFP (10% más la comisión de tu AFP), salud (7% en Fonasa o el valor de tu "
     "plan de isapre si es mayor), seguro de cesantía (0,6% si tu contrato es indefinido) y el "
     "impuesto único de segunda categoría si tu sueldo supera el tramo exento."),
    ("¿Qué es el tope imponible?",
     "Es el monto máximo sobre el cual se calculan las cotizaciones de AFP y salud. Lo que ganes "
     "por sobre ese tope no paga esas cotizaciones, aunque sí paga impuesto."),
    ("¿El cálculo es exacto?",
     "Es una estimación con los parámetros legales vigentes. Tu liquidación puede variar por "
     "bonos, horas extra, licencias, anticipos, APV, asignación familiar u otros descuentos."),
]


def paginas_sueldo(c: Contexto) -> list[Pagina]:
    p = c.p
    barata = calculos.afp_mas_barata(p)
    nombres = p["nombres_afp"]
    ejemplos = []
    for bruto in SUELDOS:
        r = calculos.sueldo_liquido(bruto, p, afp=barata)
        ejemplos.append((bruto, r["liquido"]))
    tope_pesos = p["tope_imponible_uf"] * p["uf"]
    descripcion_calc = ("Calcula tu sueldo líquido a partir del bruto, o cuánto bruto necesitas "
                        "para un líquido, con las comisiones de AFP, topes y tabla de impuesto "
                        "vigentes.")
    paginas = [Pagina(
        ruta="/calculadoras/sueldo-liquido/",
        plantilla="calc_sueldo.html",
        titulo=f"Calculadora de sueldo líquido {c.hoy.year} (bruto a líquido y líquido a bruto)",
        descripcion=descripcion_calc + f" Actualizada al {fecha_larga(c.hoy)}.",
        h1="Calculadora de sueldo líquido",
        migas=[INICIO, ("Calculadoras", "/calculadoras/"), ("Sueldo líquido", "/calculadoras/sueldo-liquido/")],
        faq=FAQ_SUELDO,
        clave="sueldo",
        calculadora=True,
        prioridad=1.0,
        jsonld=_app(c, "Calculadora de sueldo líquido", descripcion_calc, "/calculadoras/sueldo-liquido/"),
        datos_js={"parametros": p},
        contexto={
            "parametros": p,
            "inicial": calculos.sueldo_liquido(1_000_000, p, afp=barata),
            "costo": calculos.costo_empleador(1_000_000, p),
            "afps": sorted(p["comisiones_afp"].items(), key=lambda x: x[1]),
            "barata": barata,
            "tope_pesos": tope_pesos,
            "tope_afc_pesos": p["tope_cesantia_uf"] * p["uf"],
            "tabla_impuesto": tabla_impuesto_pesos(p, p["utm"]),
            "ejemplos": ejemplos,
        },
    )]

    for indice, bruto in enumerate(SUELDOS):
        por_afp = []
        for clave, comision in sorted(p["comisiones_afp"].items(), key=lambda x: x[1]):
            r = calculos.sueldo_liquido(bruto, p, afp=clave)
            por_afp.append({"clave": clave, "nombre": nombres[clave], "comision": comision,
                            "afp": r["afp"], "liquido": r["liquido"]})
        detalle = calculos.sueldo_liquido(bruto, p, afp=barata)
        plazo_fijo = calculos.sueldo_liquido(bruto, p, afp=barata, contrato="plazo_fijo")
        inverso = calculos.bruto_para_liquido(bruto, p, afp=barata)
        costo = calculos.costo_empleador(bruto, p)
        ruta = f"/sueldo-liquido/{bruto}/"
        texto = f"{pesos(bruto)} bruto"
        paginas.append(Pagina(
            ruta=ruta,
            plantilla="sueldo_monto.html",
            titulo=f"Sueldo líquido de {pesos(bruto)} bruto en {c.hoy.year}",
            descripcion=(f"Con un sueldo de {texto}, tu líquido es de aprox. "
                         f"{pesos(detalle['liquido'])} con AFP {nombres[barata]} y Fonasa. Mira el "
                         "detalle de descuentos y cuánto recibirías en cada AFP."),
            h1=f"Sueldo líquido de {pesos(bruto)} bruto",
            migas=[INICIO, ("Calculadoras", "/calculadoras/"),
                   ("Sueldo líquido", "/calculadoras/sueldo-liquido/"), (texto, ruta)],
            clave="sueldo",
            prioridad=0.7,
            frecuencia="weekly",
            contexto={
                "bruto": bruto,
                "monto_corto": monto_corto(bruto),
                "por_afp": por_afp,
                "detalle": detalle,
                "plazo_fijo": plazo_fijo,
                "inverso": inverso,
                "costo": costo,
                "barata": nombres[barata],
                "tope_pesos": tope_pesos,
                "anterior": SUELDOS[indice - 1] if indice > 0 else None,
                "siguiente": SUELDOS[indice + 1] if indice + 1 < len(SUELDOS) else None,
                "vecinos": vecinos(SUELDOS, bruto),
            },
        ))

    imm = c.params.vigente("ingreso_minimo", c.hoy)
    historial = [e for e in c.params.historial("ingreso_minimo")]
    liquido_minimo = calculos.sueldo_liquido(imm["monto"], p, afp=barata)
    liquido_minimo_plazo = calculos.sueldo_liquido(imm["monto"], p, afp=barata, contrato="plazo_fijo")
    paginas.append(Pagina(
        ruta="/sueldo-minimo/",
        plantilla="sueldo_minimo.html",
        titulo=f"Sueldo mínimo {c.hoy.year} en Chile: {pesos(imm['monto'])} (bruto y líquido)",
        descripcion=(f"El ingreso mínimo mensual en Chile es {pesos(imm['monto'])} bruto desde el "
                     f"{fecha_larga(imm['desde'])}. Su líquido aproximado es "
                     f"{pesos(liquido_minimo['liquido'])}. Historial y montos especiales."),
        h1=f"Sueldo mínimo en Chile {c.hoy.year}",
        migas=[INICIO, ("Sueldo mínimo", "/sueldo-minimo/")],
        clave="sueldo",
        prioridad=0.9,
        frecuencia="weekly",
        faq=[
            ("¿Cuánto es el sueldo mínimo líquido?",
             f"Con AFP {nombres[barata]}, Fonasa y contrato indefinido, el sueldo mínimo de "
             f"{pesos(imm['monto'])} queda en aproximadamente {pesos(liquido_minimo['liquido'])} "
             "líquidos."),
            ("¿El sueldo mínimo paga impuesto?",
             "No. El sueldo mínimo está muy por debajo del tramo exento del impuesto único."),
            ("¿Cuándo sube el sueldo mínimo?",
             "Lo fija una ley, que normalmente establece reajustes en mayo y/o enero. Revisa el "
             "historial en esta página: lo actualizamos apenas se publica un nuevo valor."),
        ],
        contexto={
            "imm": imm,
            "historial": list(reversed(historial)),
            "liquido": liquido_minimo,
            "liquido_plazo": liquido_minimo_plazo,
            "gratificacion_tope": p["gratificacion_tope_imm_anual"] * p["imm"] / 12,
            "barata": nombres[barata],
        },
    ))
    return paginas


# ---------------------------------------------------------------------------
# Otras calculadoras
# ---------------------------------------------------------------------------

def paginas_calculadoras(c: Contexto) -> list[Pagina]:
    p = c.p
    hoy = c.hoy
    calculadoras = [
        ("Sueldo líquido", "/calculadoras/sueldo-liquido/",
         "De bruto a líquido y de líquido a bruto, con tu AFP y salud."),
        ("Boleta de honorarios", "/calculadoras/boleta-honorarios/",
         f"Retención {porcentaje(p['retencion_honorarios'], 2)} de {hoy.year}: bruto y líquido."),
        ("Reajuste de arriendo por IPC", "/calculadoras/reajuste-arriendo-ipc/",
         "Cuánto sube tu arriendo según la variación del IPC."),
        ("Finiquito", "/calculadoras/finiquito/",
         "Indemnización por años de servicio, aviso previo y vacaciones."),
        ("Vacaciones proporcionales", "/calculadoras/vacaciones-proporcionales/",
         "Días de feriado proporcional y cuánto te deben pagar."),
        ("Crédito hipotecario", "/calculadoras/credito-hipotecario/",
         "Dividendo en UF y en pesos, renta mínima e intereses."),
        ("Interés compuesto y ahorro", "/calculadoras/interes-compuesto/",
         "Cuánto crece tu ahorro con aportes mensuales."),
        ("Días hábiles", "/calculadoras/dias-habiles/",
         "Cuenta días hábiles entre dos fechas con los feriados de Chile."),
    ]
    paginas = [Pagina(
        ruta="/calculadoras/",
        plantilla="calculadoras.html",
        titulo="Calculadoras financieras y laborales para Chile (gratis)",
        descripcion=("Calculadoras gratuitas para Chile: sueldo líquido, finiquito, vacaciones, "
                     "boletas de honorarios, arriendo por IPC, crédito hipotecario, interés "
                     "compuesto y días hábiles, con los parámetros legales vigentes."),
        h1="Calculadoras para tus finanzas en Chile",
        migas=[INICIO, ("Calculadoras", "/calculadoras/")],
        prioridad=0.9,
        frecuencia="weekly",
        contexto={"calculadoras": calculadoras},
    )]

    tasa_h = p["retencion_honorarios"]
    historial_honorarios = c.params.historial("retencion_honorarios")
    ejemplos_honorarios = [calculos.honorarios_desde_bruto(b, p) for b in
                           (100000, 250000, 500000, 750000, 1000000, 1500000, 2000000)]
    descripcion = (f"Calcula el líquido de tu boleta de honorarios {hoy.year} con la retención de "
                   f"{porcentaje(tasa_h, 2)}, o cuánto bruto debes cobrar para recibir un monto "
                   "líquido.")
    paginas.append(Pagina(
        ruta="/calculadoras/boleta-honorarios/",
        plantilla="calc_honorarios.html",
        titulo=f"Calculadora boleta de honorarios {hoy.year}: retención {porcentaje(tasa_h, 2)}",
        descripcion=descripcion,
        h1="Calculadora de boleta de honorarios",
        migas=[INICIO, ("Calculadoras", "/calculadoras/"),
               ("Boleta de honorarios", "/calculadoras/boleta-honorarios/")],
        clave="honorarios",
        calculadora=True,
        prioridad=0.9,
        frecuencia="weekly",
        jsonld=_app(c, "Calculadora de boleta de honorarios", descripcion,
                    "/calculadoras/boleta-honorarios/"),
        datos_js={"parametros": p},
        faq=[
            ("¿Cuánto se retiene en una boleta de honorarios?",
             f"En {hoy.year} la retención es de {porcentaje(tasa_h, 2)} del monto bruto. La tasa "
             "sube cada año hasta llegar a 17% en 2028 (Ley 21.133)."),
            ("¿Para qué sirve la retención?",
             "Se usa en la Operación Renta de abril para pagar tus cotizaciones de seguridad "
             "social (pensión, salud, seguro de accidentes y otros) y el impuesto anual. Si la "
             "retención supera lo que debes pagar, el SII te devuelve la diferencia."),
            ("¿Cómo calculo el bruto para recibir un líquido determinado?",
             f"Divide el líquido por {numero(1 - tasa_h, 4)} (es decir, 1 menos la tasa de "
             "retención). La calculadora lo hace por ti y ajusta el redondeo."),
        ],
        contexto={"tasa": tasa_h, "historial": historial_honorarios, "ejemplos": ejemplos_honorarios},
    ))

    meses_ipc = sorted(c.datos.ipc)[-36:]
    ipc_js = {m.strftime("%Y-%m"): v for m, v in ((m, c.datos.ipc[m]) for m in meses_ipc)}
    ultimo = c.ipc[0]
    periodos = []
    for meses in (1, 3, 6, 12):
        lista = sorted(c.datos.ipc)[-meses:]
        if len(lista) == meses:
            periodos.append({"meses": meses, "desde": lista[0], "hasta": lista[-1],
                             "variacion": calculos.variacion_acumulada([c.datos.ipc[m] for m in lista])})
    descripcion = ("Calcula el reajuste de tu arriendo según la variación del IPC: elige el monto "
                   "y el período, y obtén el nuevo valor con el IPC publicado por el INE.")
    paginas.append(Pagina(
        ruta="/calculadoras/reajuste-arriendo-ipc/",
        plantilla="calc_arriendo.html",
        titulo=f"Calculadora de reajuste de arriendo por IPC ({mes_anio(ultimo.year, ultimo.month)})",
        descripcion=descripcion,
        h1="Calculadora de reajuste de arriendo por IPC",
        migas=[INICIO, ("Calculadoras", "/calculadoras/"),
               ("Reajuste de arriendo por IPC", "/calculadoras/reajuste-arriendo-ipc/")],
        clave="arriendo",
        calculadora=True,
        prioridad=0.9,
        frecuencia="weekly",
        jsonld=_app(c, "Calculadora de reajuste de arriendo por IPC", descripcion,
                    "/calculadoras/reajuste-arriendo-ipc/"),
        datos_js={"ipc": ipc_js},
        faq=[
            ("¿Cómo se reajusta un arriendo por IPC?",
             "Se multiplica el arriendo por la variación acumulada del IPC del período que "
             "indica el contrato (por ejemplo, los últimos 6 o 12 meses con IPC publicado)."),
            ("¿Qué meses debo considerar?",
             "Los que diga tu contrato. Lo habitual es usar los últimos meses con IPC ya "
             "publicado al momento del reajuste: el IPC de un mes se publica cerca del día 8 del "
             "mes siguiente."),
            ("¿Este cálculo es oficial?",
             "Es referencial: compone las variaciones mensuales publicadas con un decimal. Para "
             "un cálculo oficial con el índice exacto, usa la calculadora del IPC del INE."),
        ],
        contexto={"periodos": periodos, "meses": list(reversed(meses_ipc)), "ultimo": ultimo},
    ))

    anios_feriados = [hoy.year - 3, hoy.year - 2, hoy.year - 1, hoy.year, hoy.year + 1]
    feriados_set = {f.fecha for anio in anios_feriados for f in feriados_nacionales(anio, c.feriados_extra)}
    datos_finiquito = {"parametros": p, "feriados": sorted(f.isoformat() for f in feriados_set),
                       "rango": [f"{anios_feriados[0]}-01-01", f"{anios_feriados[-1]}-11-30"]}
    inicio_ejemplo = calculos.sumar_meses(hoy, -43)
    ejemplo_finiquito = calculos.finiquito(inicio_ejemplo, hoy, 1_200_000, "necesidades_empresa", p,
                                           feriados_set, aviso_dado=False)
    ejemplo_vacaciones = calculos.finiquito(calculos.sumar_meses(hoy, -8), hoy, 1_000_000, "renuncia", p,
                                            feriados_set)
    tope_indemnizacion = p["tope_indemnizacion_uf"] * p["uf"]
    descripcion = ("Calcula tu finiquito: indemnización por años de servicio, aviso previo, "
                   "vacaciones pendientes y proporcionales en días corridos, según la causal de término.")
    paginas.append(Pagina(
        ruta="/calculadoras/finiquito/",
        plantilla="calc_finiquito.html",
        titulo=f"Calculadora de finiquito {hoy.year}: indemnización y vacaciones",
        descripcion=descripcion,
        h1="Calculadora de finiquito",
        migas=[INICIO, ("Calculadoras", "/calculadoras/"), ("Finiquito", "/calculadoras/finiquito/")],
        clave="finiquito",
        calculadora=True,
        prioridad=0.9,
        frecuencia="weekly",
        jsonld=_app(c, "Calculadora de finiquito", descripcion, "/calculadoras/finiquito/"),
        datos_js=datos_finiquito,
        faq=[
            ("¿Qué incluye un finiquito?",
             "Las remuneraciones pendientes, las vacaciones (feriado) pendientes y proporcionales y, "
             "según la causal de término, la indemnización por años de servicio y la indemnización "
             "sustitutiva del aviso previo."),
            ("¿Cuándo corresponde la indemnización por años de servicio?",
             "Cuando el empleador pone término al contrato por necesidades de la empresa o por "
             "desahucio (artículo 161) y el contrato duró al menos un año. Son 30 días de la última "
             "remuneración por cada año y fracción superior a seis meses, con un máximo de 11 años "
             f"y una remuneración tope de {numero(p['tope_indemnizacion_uf'])} UF "
             f"(unos {pesos(tope_indemnizacion)} hoy)."),
            ("Si renuncio, ¿me pagan indemnización?",
             "No corresponde indemnización por años de servicio (salvo que tu contrato la pacte), "
             "pero sí te deben pagar las vacaciones pendientes y proporcionales y los días trabajados."),
            ("¿Cuál es el plazo para pagar el finiquito?",
             "El empleador debe pagarlo dentro de 10 días hábiles contados desde la separación del "
             "trabajador (artículo 177 del Código del Trabajo)."),
            ("¿Y si el despido fue injustificado?",
             "Si un tribunal declara injustificado o improcedente el despido, la indemnización por "
             "años de servicio aumenta entre 30% y 100% según la causal invocada (artículo 168)."),
        ],
        contexto={"ejemplo": ejemplo_finiquito, "inicio_ejemplo": inicio_ejemplo,
                  "tope_indemnizacion": tope_indemnizacion,
                  "parametros_tope_uf": numero(p["tope_indemnizacion_uf"])},
    ))
    descripcion = ("Calcula tus vacaciones proporcionales: días hábiles de feriado ganados, su "
                   "conversión a días corridos con los feriados reales de Chile y el monto a pagar.")
    paginas.append(Pagina(
        ruta="/calculadoras/vacaciones-proporcionales/",
        plantilla="calc_vacaciones.html",
        titulo=f"Calculadora de vacaciones proporcionales {hoy.year} (feriado proporcional)",
        descripcion=descripcion,
        h1="Calculadora de vacaciones proporcionales",
        migas=[INICIO, ("Calculadoras", "/calculadoras/"),
               ("Vacaciones proporcionales", "/calculadoras/vacaciones-proporcionales/")],
        clave="finiquito",
        calculadora=True,
        prioridad=0.8,
        frecuencia="weekly",
        jsonld=_app(c, "Calculadora de vacaciones proporcionales", descripcion,
                    "/calculadoras/vacaciones-proporcionales/"),
        datos_js=datos_finiquito,
        faq=[
            ("¿Cuántos días de vacaciones proporcionales me corresponden?",
             f"Por cada mes trabajado desde tu último aniversario ganas "
             f"{numero(p['feriado_anual_habiles'] / 12, 2)} días hábiles de feriado "
             f"({numero(p['feriado_anual_habiles'])} al año), y la parte proporcional por cada día."),
            ("¿Por qué me pagan más días de los que gané?",
             "Porque los días hábiles se convierten a días corridos: desde el día siguiente al término "
             "del contrato se cuentan los días hábiles y se suman los sábados, domingos y feriados "
             "que quedan entre medio (artículo 73). Para el feriado, el sábado siempre es inhábil."),
            ("¿Cómo se calcula el valor de cada día?",
             "Se divide la remuneración mensual por 30 y se multiplica por los días corridos."),
            ("¿Qué pasa con las vacaciones que no tomé de años anteriores?",
             "También se pagan al terminar el contrato. Ingrésalas en el campo de días pendientes."),
        ],
        contexto={"ejemplo": ejemplo_vacaciones,
                  "ejemplo_inicio": calculos.sumar_meses(hoy, -8).isoformat()},
    ))

    tasa = p["tasa_hipotecaria_referencia"]
    ejemplos_hipotecario = []
    for valor in (2000, 2500, 3000, 3500, 4000, 5000, 6000):
        for anios in (20, 25, 30):
            r = calculos.simular_hipotecario(valor, 0.2, tasa, anios, p)
            ejemplos_hipotecario.append({"valor": valor, "anios": anios, **r})
    descripcion = ("Simula tu crédito hipotecario: dividendo mensual en UF y en pesos, renta "
                   "mínima exigida, intereses totales y saldo año a año.")
    paginas.append(Pagina(
        ruta="/calculadoras/credito-hipotecario/",
        plantilla="calc_hipotecario.html",
        titulo=f"Simulador de crédito hipotecario {hoy.year}: dividendo en UF y pesos",
        descripcion=descripcion,
        h1="Simulador de crédito hipotecario",
        migas=[INICIO, ("Calculadoras", "/calculadoras/"),
               ("Crédito hipotecario", "/calculadoras/credito-hipotecario/")],
        clave="hipotecario",
        calculadora=True,
        prioridad=0.9,
        frecuencia="weekly",
        jsonld=_app(c, "Simulador de crédito hipotecario", descripcion,
                    "/calculadoras/credito-hipotecario/"),
        datos_js={"parametros": p},
        faq=[
            ("¿Cuánto pie necesito para un crédito hipotecario?",
             "Los bancos suelen financiar hasta el 80% del valor de la vivienda, por lo que el "
             "pie habitual es de 20%. Algunos programas y subsidios permiten financiar más."),
            ("¿Qué renta necesito?",
             "Muchos bancos exigen que el dividendo no supere el 25% de tu renta líquida, aunque "
             "cada institución evalúa además tu historial y otras deudas."),
            ("¿Por qué mi dividendo real es mayor?",
             "Porque el dividendo incluye seguros obligatorios (desgravamen e incendio con "
             "sismo) y, en algunos casos, comisiones. Pide siempre la cotización formal con el "
             "CAE (carga anual equivalente)."),
        ],
        contexto={"tasa": tasa, "ejemplos": ejemplos_hipotecario},
    ))

    descripcion = ("Calcula cuánto crece tu ahorro con interés compuesto: monto inicial, aportes "
                   "mensuales, rentabilidad anual y plazo. Incluye gráfico año a año.")
    escenarios = []
    for tasa_anual in (0.03, 0.05, 0.07):
        r = calculos.proyectar_ahorro(0, 100000, tasa_anual, 20)
        escenarios.append({"tasa": tasa_anual, **r})
    paginas.append(Pagina(
        ruta="/calculadoras/interes-compuesto/",
        plantilla="calc_ahorro.html",
        titulo="Calculadora de interés compuesto y ahorro mensual (Chile)",
        descripcion=descripcion,
        h1="Calculadora de interés compuesto",
        migas=[INICIO, ("Calculadoras", "/calculadoras/"),
               ("Interés compuesto", "/calculadoras/interes-compuesto/")],
        clave="ahorro",
        calculadora=True,
        prioridad=0.8,
        frecuencia="monthly",
        jsonld=_app(c, "Calculadora de interés compuesto", descripcion, "/calculadoras/interes-compuesto/"),
        faq=[
            ("¿Qué es el interés compuesto?",
             "Es ganar intereses sobre los intereses ya ganados. Con el tiempo, el crecimiento se "
             "acelera porque la base sobre la que se calculan los intereses es cada vez mayor."),
            ("¿Qué rentabilidad debo usar?",
             "Depende del instrumento y su riesgo. Una cuenta de ahorro o depósito a plazo rinde "
             "menos que un fondo de acciones, que a su vez puede tener años negativos. Las "
             "rentabilidades pasadas no garantizan las futuras."),
            ("¿El resultado considera la inflación?",
             "No: muestra montos nominales. Si quieres pensar en pesos de hoy, usa una "
             "rentabilidad real (descontando la inflación esperada) o invierte en UF."),
        ],
        contexto={"escenarios": escenarios},
    ))

    anios = [hoy.year - 1, hoy.year, hoy.year + 1]
    feriados_js = [{"fecha": f.fecha.isoformat(), "nombre": f.nombre} for anio in anios
                   for f in feriados_nacionales(anio, c.feriados_extra)]
    descripcion = ("Cuenta los días hábiles entre dos fechas o suma días hábiles a una fecha, "
                   "considerando fines de semana y feriados legales de Chile.")
    paginas.append(Pagina(
        ruta="/calculadoras/dias-habiles/",
        plantilla="calc_dias_habiles.html",
        titulo=f"Calculadora de días hábiles en Chile {hoy.year} (con feriados)",
        descripcion=descripcion,
        h1="Calculadora de días hábiles",
        migas=[INICIO, ("Calculadoras", "/calculadoras/"), ("Días hábiles", "/calculadoras/dias-habiles/")],
        clave="feriados",
        calculadora=True,
        prioridad=0.7,
        frecuencia="monthly",
        jsonld=_app(c, "Calculadora de días hábiles", descripcion, "/calculadoras/dias-habiles/"),
        datos_js={"feriados": feriados_js, "anios": anios},
        faq=[
            ("¿Qué es un día hábil?",
             "Para la mayoría de los trámites, un día hábil es de lunes a viernes, excluyendo "
             "los feriados. Algunas normas, como el Código Civil, consideran hábiles también los "
             "sábados: revisa qué norma aplica a tu plazo."),
            ("¿Se cuentan el día de inicio y el de término?",
             "En esta calculadora puedes elegirlo. En los plazos legales, por regla general el "
             "plazo empieza a correr el día siguiente a la notificación."),
        ],
        contexto={"anios": anios},
    ))
    return paginas


# ---------------------------------------------------------------------------
# Feriados
# ---------------------------------------------------------------------------

def paginas_feriados(c: Contexto) -> list[Pagina]:
    hoy = c.hoy
    paginas = []
    for anio in (hoy.year, hoy.year - 1, hoy.year + 1):
        lista = feriados_nacionales(anio, c.feriados_extra)
        actual = anio == hoy.year
        ruta = "/feriados/" if actual else f"/feriados/{anio}/"
        largos = fines_de_semana_largos(anio, c.feriados_extra)
        proximos = proximos_feriados(hoy, 3, c.feriados_extra) if actual else []
        en_dia_habil = [f for f in lista if f.fecha.weekday() < 5]
        paginas.append(Pagina(
            ruta=ruta,
            plantilla="feriados.html",
            titulo=(f"Feriados {anio} en Chile: calendario y fines de semana largos"
                    if anio >= hoy.year else f"Feriados {anio} en Chile: calendario completo"),
            descripcion=(f"Calendario de los {len(lista)} feriados de {anio} en Chile, con los "
                         f"irrenunciables y {len(largos)} fines de semana largos."
                         + (f" Próximo feriado: {proximos[0].nombre}, {fecha_con_dia(proximos[0].fecha)}."
                            if proximos else "")),
            h1=f"Feriados {anio} en Chile",
            migas=[INICIO, ("Feriados", "/feriados/")] + ([] if actual else [(str(anio), ruta)]),
            clave="feriados",
            prioridad=1.0 if actual else (0.8 if anio > hoy.year else 0.4),
            frecuencia="daily" if actual else "monthly",
            faq=[
                ("¿Qué es un feriado irrenunciable?",
                 "Es un feriado en que los trabajadores del comercio no pueden ser obligados a "
                 "trabajar, salvo excepciones como restaurantes, farmacias de turno o "
                 "servicentros. Son irrenunciables el 1 de enero, el 1 de mayo, el 18 y 19 de "
                 "septiembre y el 25 de diciembre."),
                ("¿Los feriados se pagan?",
                 "Sí. Los trabajadores con sueldo mensual reciben su remuneración completa "
                 "aunque el mes tenga feriados. Si trabajas un feriado, la ley establece "
                 "compensaciones según tu jornada y contrato."),
                ("¿El 31 de diciembre es feriado?",
                 "No es feriado legal, pero sí feriado bancario (Ley 21.791): ese día los "
                 "bancos no atienden público."),
                ("¿Qué feriados se cambian de fecha?",
                 "San Pedro y San Pablo (29 de junio) y el Encuentro de Dos Mundos (12 de "
                 "octubre) se trasladan al lunes más cercano según el día en que caen. El Día "
                 "de las Iglesias Evangélicas (31 de octubre) se mueve al viernes si cae martes o "
                 "miércoles."),
            ],
            datos_js={"feriados": [{"fecha": f.fecha.isoformat(), "nombre": f.nombre} for f in lista]
                      + ([{"fecha": f.fecha.isoformat(), "nombre": f.nombre}
                          for f in feriados_nacionales(anio + 1, c.feriados_extra)] if actual else [])},
            contexto={
                "anio": anio,
                "lista": lista,
                "regionales": feriados_regionales(anio),
                "largos": largos,
                "proximos": proximos,
                "en_dia_habil": en_dia_habil,
                "irrenunciables": [f for f in lista if f.irrenunciable],
                "otros_anios": [a for a in (hoy.year - 1, hoy.year, hoy.year + 1) if a != anio],
                "es_actual": actual,
            },
        ))
    return paginas


# ---------------------------------------------------------------------------
# Páginas institucionales
# ---------------------------------------------------------------------------

def paginas_institucionales(c: Contexto) -> list[Pagina]:
    nombre = c.cfg["sitio"]["nombre"]
    comunes = {"frecuencia": "yearly", "prioridad": 0.3, "modificada": dt.date(2026, 10, 12)}
    return [
        Pagina(ruta="/acerca/", plantilla="acerca.html", titulo=f"Quiénes somos | {nombre}",
               descripcion=f"Qué es {nombre}, de dónde salen nuestros datos y cómo hacemos los cálculos.",
               h1=f"Acerca de {nombre}", migas=[INICIO, ("Acerca de", "/acerca/")], **comunes),
        Pagina(ruta="/contacto/", plantilla="contacto.html", titulo=f"Contacto | {nombre}",
               descripcion=f"Escríbenos para reportar un error o sugerir una calculadora para {nombre}.",
               h1="Contacto", migas=[INICIO, ("Contacto", "/contacto/")], **comunes),
        Pagina(ruta="/privacidad/", plantilla="privacidad.html", titulo=f"Política de privacidad | {nombre}",
               descripcion=f"Cómo {nombre} trata los datos de sus visitantes, cookies y publicidad.",
               h1="Política de privacidad", migas=[INICIO, ("Privacidad", "/privacidad/")], **comunes),
        Pagina(ruta="/terminos/", plantilla="terminos.html", titulo=f"Términos de uso | {nombre}",
               descripcion=f"Condiciones de uso de {nombre} y alcance de la información publicada.",
               h1="Términos de uso", migas=[INICIO, ("Términos de uso", "/terminos/")], **comunes),
        Pagina(ruta="/404.html", plantilla="404.html", titulo=f"Página no encontrada | {nombre}",
               descripcion=(f"La página que buscas no existe o cambió de dirección. Revisa los "
                            f"indicadores y calculadoras de {nombre}."), h1="Página no encontrada",
               en_sitemap=False, indexar=False),
    ]


def todas_las_paginas(c: Contexto) -> list[Pagina]:
    return (paginas_inicio(c) + paginas_uf(c) + paginas_uf_proyeccion(c) + paginas_divisas(c)
            + paginas_utm_impuesto_ipc(c)
            + paginas_sueldo(c) + paginas_calculadoras(c) + paginas_feriados(c)
            + paginas_institucionales(c))
