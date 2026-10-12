"""Línea de comandos de Lucas Claras.

    python -m lucas actualizar      # descarga datos nuevos a data/
    python -m lucas construir       # genera el sitio en dist/
    python -m lucas construir --demo  # usa datos ficticios (sin internet)
    python -m lucas servir          # vista previa en http://localhost:8000
    python -m lucas verificar       # revisa datos y parámetros por actualizar
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

from .config import RAIZ, cargar_config, cargar_parametros, hoy_chile


def _resumen_github(texto: str) -> None:
    """Escribe en el resumen del job si corre en GitHub Actions."""
    ruta = os.environ.get("GITHUB_STEP_SUMMARY")
    if ruta:
        with open(ruta, "a", encoding="utf-8") as archivo:
            archivo.write(texto + "\n")


def comando_actualizar(args) -> int:
    from .fuentes import actualizar

    cfg = cargar_config()
    resumen = actualizar(anio_inicio=args.desde or cfg["sitio"]["anio_inicio_datos"])
    lineas = ["### Actualización de datos", "", "| Serie | Descargados | Cambios | Último dato |",
              "|---|---|---|---|"]
    for serie, info in resumen["series"].items():
        lineas.append(f"| {serie} | {info['descargados']} | {info['cambios']} | {info['ultimo']} |")
        print(f"{serie:6} descargados={info['descargados']:5} cambios={info['cambios']:4} último={info['ultimo']}")
    for error in resumen["errores"]:
        print(f"::warning::{error}")
        lineas.append(f"- ⚠️ {error}")
    _resumen_github("\n".join(lineas))
    sin_datos = [s for s, info in resumen["series"].items() if not info["total"]]
    if sin_datos:
        print(f"::error::No hay datos para: {', '.join(sin_datos)}")
        return 1
    return 0


def comando_construir(args) -> int:
    from .construir import ErrorConstruccion, construir

    hoy = dt.date.fromisoformat(args.hoy) if args.hoy else None
    if args.demo and hoy is None:
        meta = RAIZ / "tests" / "fixtures" / "datos_demo" / "meta.json"
        if meta.exists():
            hoy = dt.date.fromisoformat(json.loads(meta.read_text(encoding="utf-8"))["fecha_referencia"])
    try:
        resumen = construir(salida=Path(args.salida), demo=args.demo, hoy=hoy)
    except ErrorConstruccion as error:
        print(f"::error::{error}")
        return 1
    print(f"Sitio generado: {resumen['paginas']} páginas en {resumen['salida']} "
          f"(fecha {resumen['hoy']}{', DEMO' if resumen['demo'] else ''})")
    for advertencia in resumen["advertencias"]:
        print(f"::warning::{advertencia}")
    _resumen_github(f"### Sitio generado\n\n{resumen['paginas']} páginas, fecha {resumen['hoy']}.")
    return 0


def comando_servir(args) -> int:
    import functools
    import http.server

    carpeta = Path(args.salida)
    if not carpeta.exists():
        print("Primero genera el sitio: python -m lucas construir --demo")
        return 1
    manejador = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(carpeta))
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.puerto), manejador) as servidor:
        print(f"Vista previa en http://localhost:{args.puerto} (Ctrl+C para salir)")
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


def comando_verificar(args) -> int:
    """Revisa parámetros vencidos y datos atrasados. Falla (código 1) si hay algo que hacer,
    para que GitHub te avise por correo."""
    from .config import cargar_parametros
    from .datos import cargar_datos, revisar_frescura

    hoy = hoy_chile()
    params = cargar_parametros()
    cfg = cargar_config()
    problemas: list[str] = []
    for grupo, limite, fuente in params.revisiones_pendientes(hoy):
        problemas.append(f"Revisar los parámetros '{grupo}' en parametros/chile.yaml "
                         f"(fecha de revisión: {limite}). Fuente: {fuente}")
    datos = cargar_datos(RAIZ / "data", params.get("utm_se_mantiene_con_ipc_negativo", False))
    errores, advertencias = revisar_frescura(datos, hoy)
    problemas += errores + advertencias
    if not cfg["sitio"].get("correo_contacto"):
        print("::notice::Falta 'correo_contacto' en config.yaml (recomendado para AdSense).")
    if problemas:
        lineas = ["### ⚠️ Tareas de mantención pendientes", ""] + [f"- {p}" for p in problemas]
        _resumen_github("\n".join(lineas))
        for problema in problemas:
            print(f"::error::{problema}")
        return 1
    print("Todo en orden: parámetros vigentes y datos al día.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m lucas", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("actualizar", help="descarga datos nuevos a data/")
    p.add_argument("--desde", type=int, help="año inicial si no hay datos (por defecto, config.yaml)")
    p.set_defaults(funcion=comando_actualizar)

    p = sub.add_parser("construir", help="genera el sitio estático")
    p.add_argument("--demo", action="store_true", help="usa datos ficticios de tests/fixtures")
    p.add_argument("--salida", default=str(RAIZ / "dist"))
    p.add_argument("--hoy", help="fecha AAAA-MM-DD (por defecto, hoy en Chile)")
    p.set_defaults(funcion=comando_construir)

    p = sub.add_parser("servir", help="vista previa local")
    p.add_argument("--salida", default=str(RAIZ / "dist"))
    p.add_argument("--puerto", type=int, default=8000)
    p.set_defaults(funcion=comando_servir)

    p = sub.add_parser("verificar", help="revisa parámetros vencidos y datos atrasados")
    p.set_defaults(funcion=comando_verificar)

    args = parser.parse_args(argv)
    return args.funcion(args)


if __name__ == "__main__":
    sys.exit(main())
