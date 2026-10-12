"""Carga de las series descargadas (UF, dólar, euro, UTM, IPC) y valores derivados.

Las series viven en ``data/series/<indicador>.json`` como ``{"AAAA-MM-DD": valor}``.
Las mensuales (UTM e IPC) usan como clave el primer día del mes. El IPC se guarda
tal como lo publica la fuente (variación mensual en %, p. ej. 0.4) y aquí se
convierte a fracción (0.004).

La UF se conoce por adelantado: el Banco Central la reajusta día a día entre el
10 de un mes y el 9 del siguiente según el IPC del mes anterior. Por eso, apenas
el INE publica el IPC, podemos calcular la UF de todo el período siguiente con la
misma fórmula oficial (``extender_uf``). Los tests comparan esa fórmula contra
los valores oficiales descargados.
"""

from __future__ import annotations

import calendar
import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path

from .formato import redondear

SERIES = ("uf", "dolar", "euro", "utm", "ipc")
SERIES_OBLIGATORIAS = ("uf", "dolar", "utm", "ipc")  # el euro es opcional: el SII no lo publica
SERIES_MENSUALES = ("utm", "ipc")
UN_DIA = dt.timedelta(days=1)


def primer_dia(fecha: dt.date) -> dt.date:
    return fecha.replace(day=1)


def mes_anterior(fecha: dt.date) -> dt.date:
    """Primer día del mes anterior a ``fecha``."""
    return (primer_dia(fecha) - UN_DIA).replace(day=1)


def mes_siguiente(fecha: dt.date) -> dt.date:
    """Primer día del mes siguiente a ``fecha``."""
    return (primer_dia(fecha) + dt.timedelta(days=32)).replace(day=1)


def dias_del_mes(anio: int, mes: int) -> int:
    return calendar.monthrange(anio, mes)[1]


def leer_serie(ruta: Path) -> dict[dt.date, float]:
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as archivo:
        crudo = json.load(archivo)
    return {dt.date.fromisoformat(clave): float(valor) for clave, valor in crudo.items()}


