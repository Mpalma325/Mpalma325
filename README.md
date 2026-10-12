# Saca la Cuenta

**Sitio web de indicadores económicos y calculadoras financieras para Chile que se actualiza solo y se monetiza con publicidad y enlaces de referidos.**

- **Indicadores del día:** UF, dólar, euro, UTM e IPC, con archivo por mes y por año y la **UF proyectada**.
- **11 calculadoras:** sueldo líquido, finiquito (incluida la obra o faena), vacaciones proporcionales, boletas de honorarios, IVA, horas extra (jornada de 42 horas), crédito de consumo con CAE, crédito hipotecario, reajuste de arriendo por IPC, interés compuesto y días hábiles.
- **15 guías** verificadas con fuentes oficiales (finiquito, vacaciones, gratificación, liquidación, honorarios, impuesto único, IVA, CAE, arriendo, hipotecario, UF, UTM, dólar...), con cifras que se actualizan solas.
- **Indicadores previsionales del mes**, calendario de **feriados** (con archivo `.ics`), página de **metodología** e historial de correcciones.
- **API gratuita** de indicadores en JSON y **widget** para otros sitios, para conseguir enlaces.

En total, unas 350 páginas que se regeneran solas dos veces al día.

> ⚠️ **Esta rama vive temporalmente en el repositorio de perfil `Mpalma325/Mpalma325`.** La sesión de Claude no tenía permiso para crear repositorios nuevos. **No la fusiones con `main` de ese repositorio** (reemplazaría el README del perfil). Muévela a su propio repositorio con los pasos de la sección [Mover a un repositorio propio](#mover-a-un-repositorio-propio).

---

## Cómo genera ingresos

```
 Google (búsquedas)  ──►  Saca la Cuenta  ──►  Publicidad (AdSense)
 "valor uf hoy"           ~350 páginas       Referidos (Fintual, Global66, ...)
 "sueldo líquido 1 millón" útiles y rápidas   Productos propios (más adelante)
          ▲                     │
          │        GitHub Actions, 2 veces al día:
          └──────  descarga datos → prueba → construye → publica
```

- **Costo:** el dominio `.cl` (~$10.000 al año en NIC Chile). El hosting (Cloudflare) y la automatización (GitHub Actions) son gratis.
- **Trabajo:** unas horas para ponerlo en marcha y luego ~1–2 horas al mes de mantención. GitHub les avisa por correo cuando hay que actualizar algo.
- **Expectativa realista:** el tráfico orgánico tarda entre 3 y 12 meses en llegar. Revisen los escenarios en [docs/PLAN_DE_NEGOCIO.md](docs/PLAN_DE_NEGOCIO.md). No es dinero rápido: es un activo que, bien cuidado, crece solo.

## Lista para lanzar

- [ ] Mover el código a un repositorio propio (abajo)
- [ ] Revisar textos y parámetros (`config.yaml`, `parametros/chile.yaml`) y completar `sitio.equipo` ("Quiénes somos")
- [ ] Pedir la clave gratuita de la API de la CMF (respaldo oficial para el dólar y el euro)
- [ ] Comprar el dominio y publicar en Cloudflare → [guía paso a paso](docs/GUIA_PUESTA_EN_MARCHA.md)
- [ ] Crear el correo de contacto gratis con Cloudflare Email Routing
- [ ] Registrar el sitio en Google Search Console y Bing Webmaster Tools
- [ ] Postular a Google AdSense cuando el sitio tenga algunas semanas indexado
- [ ] Inscribirse en programas de referidos y agregarlos a `config.yaml` → [programas verificados](docs/MONETIZACION.md)
- [ ] Seguir el plan de las primeras 8 semanas → [lanzamiento](docs/LANZAMIENTO.md)

## Probarlo en tu computador

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python -m lucas construir --demo   # sitio con datos FICTICIOS, sin internet
python -m lucas servir             # abre http://localhost:8000
```

Con datos reales (requiere internet):

```bash
python -m lucas actualizar         # descarga UF, dólar, euro, UTM e IPC a data/
python -m lucas construir          # genera el sitio en dist/
python -m lucas verificar          # revisa parámetros por actualizar y datos atrasados
python -m lucas guias --demo       # valida las guías de contenido/guias/
```

Pruebas: `python -m pytest` (las de paridad con JavaScript requieren Node.js).

## Cómo está hecho

| Carpeta / archivo | Qué contiene |
|---|---|
| `lucas/` | El generador en Python: descarga de datos (`fuentes.py`), metodología UF/UTM (`datos.py`), fórmulas (`calculos.py`), feriados (`feriados.py`, `calendario.py`), páginas (`paginas.py` y `paginas_*.py`), guías (`guias.py`), API (`api.py`), fuentes y metodología (`confianza.py`) y construcción (`construir.py`). |
| `contenido/` | Las guías en Markdown (`guias/`, formato en `LEEME.md`) y el historial público de correcciones (`correcciones.yaml`). |
| `widget/` | El widget que otros sitios insertan (`widget.js`, se publica en la raíz del sitio). |
| `plantillas/` | Plantillas HTML (Jinja2) de cada tipo de página. |
| `estaticos/` | CSS, JavaScript de las calculadoras (`calculos.js` replica `calculos.py`) e imágenes. |
| `parametros/chile.yaml` | Parámetros legales con fecha de vigencia y fuente: comisiones AFP, topes, tabla de impuesto único, sueldo mínimo, retención de honorarios, feriados especiales. |
| `config.yaml` | Nombre, URL, AdSense, referidos y analítica. |
| `data/` | Datos descargados (los sube GitHub Actions). |
| `tests/` | Pruebas: fórmulas contra valores oficiales, feriados contra las listas de gob.cl, paridad Python/JavaScript, sitio sin enlaces rotos y SEO básico. |
| `.github/workflows/` | `pruebas.yml` (en cada push) y `publicar.yml` (actualización y publicación automáticas). |

Decisiones de diseño:

- **Sitio estático**, sin servidor ni base de datos: carga muy rápido (clave para Google), no tiene costos y no se cae.
- **Cálculos en el navegador:** los montos que ingresa el usuario no salen de su computador.
- **La UF se calcula por adelantado** con la fórmula oficial del Banco Central apenas el INE publica el IPC, y la fórmula se valida contra los valores oficiales en cada ejecución.
- **Los feriados se calculan con las reglas de la ley** (traslados, solsticio, Pascua), no con una lista copiada.
- **Los parámetros legales tienen fecha de vigencia:** se pueden cargar cambios futuros por adelantado y el sitio los aplica solo el día que corresponde.

## Mover a un repositorio propio

1. En GitHub, crea un repositorio **vacío** llamado `saca-la-cuenta` (sin README ni licencia). Puede ser privado si publicas en Cloudflare.
2. En tu computador:

   ```bash
   git clone --branch ccr-eb6f7695-mr7j22 https://github.com/Mpalma325/Mpalma325.git saca-la-cuenta
   cd saca-la-cuenta
   git remote set-url origin https://github.com/Mpalma325/saca-la-cuenta.git
   git push -u origin ccr-eb6f7695-mr7j22:main
   git checkout -B main origin/main
   ```

3. Sigue la [guía de puesta en marcha](docs/GUIA_PUESTA_EN_MARCHA.md).
4. Cuando todo funcione, puedes borrar la rama `ccr-eb6f7695-mr7j22` del repositorio de perfil.

## Documentación

- [Guía de puesta en marcha](docs/GUIA_PUESTA_EN_MARCHA.md): dominio, Cloudflare, Search Console, AdSense y referidos.
- [Plan de negocio](docs/PLAN_DE_NEGOCIO.md): mercado, competencia, proyección de ingresos, hoja de ruta y roles.
- [Mantención](docs/MANTENCION.md): qué actualizar y cuándo, y cómo agregar páginas, guías o calculadoras.
- [Monetización](docs/MONETIZACION.md): programas de referidos verificados, AdSense en Chile, impuestos y otras fuentes de ingreso.
- [Lanzamiento](docs/LANZAMIENTO.md): plan de 8 semanas para conseguir visitas y enlaces, con borradores de mensajes.
