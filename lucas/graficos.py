"""Gráficos SVG livianos generados en Python (sin JavaScript ni librerías externas).

Un gráfico inline pesa unos pocos KB, se ve nítido en cualquier pantalla y no
afecta la velocidad de carga, que es clave para el posicionamiento en Google.
Los colores se definen en CSS (clases ``g-*``), así funcionan en modo oscuro.
"""

from __future__ import annotations

import datetime as dt
import itertools
import math

from markupsafe import Markup, escape

from .formato import MESES, numero

_contador = itertools.count(1)

# Tamaño del viewBox. Con 480 de ancho el texto se lee en el celular (unos 10 px en una pantalla
# de 390 px); en pantallas anchas la figura llega a 760 px como máximo (.figura en estilos.css).
ANCHO, ALTO = 480, 240


def _marcas_eje(minimo: float, maximo: float, cantidad: int = 4) -> list[float]:
    """Valores "redondos" para las líneas guía del eje Y."""
    if maximo == minimo:
        return [minimo]
    paso_bruto = (maximo - minimo) / cantidad
    magnitud = 10 ** math.floor(math.log10(paso_bruto))
    for multiplo in (1, 2, 2.5, 5, 10):
        paso = multiplo * magnitud
        if paso >= paso_bruto:
            break
    inicio = math.ceil(minimo / paso) * paso
    marcas = []
    valor = inicio
    while valor <= maximo + 1e-9:
        marcas.append(round(valor, 10))
        valor += paso
    return marcas


def _etiqueta_fecha(fecha: dt.date, con_dia: bool) -> str:
    mes = MESES[fecha.month - 1][:3]
    if con_dia:
        return f"{fecha.day} {mes} {fecha.year % 100:02d}"
    return f"{mes} {fecha.year}"


def grafico_linea(puntos: list[tuple[dt.date, float]], titulo: str, decimales: int = 0,
                  prefijo: str = "$", sufijo: str = "", ancho: int = ANCHO, alto: int = ALTO,
                  con_dia: bool = True, proyeccion: list[tuple[dt.date, float]] | None = None) -> Markup:
    """Gráfico de línea con área sombreada, líneas guía y etiquetas en formato chileno.

    ``proyeccion`` agrega una segunda serie punteada (por ejemplo, la UF proyectada).
    """
    puntos = sorted(puntos)
    proyeccion = sorted(proyeccion or [])
    if len(puntos) < 2:
        return Markup("")
    identificador = f"g{next(_contador)}"
    izq, der, sup, inf = 70, 14, 14, 30
    todos = puntos + proyeccion
    fechas = [p[0].toordinal() for p in puntos]
    valores = [p[1] for p in puntos]
    vmin = min(v for _, v in todos)
    vmax = max(v for _, v in todos)
    margen = (vmax - vmin) * 0.08 or abs(vmax) * 0.01 or 1
    ymin, ymax = vmin - margen, vmax + margen
    xmin = fechas[0]
    xmax = max(fechas[-1], proyeccion[-1][0].toordinal() if proyeccion else fechas[-1])

    def x(ordinal: int) -> float:
        return izq + (ordinal - xmin) / ((xmax - xmin) or 1) * (ancho - izq - der)

    def y(valor: float) -> float:
        return sup + (ymax - valor) / (ymax - ymin) * (alto - sup - inf)

    linea = " ".join(f"{'M' if i == 0 else 'L'}{x(f):.1f},{y(v):.1f}"
                     for i, (f, v) in enumerate(zip(fechas, valores)))
    base = alto - inf
    area = f"{linea} L{x(fechas[-1]):.1f},{base} L{x(xmin):.1f},{base} Z"

    partes = [
        f'<svg class="grafico" viewBox="0 0 {ancho} {alto}" role="img" '
        f'aria-labelledby="{identificador}-t" preserveAspectRatio="xMidYMid meet">',
        f'<title id="{identificador}-t">{escape(titulo)}</title>',
    ]
    for marca in _marcas_eje(ymin, ymax):
        yy = y(marca)
        partes.append(f'<line class="g-guia" x1="{izq}" x2="{ancho - der}" y1="{yy:.1f}" y2="{yy:.1f}"/>')
        etiqueta = f"{prefijo}{numero(marca, decimales)}{sufijo}"
        partes.append(f'<text class="g-texto" x="{izq - 8}" y="{yy + 4:.1f}" text-anchor="end">'
                      f"{escape(etiqueta)}</text>")
    partes.append(f'<path class="g-area" d="{area}"/>')
    partes.append(f'<path class="g-linea" d="{linea}"/>')
    if proyeccion:
        tramo = [(fechas[-1], valores[-1])] + [(f.toordinal(), v) for f, v in proyeccion]
        punteada = " ".join(f"{'M' if i == 0 else 'L'}{x(f):.1f},{y(v):.1f}" for i, (f, v) in enumerate(tramo))
        partes.append(f'<path class="g-linea g-proyeccion" d="{punteada}"/>')
    ultimo_x, ultimo_y = x(fechas[-1]), y(valores[-1])
    partes.append(f'<circle class="g-punto" cx="{ultimo_x:.1f}" cy="{ultimo_y:.1f}" r="4"/>')
    etiquetas = [(fechas[0], puntos[0][0], "start")]
    if proyeccion:
        etiquetas += [(fechas[-1], puntos[-1][0], "middle"),
                      (proyeccion[-1][0].toordinal(), proyeccion[-1][0], "end")]
    else:
        medio = len(puntos) // 2
        etiquetas += [(fechas[medio], puntos[medio][0], "middle"), (fechas[-1], puntos[-1][0], "end")]
    for ordinal, fecha, ancla in etiquetas:
        partes.append(f'<text class="g-texto" x="{x(ordinal):.1f}" y="{alto - 8}" '
                      f'text-anchor="{ancla}">{escape(_etiqueta_fecha(fecha, con_dia))}</text>')
    partes.append("</svg>")
    return Markup("".join(partes))


