"""App instalable (PWA): manifiesto, service worker y páginas de instalación.

El sitio se puede instalar desde el navegador ("Agregar a pantalla de inicio") en
Android, iPhone y computadores, gratis y sin pasar por las tiendas de aplicaciones.
El service worker guarda las páginas que la persona visita para que sigan
funcionando sin conexión (las calculadoras calculan en el navegador), pero siempre
pide primero la versión nueva a la red: los valores del día no quedan pegados.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .construir import Contexto, Pagina

TEMA = "#0f766e"
FONDO = "#f4f6f7"

# Accesos directos al mantener presionado el ícono (Android y escritorio).
ACCESOS = [
    ("UF hoy", "/uf/"),
    ("Sueldo líquido", "/calculadoras/sueldo-liquido/"),
    ("Calculadoras", "/calculadoras/"),
    ("Feriados", "/feriados/"),
]

# Páginas que se guardan al instalar, para que la app abra aunque no haya conexión.
PRECARGA = ["/", "/sin-conexion/", "/calculadoras/"]


def manifiesto(cfg: dict) -> dict:
    sitio = cfg["sitio"]
    base = sitio["ruta_base"]
    icono = base + "/estaticos/img/"
    return {
        "name": f"{sitio['nombre']}: indicadores y calculadoras",
        "short_name": sitio["nombre"],
        "description": sitio["eslogan"],
        "lang": sitio["idioma"],
        "id": base + "/",
        "start_url": base + "/",
        "scope": base + "/",
        "display": "standalone",
        "background_color": FONDO,
        "theme_color": TEMA,
        "categories": ["finance", "utilities"],
        "icons": [
            {"src": icono + "icono-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": icono + "icono-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": icono + "icono-maskable-512.png", "sizes": "512x512", "type": "image/png",
             "purpose": "maskable"},
        ],
        "shortcuts": [{"name": nombre, "url": base + ruta} for nombre, ruta in ACCESOS],
    }


SERVICE_WORKER = """/* Service worker de __NOMBRE__: guarda las páginas visitadas para usarlas sin conexión.
   Las páginas siempre se piden primero a la red (los valores cambian cada día); el
   caché solo se usa si no hay conexión. Los archivos de /estaticos/ llevan su versión
   en la URL, así que se sirven del caché. Se genera en lucas/app_instalable.py. */
'use strict';

var VERSION = '__VERSION__';
var BASE = '__BASE__';
var CACHE = 'paginas-' + VERSION;
var MAXIMO_PAGINAS = 60;
var PRECARGA = __PRECARGA__;

self.addEventListener('install', function (evento) {
  evento.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(PRECARGA);
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener('activate', function (evento) {
  evento.waitUntil(
    caches.keys().then(function (nombres) {
      return Promise.all(nombres.filter(function (nombre) {
        return nombre !== CACHE;
      }).map(function (nombre) {
        return caches.delete(nombre);
      }));
    }).then(function () {
      return self.clients.claim();
    })
  );
});

function recortar(cache) {
  return cache.keys().then(function (claves) {
    if (claves.length <= MAXIMO_PAGINAS) {
      return null;
    }
    return cache.delete(claves[0]).then(function () {
      return recortar(cache);
    });
  });
}

function guardar(peticion, respuesta) {
  if (!respuesta || !respuesta.ok || respuesta.type !== 'basic') {
    return;
  }
  var copia = respuesta.clone();
  caches.open(CACHE).then(function (cache) {
    return cache.put(peticion, copia).then(function () {
      return recortar(cache);
    });
  });
}

self.addEventListener('fetch', function (evento) {
  var peticion = evento.request;
  var url = new URL(peticion.url);
  if (peticion.method !== 'GET' || url.origin !== self.location.origin) {
    return;  // anuncios, analítica y otros sitios: sin intervenir
  }
  if (url.pathname.indexOf(BASE + '/estaticos/') === 0) {
    evento.respondWith(
      caches.match(peticion).then(function (guardada) {
        return guardada || fetch(peticion).then(function (respuesta) {
          guardar(peticion, respuesta);
          return respuesta;
        });
      })
    );
    return;
  }
  if (peticion.mode === 'navigate' || url.pathname.indexOf(BASE + '/api/') === 0) {
    evento.respondWith(
      fetch(peticion).then(function (respuesta) {
        guardar(peticion, respuesta);
        return respuesta;
      }).catch(function () {
        return caches.match(peticion, { ignoreSearch: true }).then(function (guardada) {
          return guardada || caches.match(BASE + '/sin-conexion/');
        });
      })
    );
  }
});
"""


def service_worker(cfg: dict, version: str) -> str:
    base = cfg["sitio"]["ruta_base"]
    precarga = json.dumps([base + ruta for ruta in PRECARGA])
    return (SERVICE_WORKER.replace("__NOMBRE__", cfg["sitio"]["nombre"])
            .replace("__VERSION__", version).replace("__BASE__", base)
            .replace("__PRECARGA__", precarga))


def escribir_app(salida: Path, cfg: dict, ahora: dt.datetime) -> None:
    """Escribe /manifest.webmanifest y /sw.js (debe vivir en la raíz para controlar todo el sitio)."""
    (salida / "manifest.webmanifest").write_text(
        json.dumps(manifiesto(cfg), ensure_ascii=False, indent=1), encoding="utf-8")
    (salida / "sw.js").write_text(service_worker(cfg, ahora.strftime("%Y%m%d%H%M")), encoding="utf-8")


def paginas_app(c: Contexto) -> list[Pagina]:
    nombre = c.cfg["sitio"]["nombre"]
    inicio = ("Inicio", "/")
    return [
        Pagina(
            ruta="/app/",
            plantilla="app.html",
            titulo=f"Instala la app de {nombre} gratis (Android y iPhone)",
            descripcion=(f"Instala {nombre} en tu celular en segundos y sin tienda de aplicaciones: "
                         "UF, dólar, feriados y calculadoras con un toque, incluso sin conexión."),
            h1=f"Instala {nombre} en tu celular",
            migas=[inicio, ("App", "/app/")],
            prioridad=0.5,
            frecuencia="monthly",
            modificada=dt.date(2026, 10, 12),
            faq=[
                ("¿Cuánto cuesta la app?",
                 "Nada. Es el mismo sitio, instalado como app desde el navegador: no pasa por "
                 "Google Play ni por la App Store y no pide permisos especiales."),
                ("¿Funciona sin internet?",
                 "Sí, con lo último que viste: las páginas que visitaste quedan guardadas en tu "
                 "celular y las calculadoras calculan en el mismo teléfono. Los valores del día se "
                 "actualizan apenas vuelves a tener conexión."),
                ("¿Cómo la desinstalo?",
                 "Como cualquier app: mantén presionado el ícono y elige desinstalar (Android) o "
                 "eliminar (iPhone)."),
            ],
        ),
        Pagina(
            ruta="/sin-conexion/",
            plantilla="sin_conexion.html",
            titulo=f"Sin conexión | {nombre}",
            descripcion=("No hay conexión a internet. Las páginas que ya visitaste siguen "
                         "disponibles en la app y se actualizan al volver la conexión."),
            h1="Estás sin conexión",
            en_sitemap=False,
            indexar=False,
        ),
    ]
