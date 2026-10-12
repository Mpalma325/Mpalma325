"""Metodología (/metodologia/) y datos de las páginas institucionales (/acerca/, /contacto/).

Lo que dice la metodología sale del propio sistema para que no quede desactualizado: las
fuentes de ``fuentes.ORDEN_FUENTES``, la vigencia y la fuente de cada grupo de
``parametros/chile.yaml``, la comparación de las fórmulas de la UF y la UTM con los datos
oficiales descargados y el historial de ``contenido/correcciones.yaml``.

Las páginas se suman en ``paginas_institucionales`` (lucas/paginas.py).
"""

from __future__ import annotations

from .confianza import (FUENTES_OFICIALES, cargar_correcciones, como_fecha, enlazar_fuentes,
                        equipo_de, etiqueta_red, nombre_fuente, redes_de, repositorio_de, vigencia)
from .construir import Contexto, Pagina
from .datos import Datos, comparar_uf_con_metodologia, comparar_utm_con_metodologia, mes_anterior
from .fuentes import ORDEN_FUENTES, SII, SII_PAGINAS

# Quién publica cada indicador (texto con organismos que enlaza ``enlazar_fuentes``).
INDICADORES = {
    "uf": ("UF", "Banco Central de Chile, con el IPC del INE"),
    "utm": ("UTM y UTA", "Servicio de Impuestos Internos, reajustada según el IPC"),
    "ipc": ("IPC", "Instituto Nacional de Estadísticas"),
    "dolar": ("Dólar observado", "Banco Central de Chile"),
    "euro": ("Euro", "Banco Central de Chile"),
}

# De dónde descarga el sitio cada indicador (claves de ``fuentes.ORDEN_FUENTES``).
DESCARGAS = {
    "sii.cl": ("SII", True),
    "api.cmfchile.cl": ("API de la CMF", True),
    "findic.cl": ("findic.cl", False),
    "mindicador.cl": ("mindicador.cl", False),
}

# Nombre de cada grupo de parametros/chile.yaml en la tabla de la metodología. Un grupo
# nuevo sin nombre aquí aparece igual, con su clave.
PARAMETROS = {
    "afp": "Comisiones de las AFP",
    "topes_imponibles": "Topes imponibles",
    "seguro_cesantia": "Seguro de cesantía",
    "salud": "Cotización de salud",
    "ingreso_minimo": "Ingreso mínimo mensual",
    "gratificacion": "Gratificación legal",
    "impuesto_unico": "Tabla del impuesto único",
    "retencion_honorarios": "Retención de boletas de honorarios",
    "iva": "IVA",
    "impuesto_timbres": "Impuesto de timbres y estampillas",
    "apv": "Ahorro previsional voluntario (APV)",
    "cotizaciones_empleador": "Cotizaciones del empleador (SIS, reforma de pensiones y mutual)",
    "indemnizaciones": "Indemnizaciones y feriado anual",
    "jornada_laboral": "Jornada laboral y horas extra",
    "credito_hipotecario": "Tasa hipotecaria de referencia (supuesto de los ejemplos)",
    "credito_consumo": "Tasa del crédito de consumo (supuesto de los ejemplos)",
    "feriados_extra": "Feriados por elecciones y leyes especiales",
}


def contexto_institucional(c: Contexto) -> dict:
    """Equipo, redes y repositorio de config.yaml más las URL oficiales, para las plantillas."""
    return {
        "equipo": equipo_de(c.cfg),
        "redes": [(etiqueta_red(url), url) for url in redes_de(c.cfg)],
        "repositorio": repositorio_de(c.cfg),
        "oficiales": FUENTES_OFICIALES,
    }


# ---------------------------------------------------------------------------
# Datos de la metodología
# ---------------------------------------------------------------------------

def tabla_fuentes(c: Contexto) -> list[dict]:
    """Una fila por indicador con quién lo publica y de dónde lo descargamos, en orden."""
    filas = []
    for indicador, orden in ORDEN_FUENTES.items():
        nombre, publica = INDICADORES.get(indicador, (indicador.upper(), ""))
        if indicador == "euro" and c.euro is None:
            continue  # sin datos recientes del euro, el sitio no publica sus páginas
        descargas = []
        for codigo in orden:
            texto, oficial = DESCARGAS.get(codigo, (codigo, False))
            url = ""
            if codigo == "sii.cl" and indicador in SII_PAGINAS:
                url = f"{SII}/{SII_PAGINAS[indicador].format(anio=c.hoy.year)}"
            elif codigo == "api.cmfchile.cl":
                url = "https://api.cmfchile.cl/"
            descargas.append({"texto": texto, "url": url, "oficial": oficial})
        filas.append({"indicador": nombre, "publica": enlazar_fuentes(publica) if publica else "",
                      "descargas": descargas})
    return filas