def grafico_barras(puntos: list[tuple[dt.date, float]], titulo: str, decimales: int = 1,
                   sufijo: str = "%", ancho: int = ANCHO, alto: int = ALTO) -> Markup:
    """Barras para variaciones mensuales (positivas hacia arriba, negativas hacia abajo)."""
    puntos = sorted(puntos)
    if not puntos:
        return Markup("")
    identificador = f"g{next(_contador)}"
    izq, der, sup, inf = 52, 10, 14, 30
    valores = [v for _, v in puntos]
    ymax = max(max(valores), 0) or 0.1
    ymin = min(min(valores), 0)
    margen = (ymax - ymin) * 0.1
    ymax += margen
    ymin -= margen if ymin < 0 else 0

    def y(valor: float) -> float:
        return sup + (ymax - valor) / (ymax - ymin) * (alto - sup - inf)

    ancho_util = ancho - izq - der
    paso = ancho_util / len(puntos)
    barra = paso * 0.7
    partes = [
        f'<svg class="grafico" viewBox="0 0 {ancho} {alto}" role="img" '
        f'aria-labelledby="{identificador}-t" preserveAspectRatio="xMidYMid meet">',
        f'<title id="{identificador}-t">{escape(titulo)}</title>',
    ]
    for marca in _marcas_eje(ymin, ymax):
        yy = y(marca)
        partes.append(f'<line class="g-guia" x1="{izq}" x2="{ancho - der}" y1="{yy:.1f}" y2="{yy:.1f}"/>')
        partes.append(f'<text class="g-texto" x="{izq - 6}" y="{yy + 4:.1f}" text-anchor="end">'
                      f"{escape(numero(marca, decimales) + sufijo)}</text>")
    cero = y(0)
    for indice, (fecha, valor) in enumerate(puntos):
        xx = izq + indice * paso + (paso - barra) / 2
        arriba = min(y(valor), cero)
        altura = abs(y(valor) - cero) or 1
        clase = "g-barra" if valor >= 0 else "g-barra g-negativa"
        etiqueta = f"{_etiqueta_fecha(fecha, False)}: {numero(valor, decimales)}{sufijo}"
        partes.append(f'<rect class="{clase}" x="{xx:.1f}" y="{arriba:.1f}" width="{barra:.1f}" '
                      f'height="{altura:.1f}"><title>{escape(etiqueta)}</title></rect>')
    # La primera fecha se alinea con el borde izquierdo de su barra y la última con el derecho,
    # para que no se corten en un gráfico angosto.
    ultimo = len(puntos) - 1
    for indice in sorted({0, len(puntos) // 2, ultimo}):
        fecha = puntos[indice][0]
        if indice == 0 and ultimo > 0:
            xx, ancla = izq + (paso - barra) / 2, "start"
        elif indice == ultimo and ultimo > 0:
            xx, ancla = izq + indice * paso + (paso + barra) / 2, "end"
        else:
            xx, ancla = izq + indice * paso + paso / 2, "middle"
        partes.append(f'<text class="g-texto" x="{xx:.1f}" y="{alto - 8}" text-anchor="{ancla}">'
                      f"{escape(_etiqueta_fecha(fecha, False))}</text>")
    partes.append("</svg>")
    return Markup("".join(partes))


def grafico_ahorro(serie: list[dict]) -> Markup:
    """Barras del ahorro año a año: aportes (abajo) e intereses (arriba).

    Es el mismo SVG que dibuja ``graficoAhorro`` en estaticos/js/app.js: la página trae el del
    ejemplo (se ve sin JavaScript) y el JavaScript lo redibuja al cambiar los datos en el mismo
    espacio reservado (``.grafico-ahorro-lienzo``), sin mover la página. Una coordenada puede
    diferir en una décima por redondeo, sin efecto visible.
    """
    ancho, alto = 320, 160
    maximo = serie[-1]["saldo"] or 1
    paso = ancho / len(serie)
    partes = [f'<svg class="grafico" viewBox="0 0 {ancho} {alto}">']
    for indice, punto in enumerate(serie):
        x = indice * paso + paso * 0.15
        w = paso * 0.7
        total = punto["saldo"] / maximo * (alto - 10)
        aporte = min(punto["aportado"], punto["saldo"]) / maximo * (alto - 10)
        partes.append(f'<rect class="g-barra-aporte" x="{x:.1f}" y="{alto - aporte:.1f}" '
                      f'width="{w:.1f}" height="{aporte:.1f}"/>'
                      f'<rect class="g-barra" x="{x:.1f}" y="{alto - total:.1f}" '
                      f'width="{w:.1f}" height="{max(0, total - aporte):.1f}"/>')
    partes.append("</svg>")
    return Markup("".join(partes))
