"""Línea de comandos de Saca la Cuenta.

    python -m lucas actualizar      # descarga datos nuevos a data/
    python -m lucas construir       # genera el sitio en dist/
    python -m lucas construir --demo  # usa datos ficticios (sin internet)
    python -m lucas servir          # vista previa en http://localhost:8000
    python -m lucas verificar       # revisa datos y parámetros por actualizar
    python -m lucas diagnosticar    # prueba las fuentes de datos
    python -m lucas guias           # valida las guías de contenido/guias/
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
    from .datos import SERIES_OBLIGATORIAS
    sin_datos = [s for s, info in resumen["series"].items() if not info["total"] and s in SERIES_OBLIGATORIAS]
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


def comando_diagnosticar(args) -> int:
    """Prueba cada fuente de datos: si responde, cuánto tarda y qué trae."""
    import time

    from . import fuentes

    anio = hoy_chile().year
    pruebas = [("mindicador.cl", i, lambda i=i: fuentes.serie_mindicador(i, anio, intentos=1, timeout=20))
               for i in ("uf", "dolar", "euro", "utm", "ipc")]
    pruebas += [("sii.cl", i, lambda i=i: fuentes.serie_sii(i, anio, intentos=1, timeout=30))
                for i in ("uf", "dolar", "utm", "ipc")]
    pruebas += [("findic.cl", i, lambda i=i: fuentes.serie_findic(i, anio, intentos=1, timeout=20))
                for i in ("uf", "dolar", "euro", "utm", "ipc")]
    clave = os.environ.get("CMF_API_KEY", "").strip()
    if clave:
        pruebas += [("api.cmfchile.cl", i, lambda i=i: fuentes.serie_cmf(i, anio, clave))
                    for i in ("uf", "dolar", "euro", "utm", "ipc")]
    caidas: set[str] = set()
    for fuente, indicador, funcion in pruebas:
        if fuente in caidas:
            print(f"OMITIDA {fuente:16} {indicador:6} (la fuente no respondió antes)")
            continue
        inicio = time.monotonic()
        try:
            serie = funcion()
            fechas = sorted(serie)
            print(f"OK      {fuente:16} {indicador:6} {len(serie):4} valores: "
                  f"{fechas[0]} = {serie[fechas[0]]} ... {fechas[-1]} = {serie[fechas[-1]]} "
                  f"({time.monotonic() - inicio:.1f} s)")
        except Exception as error:  # noqa: BLE001 - diagnóstico: mostrar cualquier falla
            print(f"FALLA   {fuente:16} {indicador:6} ({time.monotonic() - inicio:.1f} s): {error}")
            if "No se pudo descargar" in str(error):
                caidas.add(fuente)
    if args.detalle:
        import re as _re
        for url in ("https://findic.cl/api/", "https://findic.cl/api/euro/2026"):
            inicio = time.monotonic()
            try:
                texto = fuentes.descargar_texto(url, intentos=1, timeout=20)
            except fuentes.ErrorDescarga as error:
                print(f"\nFALLA   {url} ({time.monotonic() - inicio:.1f} s): {error}")
                continue
            plano = " ".join(_re.sub(r"<[^>]+>", " ", texto).split())
            print(f"\nOK      {url}: {len(texto)} caracteres ({time.monotonic() - inicio:.1f} s)")
            for clave_busqueda in ("Dólar observado", "Dolar observado", "Euro", "UF", '"valor"'):
                posicion = plano.find(clave_busqueda)
                if posicion >= 0:
                    print(f"   …{plano[max(0, posicion - 60): posicion + 140]}…")
    if args.detalle and "sii.cl" not in caidas:
        for pagina in ("dolar/dolar{anio}.htm",):
            try:
                html = fuentes.descargar_texto(f"{fuentes.SII}/{pagina.format(anio=anio)}", intentos=1)
            except fuentes.ErrorDescarga as error:
                print(error)
                continue
            tablas = fuentes.tablas_html(html)
            print(f"\n{pagina.format(anio=anio)}: {len(tablas)} tablas")
            for numero, tabla in enumerate(tablas):
                print(f"  tabla {numero}: {len(tabla)} filas")
                for fila in tabla[:3] + tabla[-2:]:
                    print("    ", [celda[:18] for celda in fila[:14]])
    return 0


def comando_guias(args) -> int:
    """Valida las guías igual que la construcción del sitio y muestra un resumen por archivo.
    Falla (código 1) si alguna tiene errores."""
    from .construir import ErrorConstruccion
    from .guias import archivos_de_guias, contexto_de_revision, revisar_todas
    from .paginas import todas_las_paginas

    hoy = dt.date.fromisoformat(args.hoy) if args.hoy else None
    try:
        c, entorno = contexto_de_revision(demo=args.demo, hoy=hoy)
    except ErrorConstruccion as error:
        print(f"::error::{error}\nPrueba con datos de demostración: python -m lucas guias --demo")
        return 1
    archivos = [Path(a) for a in args.archivos] or archivos_de_guias()
    if not archivos:
        print("No hay guías que validar.")
        return 1
    # Rutas del sitio para avisar de enlaces a calculadoras que no existen.
    rutas = {p.ruta for p in todas_las_paginas(c)} | {f"/guias/{a.stem}/" for a in archivos_de_guias()}
    print(f"Datos {'de demostración' if c.datos.demo else 'reales'} al {c.hoy:%d-%m-%Y}.\n")
    total_errores = 0
    for r in revisar_todas(archivos, c, entorno, rutas):
        print(f"[{'ERROR' if r.errores else 'OK'}] {r.archivo.name}: {r.palabras or '?'} palabras")
        for error in r.errores:
            print(f"    error: {error}")
        for aviso in r.avisos:
            print(f"    aviso: {aviso}")
        if args.html and r.html:
            print(r.html)
        total_errores += len(r.errores)
    print(f"\n{len(archivos)} guías, {total_errores} errores.")
    return 1 if total_errores else 0


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

    p = sub.add_parser("diagnosticar", help="prueba las fuentes de datos (mindicador, SII, CMF)")
    p.add_argument("--detalle", action="store_true", help="muestra las tablas que encuentra en el SII")
    p.set_defaults(funcion=comando_diagnosticar)

    p = sub.add_parser("guias", help="valida las guías de contenido/guias/ (ver contenido/LEEME.md)")
    p.add_argument("archivos", nargs="*", help="guías a revisar (por defecto, todas)")
    p.add_argument("--html", action="store_true", help="muestra además el HTML generado")
    p.add_argument("--demo", action="store_true", help="usa los datos de demostración aunque haya datos reales")
    p.add_argument("--hoy", help="fecha AAAA-MM-DD (por defecto, hoy en Chile o la de los datos de demostración)")
    p.set_defaults(funcion=comando_guias)

    args = parser.parse_args(argv)
    return args.funcion(args)


if __name__ == "__main__":
    sys.exit(main())
