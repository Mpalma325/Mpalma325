"""Feriados legales de Chile.

Se calculan a partir de las reglas de la ley (no de una lista fija), para que
el sitio siga funcionando solo año tras año. Los feriados extraordinarios
(elecciones, feriados aprobados por leyes especiales) se agregan en
``parametros/chile.yaml`` bajo ``feriados_extra``.

Reglas implementadas:

- Viernes y Sábado Santo: dependen del Domingo de Pascua.
- Día Nacional de los Pueblos Indígenas (Ley 21.357): día del solsticio de
  invierno, según la hora de Chile continental.
- San Pedro y San Pablo (29 jun) y Encuentro de Dos Mundos (12 oct), Ley 19.668:
  si caen martes, miércoles o jueves se trasladan al lunes de esa semana; si
  caen viernes, al lunes siguiente.
- Día de las Iglesias Evangélicas y Protestantes (31 oct), Ley 20.299: si cae
  martes se traslada al viernes 27 de octubre; si cae miércoles, al viernes
  2 de noviembre.
- Fiestas Patrias, Ley 20.215: el 17 de septiembre es feriado si cae lunes y
  el 20 de septiembre si cae viernes. Ley 20.983: si el 18 y 19 caen sábado y
  domingo, el viernes 17 también es feriado.
- Año Nuevo, Ley 20.983: si el 1 de enero cae domingo, el lunes 2 es feriado.
- El 31 de diciembre es feriado bancario (Ley 21.791), no feriado legal: no se
  incluye en la lista.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass

from .config import ZONA_CHILE

UN_DIA = dt.timedelta(days=1)


@dataclass(frozen=True)
class Feriado:
    fecha: dt.date
    nombre: str
    tipo: str = "Civil"  # "Civil" o "Religioso"
    irrenunciable: bool = False
    nota: str = ""
    regional: str = ""  # región o comunas, si no es nacional


# ---------------------------------------------------------------------------
# Astronomía: Pascua y solsticio
# ---------------------------------------------------------------------------

def domingo_de_pascua(anio: int) -> dt.date:
    """Algoritmo anónimo gregoriano (Meeus/Jones/Butcher)."""
    a = anio % 19
    b, c = divmod(anio, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return dt.date(anio, mes, dia + 1)


# Términos periódicos de la tabla 27.C de "Astronomical Algorithms" (J. Meeus).
_TERMINOS_SOLSTICIO = (
    (485, 324.96, 1934.136), (203, 337.23, 32964.467), (199, 342.08, 20.186),
    (182, 27.85, 445267.112), (156, 73.14, 45036.886), (136, 171.52, 22518.443),
    (77, 222.54, 65928.934), (74, 296.72, 3034.906), (70, 243.58, 9037.513),
    (58, 119.81, 33718.147), (52, 297.17, 150.678), (50, 21.02, 2281.226),
    (45, 247.54, 29929.562), (44, 325.15, 31555.956), (29, 60.93, 4443.417),
    (18, 155.12, 67555.328), (17, 288.79, 4562.452), (16, 198.04, 62894.029),
    (14, 199.76, 31436.921), (12, 95.39, 14577.848), (12, 287.11, 31931.756),
    (12, 320.81, 34777.259), (9, 227.73, 1222.114), (8, 15.45, 16859.074),
)


def solsticio_de_junio(anio: int) -> dt.datetime:
    """Instante (UTC) del solsticio de junio, con error de pocos minutos (Meeus, cap. 27)."""
    y = (anio - 2000) / 1000
    jde0 = (2451716.56767 + 365241.62603 * y + 0.00325 * y**2
            + 0.00888 * y**3 - 0.00030 * y**4)
    t = (jde0 - 2451545.0) / 36525
    w = math.radians(35999.373 * t - 2.47)
    delta_lambda = 1 + 0.0334 * math.cos(w) + 0.0007 * math.cos(2 * w)
    s = sum(a * math.cos(math.radians(b + c * t)) for a, b, c in _TERMINOS_SOLSTICIO)
    jde = jde0 + 0.00001 * s / delta_lambda
    # Tiempo dinámico -> tiempo universal (ΔT ≈ 69 s en esta década; basta para fijar el día).
    jd_ut = jde - 69.0 / 86400
    return dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(days=jd_ut - 2440587.5)


def dia_de_los_pueblos_indigenas(anio: int) -> dt.date:
    """Día del solsticio de invierno según la hora de Chile continental (Ley 21.357)."""
    if anio == 2021:
        # Primer año de vigencia: la ley fijó el lunes 21 de junio de 2021.
        return dt.date(2021, 6, 21)
    return solsticio_de_junio(anio).astimezone(ZONA_CHILE).date()


# ---------------------------------------------------------------------------
# Reglas de traslado
# ---------------------------------------------------------------------------

def trasladar_ley_19668(fecha: dt.date) -> dt.date:
    """29 de junio y 12 de octubre: mar/mié/jue -> lunes de esa semana; viernes -> lunes siguiente."""
    dia = fecha.weekday()  # lunes = 0
    if dia in (1, 2, 3):
        return fecha - dt.timedelta(days=dia)
    if dia == 4:
        return fecha + dt.timedelta(days=3)
    return fecha


def dia_iglesias_evangelicas(anio: int) -> dt.date:
    """31 de octubre; si cae martes pasa al viernes 27, si cae miércoles al viernes 2 de noviembre."""
    fecha = dt.date(anio, 10, 31)
    if fecha.weekday() == 1:
        return dt.date(anio, 10, 27)
    if fecha.weekday() == 2:
        return dt.date(anio, 11, 2)
    return fecha


def _nota_traslado(original: dt.date, final: dt.date) -> str:
    if original == final:
        return ""
    from .formato import dia_mes
    return f"Se traslada desde el {dia_mes(original)}"


# ---------------------------------------------------------------------------
# Listas de feriados
# ---------------------------------------------------------------------------

def feriados_nacionales(anio: int, extras: list[dict] | None = None) -> list[Feriado]:
    """Feriados nacionales del año, ordenados por fecha.

    ``extras`` es la lista ``feriados_extra`` de parametros/chile.yaml: feriados
    por elecciones o leyes especiales (cada uno con fecha, nombre e irrenunciable).
    """
    pascua = domingo_de_pascua(anio)
    lista = [
        Feriado(dt.date(anio, 1, 1), "Año Nuevo", "Civil", True),
    ]
    if anio >= 2017 and dt.date(anio, 1, 1).weekday() == 6:
        lista.append(Feriado(dt.date(anio, 1, 2), "Feriado adicional de Año Nuevo", "Civil",
                             nota="Ley 20.983: el 1 de enero cae domingo"))
    lista += [
        Feriado(pascua - 2 * UN_DIA, "Viernes Santo", "Religioso"),
        Feriado(pascua - UN_DIA, "Sábado Santo", "Religioso"),
        Feriado(dt.date(anio, 5, 1), "Día Nacional del Trabajo", "Civil", True),
        Feriado(dt.date(anio, 5, 21), "Día de las Glorias Navales", "Civil"),
    ]
    if anio >= 2021:
        lista.append(Feriado(dia_de_los_pueblos_indigenas(anio),
                             "Día Nacional de los Pueblos Indígenas", "Civil"))

    san_pedro = dt.date(anio, 6, 29)
    lista.append(Feriado(trasladar_ley_19668(san_pedro), "San Pedro y San Pablo", "Religioso",
                         nota=_nota_traslado(san_pedro, trasladar_ley_19668(san_pedro))))
    lista += [
        Feriado(dt.date(anio, 7, 16), "Día de la Virgen del Carmen", "Religioso"),
        Feriado(dt.date(anio, 8, 15), "Asunción de la Virgen", "Religioso"),
    ]
    diecisiete = dt.date(anio, 9, 17)
    if diecisiete.weekday() == 0:
        lista.append(Feriado(diecisiete, "Fiestas Patrias (feriado adicional)", "Civil",
                             nota="Ley 20.215: el 18 y 19 caen martes y miércoles"))
    elif diecisiete.weekday() == 4 and anio >= 2017:
        lista.append(Feriado(diecisiete, "Fiestas Patrias (feriado adicional)", "Civil",
                             nota="Ley 20.983: el 18 y 19 caen sábado y domingo"))
    lista += [
        Feriado(dt.date(anio, 9, 18), "Independencia Nacional", "Civil", True),
        Feriado(dt.date(anio, 9, 19), "Día de las Glorias del Ejército", "Civil", True),
    ]
    if dt.date(anio, 9, 20).weekday() == 4:
        lista.append(Feriado(dt.date(anio, 9, 20), "Fiestas Patrias (feriado adicional)", "Civil",
                             nota="Ley 20.215: el 18 y 19 caen miércoles y jueves"))

    dos_mundos = dt.date(anio, 10, 12)
    lista.append(Feriado(trasladar_ley_19668(dos_mundos), "Encuentro de Dos Mundos", "Civil",
                         nota=_nota_traslado(dos_mundos, trasladar_ley_19668(dos_mundos))))
    evangelicas = dia_iglesias_evangelicas(anio)
    lista.append(Feriado(evangelicas, "Día de las Iglesias Evangélicas y Protestantes", "Religioso",
                         nota=_nota_traslado(dt.date(anio, 10, 31), evangelicas)))
    lista += [
        Feriado(dt.date(anio, 11, 1), "Día de Todos los Santos", "Religioso"),
        Feriado(dt.date(anio, 12, 8), "Inmaculada Concepción", "Religioso"),
        Feriado(dt.date(anio, 12, 25), "Navidad", "Religioso", True),
    ]

    # Feriados por elecciones o leyes especiales. Si una ley especial cambia de
    # fecha un feriado, la entrada lleva `reemplaza: "<nombre del feriado>"`.
    extras_del_anio = []
    for extra in extras or []:
        fecha = extra["fecha"]
        if not isinstance(fecha, dt.date):
            fecha = dt.date.fromisoformat(str(fecha))
        if fecha.year == anio:
            extras_del_anio.append((fecha, extra))
    reemplazados = {extra["reemplaza"] for _, extra in extras_del_anio if extra.get("reemplaza")}
    lista = [f for f in lista if f.nombre not in reemplazados]
    for fecha, extra in extras_del_anio:
        lista.append(Feriado(fecha, extra["nombre"], extra.get("tipo", "Civil"),
                             bool(extra.get("irrenunciable", False)), extra.get("nota", "")))

    lista.sort(key=lambda f: (f.fecha, f.nombre))
    return lista


def feriados_regionales(anio: int) -> list[Feriado]:
    """Feriados que solo rigen en una región o comuna."""
    return [
        Feriado(dt.date(anio, 6, 7), "Asalto y Toma del Morro de Arica", "Civil",
                regional="Región de Arica y Parinacota"),
        Feriado(dt.date(anio, 8, 20), "Nacimiento del Prócer de la Independencia", "Civil",
                regional="Comunas de Chillán y Chillán Viejo"),
    ]


def es_feriado(fecha: dt.date, extras: list[dict] | None = None) -> bool:
    return any(f.fecha == fecha for f in feriados_nacionales(fecha.year, extras))


def proximos_feriados(desde: dt.date, cantidad: int = 3, extras: list[dict] | None = None) -> list[Feriado]:
    """Los próximos feriados a partir de ``desde`` (incluido)."""
    resultado: list[Feriado] = []
    anio = desde.year
    while len(resultado) < cantidad and anio <= desde.year + 2:
        resultado += [f for f in feriados_nacionales(anio, extras) if f.fecha >= desde]
        anio += 1
    return resultado[:cantidad]


def fines_de_semana_largos(anio: int, extras: list[dict] | None = None) -> list[dict]:
    """Bloques de 3 o más días libres seguidos (sábado, domingo o feriado) que incluyen un feriado."""
    feriados = {f.fecha: f for f in feriados_nacionales(anio, extras)}
    feriados.update({f.fecha: f for f in feriados_nacionales(anio + 1, extras) if f.fecha.month == 1})

    def libre(dia: dt.date) -> bool:
        return dia.weekday() >= 5 or dia in feriados

    bloques = []
    dia = dt.date(anio, 1, 1)
    while dia.year == anio:
        if libre(dia) and not libre(dia - UN_DIA):
            fin = dia
            while libre(fin + UN_DIA):
                fin += UN_DIA
            dias = (fin - dia).days + 1
            incluidos = [feriados[d] for d in _rango(dia, fin) if d in feriados]
            if dias >= 3 and incluidos:
                bloques.append({"inicio": dia, "fin": fin, "dias": dias, "feriados": incluidos})
            dia = fin
        dia += UN_DIA
    return bloques


def _rango(inicio: dt.date, fin: dt.date):
    dia = inicio
    while dia <= fin:
        yield dia
        dia += UN_DIA


def dias_habiles_entre(inicio: dt.date, fin: dt.date, extras: list[dict] | None = None) -> int:
    """Días hábiles (lunes a viernes, sin feriados) entre dos fechas, ambas incluidas."""
    feriados: set[dt.date] = set()
    for anio in range(inicio.year, fin.year + 1):
        feriados |= {f.fecha for f in feriados_nacionales(anio, extras)}
    return sum(1 for d in _rango(inicio, fin) if d.weekday() < 5 and d not in feriados)