def escribir_serie(ruta: Path, serie: dict[dt.date, float]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ordenada = {clave.isoformat(): valor for clave, valor in sorted(serie.items())}
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(ordenada, archivo, indent=1, ensure_ascii=False)
        archivo.write("\n")


# ---------------------------------------------------------------------------
# Metodología UF y UTM
# ---------------------------------------------------------------------------

def periodo_uf(fecha: dt.date) -> tuple[dt.date, dt.date]:
    """Devuelve (día 9 base, día 9 final) del período UF al que pertenece ``fecha``.

    El período va del día 10 de un mes al día 9 del mes siguiente. El valor del
    día 9 "base" es el punto de partida y el del día 9 final cierra el período.
    """
    if fecha.day >= 10:
        base = fecha.replace(day=9)
    else:
        base = mes_anterior(fecha).replace(day=9)
    final = mes_siguiente(base).replace(day=9)
    return base, final


def uf_segun_metodologia(fecha: dt.date, uf_dia_9: float, ipc_mes_anterior: float) -> float:
    """Valor de la UF en ``fecha`` según la fórmula del Banco Central.

    ``uf_dia_9`` es la UF del día 9 que abre el período y ``ipc_mes_anterior`` la
    variación del IPC (en fracción) del mes anterior al del inicio del período.
    """
    base, _ = periodo_uf(fecha)
    dias_periodo = dias_del_mes(base.year, base.month)
    n = (fecha - base).days
    return redondear(uf_dia_9 * (1 + ipc_mes_anterior) ** (n / dias_periodo), 2)


def extender_uf(uf_oficial: dict[dt.date, float], ipc: dict[dt.date, float],
                max_dias: int = 70) -> dict[dt.date, float]:
    """Calcula la UF de los días posteriores al último valor oficial, mientras el IPC lo permita."""
    if not uf_oficial:
        return {}
    valores = dict(uf_oficial)
    calculada: dict[dt.date, float] = {}
    dia = max(uf_oficial) + UN_DIA
    for _ in range(max_dias):
        base, _ = periodo_uf(dia)
        uf_base = valores.get(base)
        variacion = ipc.get(mes_anterior(base))
        if uf_base is None or variacion is None:
            break
        valor = uf_segun_metodologia(dia, uf_base, variacion)
        valores[dia] = valor
        calculada[dia] = valor
        dia += UN_DIA
    return calculada


def comparar_uf_con_metodologia(uf_oficial: dict[dt.date, float], ipc: dict[dt.date, float]):
    """Recalcula cada UF oficial con la fórmula. Devuelve (cantidad comparada, diferencias)."""
    comparadas = 0
    diferencias = []
    for dia, valor in sorted(uf_oficial.items()):
        base, _ = periodo_uf(dia)
        uf_base = uf_oficial.get(base)
        variacion = ipc.get(mes_anterior(base))
        if uf_base is None or variacion is None:
            continue
        calculado = uf_segun_metodologia(dia, uf_base, variacion)
        comparadas += 1
        if abs(calculado - valor) > 0.005:
            diferencias.append((dia, valor, calculado))
    return comparadas, diferencias


def uf_proyectada(fecha_base: dt.date, uf_base: float, inflacion_anual: float,
                  fecha: dt.date) -> float:
    """Proyecta la UF en ``fecha`` a partir de un día 9 conocido.

    Supone una inflación mensual constante equivalente a ``inflacion_anual`` y
    aplica la misma mecánica oficial: reajuste geométrico diario entre días 9,
    con redondeo a dos decimales al cierre de cada período.
    """
    mensual = (1 + inflacion_anual) ** (1 / 12) - 1
    valor, base = uf_base, fecha_base
    while True:
        cierre = mes_siguiente(base).replace(day=9)
        if fecha <= cierre:
            return uf_segun_metodologia(fecha, valor, mensual) if fecha > base else valor
        valor = redondear(valor * (1 + mensual), 2)
        base = cierre


def utm_segun_metodologia(utm_mes_anterior: float, ipc_dos_meses_antes: float,
                          mantener_si_ipc_negativo: bool) -> float:
    """UTM de un mes: la del mes anterior reajustada por el IPC de dos meses antes."""
    if ipc_dos_meses_antes < 0 and mantener_si_ipc_negativo:
        return utm_mes_anterior
    return redondear(utm_mes_anterior * (1 + ipc_dos_meses_antes))


def extender_utm(utm: dict[dt.date, float], ipc: dict[dt.date, float],
                 mantener_si_ipc_negativo: bool, meses: int = 2) -> dict[dt.date, float]:
    """Calcula la UTM de los meses siguientes al último valor oficial, si ya se conoce el IPC."""
    if not utm:
        return {}
    valores = dict(utm)
    calculada: dict[dt.date, float] = {}
    mes = mes_siguiente(max(utm))
    for _ in range(meses):
        anterior = valores.get(mes_anterior(mes))
        variacion = ipc.get(mes_anterior(mes_anterior(mes)))
        if anterior is None or variacion is None:
            break
        valor = utm_segun_metodologia(anterior, variacion, mantener_si_ipc_negativo)
        valores[mes] = valor
        calculada[mes] = valor
        mes = mes_siguiente(mes)
    return calculada


def comparar_utm_con_metodologia(utm: dict[dt.date, float], ipc: dict[dt.date, float],
                                 mantener_si_ipc_negativo: bool):
    comparadas = 0
    diferencias = []
    for mes, valor in sorted(utm.items()):
        anterior = utm.get(mes_anterior(mes))
        variacion = ipc.get(mes_anterior(mes_anterior(mes)))
        if anterior is None or variacion is None:
            continue
        calculado = utm_segun_metodologia(anterior, variacion, mantener_si_ipc_negativo)
        comparadas += 1
        if abs(calculado - valor) > 0.5:
            diferencias.append((mes, valor, calculado))
    return comparadas, diferencias


# ---------------------------------------------------------------------------
# Contenedor de datos
# ---------------------------------------------------------------------------

@dataclass
class Datos:
    uf: dict[dt.date, float]
    dolar: dict[dt.date, float]
    euro: dict[dt.date, float]
    utm: dict[dt.date, float]
    ipc: dict[dt.date, float]  # variación mensual en fracción, clave = primer día del mes
    uf_calculada: dict[dt.date, float] = field(default_factory=dict)
    utm_calculada: dict[dt.date, float] = field(default_factory=dict)
    ultimos: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    @property
    def demo(self) -> bool:
        return bool(self.meta.get("demo"))

    def euro_vigente(self, hoy: dt.date) -> bool:
        """Hay euro si su último dato tiene menos de 30 días (si no, se ocultan sus páginas)."""
        return bool(self.euro) and (hoy - max(self.euro)).days <= 30

    def uf_dia(self, fecha: dt.date) -> float | None:
        return self.uf.get(fecha, self.uf_calculada.get(fecha))

    def uf_completa(self) -> dict[dt.date, float]:
        return dict(sorted({**self.uf_calculada, **self.uf}.items()))

    def utm_mes(self, fecha: dt.date) -> float | None:
        mes = primer_dia(fecha)
        return self.utm.get(mes, self.utm_calculada.get(mes))

    def utm_completa(self) -> dict[dt.date, float]:
        return dict(sorted({**self.utm_calculada, **self.utm}.items()))

    @staticmethod
    def ultimo(serie: dict[dt.date, float], hasta: dt.date) -> tuple[dt.date, float] | None:
        """Último dato de ``serie`` con fecha menor o igual a ``hasta``."""
        fechas = [f for f in serie if f <= hasta]
        if not fechas:
            return None
        fecha = max(fechas)
        return fecha, serie[fecha]

    @staticmethod
    def anterior(serie: dict[dt.date, float], fecha: dt.date) -> tuple[dt.date, float] | None:
        """Dato inmediatamente anterior a ``fecha``."""
        fechas = [f for f in serie if f < fecha]
        if not fechas:
            return None
        previa = max(fechas)
        return previa, serie[previa]


def cargar_datos(directorio: Path, mantener_utm_si_ipc_negativo: bool = True) -> Datos:
    series = directorio / "series"
    ipc_porcentaje = leer_serie(series / "ipc.json")
    datos = Datos(
        uf=leer_serie(series / "uf.json"),
        dolar=leer_serie(series / "dolar.json"),
        euro=leer_serie(series / "euro.json"),
        utm={primer_dia(f): v for f, v in leer_serie(series / "utm.json").items()},
        ipc={primer_dia(f): v / 100 for f, v in ipc_porcentaje.items()},
    )
    datos.uf_calculada = extender_uf(datos.uf, datos.ipc)
    datos.utm_calculada = extender_utm(datos.utm, datos.ipc, mantener_utm_si_ipc_negativo)
    for nombre in ("ultimos", "meta"):
        ruta = directorio / f"{nombre}.json"
        if ruta.exists():
            with open(ruta, encoding="utf-8") as archivo:
                setattr(datos, nombre, json.load(archivo))
    return datos


def revisar_frescura(datos: Datos, hoy: dt.date) -> tuple[list[str], list[str]]:
    """Devuelve (errores, advertencias) sobre datos faltantes o desactualizados."""
    errores: list[str] = []
    advertencias: list[str] = []
    for nombre in SERIES_OBLIGATORIAS:
        if not getattr(datos, nombre):
            errores.append(f"No hay datos de {nombre}. Ejecuta: python -m lucas actualizar")
    if errores:
        return errores, advertencias
    if datos.uf_dia(hoy) is None:
        errores.append(f"No se conoce la UF de hoy ({hoy}). Último dato oficial: {max(datos.uf)}")
    if not datos.euro_vigente(hoy):
        advertencias.append("No hay datos recientes del euro: se omiten sus páginas "
                            "(configura CMF_API_KEY si mindicador.cl no responde)")
    for nombre, limite in (("dolar", 7), ("euro", 7)):
        if not getattr(datos, nombre):
            continue
        ultima = max(getattr(datos, nombre))
        atraso = (hoy - ultima).days
        if atraso > limite:
            advertencias.append(f"El último {nombre} es del {ultima} ({atraso} días de atraso)")
    if datos.utm_mes(hoy) is None:
        advertencias.append(f"No se conoce la UTM de {hoy:%m-%Y}")
    ultimo_ipc = max(datos.ipc)
    if (hoy - ultimo_ipc).days > 75:
        advertencias.append(f"El último IPC es de {ultimo_ipc:%m-%Y}; debería haber uno más reciente")
    return errores, advertencias