def verificacion_uf(datos: Datos) -> dict | None:
    """Recalcula cada UF oficial descargada con la fórmula del Banco Central."""
    comparadas, diferencias = comparar_uf_con_metodologia(datos.uf, datos.ipc)
    if not comparadas:
        return None
    return {"comparadas": comparadas, "coinciden": comparadas - len(diferencias),
            "desde": min(datos.uf), "hasta": max(datos.uf)}


def verificacion_utm(datos: Datos, mantener: bool) -> dict | None:
    """Recalcula cada UTM oficial con el IPC de dos meses antes; cuenta los meses con IPC
    negativo y toma el más reciente como ejemplo."""
    comparadas, diferencias = comparar_utm_con_metodologia(datos.utm, datos.ipc, mantener)
    if not comparadas:
        return None
    negativos = [m for m in sorted(datos.utm)
                 if mes_anterior(m) in datos.utm and datos.ipc.get(mes_anterior(mes_anterior(m)), 0) < 0]
    ejemplo = None
    if negativos:
        mes = negativos[-1]
        mes_ipc = mes_anterior(mes_anterior(mes))
        ejemplo = {"mes": mes, "valor": datos.utm[mes], "anterior": datos.utm[mes_anterior(mes)],
                   "mes_ipc": mes_ipc, "ipc": datos.ipc[mes_ipc]}
    return {"comparadas": comparadas, "coinciden": comparadas - len(diferencias),
            "negativos": len(negativos), "ejemplo": ejemplo, "mantener": mantener}


def tabla_parametros(c: Contexto) -> list[dict]:
    """Cada grupo de parametros/chile.yaml con su vigencia, su fuente y su próxima revisión."""
    filas = []
    for grupo, valor in c.params.crudo.items():
        if not isinstance(valor, dict):
            continue
        fuente = str(valor.get("fuente") or "")
        revisar = como_fecha(valor["revisar_antes_de"]) if valor.get("revisar_antes_de") else None
        filas.append({
            "nombre": PARAMETROS.get(grupo, grupo.replace("_", " ").capitalize()),
            "vigencia": vigencia(c.params, grupo, c.hoy) if valor.get("vigencias") else None,
            "fuente": fuente,
            "nombre_fuente": nombre_fuente(fuente) if fuente else "",
            "revisar": revisar,
            "vencida": bool(revisar and revisar <= c.hoy),  # el aviso de revisión ya llegó
        })
    return filas


def pagina_metodologia(c: Contexto) -> Pagina:
    from .paginas import INICIO  # import diferido: paginas importa este módulo
    mantener = bool(c.params.get("utm_se_mantiene_con_ipc_negativo", False))
    usadas = [DESCARGAS.get(codigo, (codigo, False))[0] for codigo in c.datos.meta.get("fuentes") or []]
    return Pagina(
        ruta="/metodologia/",
        plantilla="metodologia.html",
        titulo=f"Cómo calculamos y de dónde salen los datos | {c.cfg['sitio']['nombre']}",
        descripcion=("Fuentes oficiales de la UF, la UTM, el IPC y el dólar, cada cuánto se "
                     "actualizan, qué valores son calculados, cómo verificamos las fórmulas e "
                     "historial de correcciones."),
        h1="Cómo calculamos y de dónde salen los datos",
        migas=[INICIO, ("Metodología", "/metodologia/")],
        prioridad=0.5,
        frecuencia="monthly",
        faq=[
            ("¿Los valores de este sitio son oficiales?",
             "La UF, la UTM, el IPC, el dólar observado y el euro son los valores oficiales que "
             "publican el Banco Central, el SII y el INE. Algunos valores son calculados (la UF de "
             "los días que aún no se publican, con la fórmula oficial) o proyectados (la UF de los "
             "próximos meses), y siempre lo indicamos. Los resultados de las calculadoras son "
             "estimaciones."),
            ("¿Cada cuánto se actualizan los datos?",
             "Dos veces al día, temprano en la mañana y en la tarde (hora de Chile). La fecha de la "
             "última actualización aparece al pie de cada página."),
            ("¿Qué hago si encuentro un error?",
             "Repórtalo como se explica en la página de contacto, con la dirección de la página, el "
             "valor que ves y el que esperabas. Lo revisamos contra la fuente oficial y, si "
             "corresponde, lo corregimos y lo anotamos en el historial de correcciones de esta página."),
        ],
        contexto={
            "fuentes": tabla_fuentes(c),
            "fuentes_usadas": usadas,
            "uf_oficial_hasta": max(c.datos.uf),
            "uf_calculada_hasta": max(c.datos.uf_calculada) if c.datos.uf_calculada else None,
            "verificacion_uf": verificacion_uf(c.datos),
            "verificacion_utm": verificacion_utm(c.datos, mantener),
            "parametros": tabla_parametros(c),
            "correcciones": cargar_correcciones(),
            "oficiales": FUENTES_OFICIALES,
        },
    )
