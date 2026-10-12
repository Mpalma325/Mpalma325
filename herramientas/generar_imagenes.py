"""Genera las imágenes PNG del sitio (íconos y la imagen para redes sociales).

Uso: python herramientas/generar_imagenes.py
Requiere Pillow (pip install -r requirements-dev.txt). Las imágenes ya están en
el repositorio; solo necesitas correr esto si cambias el logo o el nombre
(el nombre y el eslogan se leen de config.yaml).
"""

from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "estaticos" / "img"
VERDE = (15, 118, 110)
VERDE_OSCURO = (17, 94, 89)
AMBAR = (251, 191, 36)
BLANCO = (255, 255, 255)

FUENTES = [
    "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def fuente(tamano: int, peso: str = "ExtraBold") -> ImageFont.FreeTypeFont:
    candidatas = [f.replace("ExtraBold", peso) for f in FUENTES] + FUENTES
    for ruta in candidatas:
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tamano)
    return ImageFont.load_default()


def logo(tamano: int, invertido: bool = False, margen: float = 0.0) -> Image.Image:
    """Dibuja el logo (misma geometría que logo.svg, en una grilla de 64x64): un signo
    igual, el resultado de "sacar la cuenta", con la barra de abajo en ámbar.

    ``invertido`` usa fondo blanco y la barra de arriba verde (para fondos verdes).
    ``margen`` achica el signo hacia el centro (íconos "maskable" de Android, que el
    sistema recorta en círculo): con margen, el fondo ocupa todo el cuadrado."""
    fondo, barra = (BLANCO, VERDE) if invertido else (VERDE, BLANCO)
    escala = 4  # sobremuestreo para bordes suaves
    s = tamano * escala / 64
    img = Image.new("RGBA", (tamano * escala, tamano * escala), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if margen:
        d.rectangle([0, 0, 64 * s - 1, 64 * s - 1], fill=fondo)
    else:
        d.rounded_rectangle([0, 0, 64 * s - 1, 64 * s - 1], radius=15 * s, fill=fondo)
    k = 1 - margen  # factor de escala del signo alrededor del centro (32, 32)

    def p(x: float, y: float) -> tuple[float, float]:
        return ((32 + (x - 32) * k) * s, (32 + (y - 32) * k) * s)

    ancho = 8 * s * k
    for y, color in ((25, barra), (40, AMBAR)):
        inicio, fin = p(18, y), p(46, y)
        d.line([inicio, fin], fill=color, width=round(ancho))
        for x0, y0 in (inicio, fin):
            d.ellipse([x0 - ancho / 2, y0 - ancho / 2, x0 + ancho / 2, y0 + ancho / 2], fill=color)
    return img.resize((tamano, tamano), Image.LANCZOS)


def imagen_social(nombre: str, eslogan: str) -> Image.Image:
    ancho, alto = 1200, 630
    img = Image.new("RGB", (ancho, alto), VERDE)
    d = ImageDraw.Draw(img)
    for y in range(alto):  # degradado vertical suave
        t = y / alto
        color = tuple(round(a + (b - a) * t) for a, b in zip(VERDE, VERDE_OSCURO))
        d.line([(0, y), (ancho, y)], fill=color)
    marca = logo(180, invertido=True)
    img.paste(marca, (90, 120), marca)
    tamano = 104
    while d.textlength(nombre, font=fuente(tamano)) > ancho - 310 - 70 and tamano > 60:
        tamano -= 4  # el nombre debe caber al lado del logo
    d.text((310, 120 + (104 - tamano) // 2), nombre, font=fuente(tamano), fill=BLANCO)
    letra_eslogan = fuente(40, "Medium")
    palabras, lineas = eslogan.split(), [""]
    for palabra in palabras:  # ajusta el eslogan al ancho disponible
        prueba = (lineas[-1] + " " + palabra).strip()
        if d.textlength(prueba, font=letra_eslogan) > ancho - 314 - 70:
            lineas.append(palabra)
        else:
            lineas[-1] = prueba
    for i, linea in enumerate(lineas):
        d.text((314, 252 + i * 50), linea, font=letra_eslogan, fill=(220, 245, 241))
    temas = ["UF hoy", "Dólar", "UTM", "Sueldo líquido", "Honorarios", "Feriados"]
    x, y = 94, 440
    letra = fuente(34, "SemiBold")
    for tema in temas:
        caja = d.textbbox((0, 0), tema, font=letra)
        w = caja[2] - caja[0] + 44
        if x + w > ancho - 80:
            x, y = 94, y + 78
        d.rounded_rectangle([x, y, x + w, y + 60], radius=30, fill=(10, 84, 78), outline=(120, 205, 196), width=2)
        d.text((x + 22, y + 8), tema, font=letra, fill=BLANCO)
        x += w + 16
    return img


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    logo(180, margen=0.12).save(DESTINO / "apple-touch-icon.png")  # iOS redondea las esquinas
    logo(512).save(DESTINO / "logo-512.png")
    logo(256).save(DESTINO / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # Íconos de la app instalable (manifest.webmanifest)
    logo(192).save(DESTINO / "icono-192.png")
    logo(512).save(DESTINO / "icono-512.png")
    logo(512, margen=0.2).save(DESTINO / "icono-maskable-512.png")
    sitio = yaml.safe_load((RAIZ / "config.yaml").read_text(encoding="utf-8"))["sitio"]
    imagen_social(sitio["nombre"], sitio["eslogan"]).save(DESTINO / "og.png", optimize=True)
    print("Imágenes generadas en", DESTINO)


if __name__ == "__main__":
    main()
