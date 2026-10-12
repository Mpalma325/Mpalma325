# Guías de Saca la Cuenta

Las guías son artículos explicativos que acompañan a las calculadoras ("Cómo se calcula el
finiquito", "Qué es la UF", etc.). Sirven para atraer búsquedas informativas desde Google y
para que Google AdSense vea contenido original de valor.

El sitio las publica solo (`lucas/guias.py`): cada guía tiene su página en `/guias/<slug>/`,
aparece en el índice `/guias/` agrupada por categoría, entra al sitemap y lleva datos
estructurados (Article, migas y preguntas frecuentes). En la página se agregan solos el
índice de contenidos, el recuadro "Calcúlalo" con las calculadoras relacionadas, las fuentes,
las preguntas frecuentes, los anuncios y los enlaces de referidos de la categoría.

## Archivos

- Una guía = un archivo `contenido/guias/<slug>.md` (UTF-8).
- `<slug>`: minúsculas, números y guiones, máx. 60 caracteres. Será la URL: `/guias/<slug>/`.
- Archivos que empiezan con `_` o en mayúscula (p. ej. `_borrador.md` o `LEEME.md`) NO son guías:
  sirven para dejar borradores que todavía no se publican.

## Formato

```markdown
---
titulo: "Cómo calcular el finiquito en Chile ({{ hoy.year }})"   # <title>, máx. 70 caracteres ya renderizado
descripcion: "Qué incluye el finiquito, cómo se calculan la indemnización por años de servicio y las vacaciones, con ejemplos y plazos legales."   # 110-165 ideal
h1: "Cómo se calcula el finiquito"
resumen: "Indemnización por años de servicio, aviso previo y vacaciones: qué te corresponde según la causal de término."   # máx. 220, para la tarjeta en /guias/
publicada: 2026-10-12      # fecha sin comillas
revisada: 2026-10-12       # última revisión de contenido (≤ hoy)
categoria: trabajo         # trabajo | impuestos | vivienda | ahorro | indicadores
orden: 10                  # opcional: orden dentro de la categoría (menor = primero)
calculadoras:              # rutas internas relacionadas (se muestran como "Calcúlalo")
  - /calculadoras/finiquito/
  - /calculadoras/vacaciones-proporcionales/
fuentes:                   # mínimo 2, solo https, idealmente oficiales (bcn.cl, dt.gob.cl, sii.cl, spensiones.cl, ine.gob.cl, bcentral.cl, cmfchile.cl, chileatiende.gob.cl)
  - nombre: "Código del Trabajo, artículos 161 a 177 (BCN)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=207436"
  - nombre: "Dirección del Trabajo"
    url: "https://www.dt.gob.cl/"          # usa la URL exacta de la página que citas, verificada
faq:                       # 2 a 6 preguntas; van al final y en JSON-LD FAQPage
  - pregunta: "¿Cuál es el plazo para pagar el finiquito?"
    respuesta: "El empleador tiene 10 días hábiles desde la separación del trabajador (artículo 177 del Código del Trabajo)."
---
Párrafo de entrada (2-4 líneas) que responde de inmediato la pregunta principal.

## Primera sección

Texto en Markdown...
```

- `titulo`, `descripcion`, `h1`, `resumen` y las preguntas/respuestas del `faq` admiten expresiones Jinja (`{{ hoy.year }}`, `{{ p.imm|pesos }}`), que se renderizan antes de medir su largo.
- El **cuerpo** se procesa primero como plantilla **Jinja2** (StrictUndefined: una variable inexistente es un error) y después como **Markdown** con las extensiones `tables`, `toc` (`toc_depth: 2-3`) y `sane_lists`. Ninguna otra extensión.
- Jinja no borra los saltos de línea de las etiquetas `{% ... %}`: dentro de una tabla o una lista usa `-%}` (por ejemplo `{% for x in lista -%}`) para que no queden líneas en blanco que la corten.
- No uses `# ` (h1) en el cuerpo: la plantilla ya pone el `h1`. Usa `##` para secciones (mínimo 3) y `###` para subsecciones. Los `##` y `###` forman el índice de la guía.
- Enlaces internos SIEMPRE con `ruta()`: `[calculadora de finiquito]({{ ruta('/calculadoras/finiquito/') }})`. Enlaces externos con `https://`.
- Las citas de Markdown (`> texto`) se muestran como recuadros: úsalas para notas y advertencias.
- Extensión: 900 a 1.600 palabras (mínimo duro: 500).
- Campo opcional `palabras_clave` (lista de términos): se publica en el JSON-LD del artículo.

## Variables disponibles en el cuerpo (y en los campos con Jinja)

| Variable | Qué es |
|---|---|
| `hoy` | `datetime.date` del día en que se genera el sitio (Chile) |
| `p` | diccionario de parámetros vigentes hoy (ver `contexto_parametros` en `lucas/calculos.py`): `p.uf`, `p.utm`, `p.imm`, `p.tope_imponible_uf`, `p.tope_cesantia_uf`, `p.tasa_afp`, `p.comisiones_afp` (dict por AFP), `p.nombres_afp`, `p.salud_obligatoria`, `p.cesantia_trabajador` / `p.cesantia_empleador` (dict: `indefinido`, `plazo_fijo`, `indefinido_11`), `p.tramos_impuesto` (lista de `{hasta, factor, rebaja}` en UTM), `p.retencion_honorarios`, `p.tope_apv_mensual_uf`, `p.gratificacion_tasa`, `p.gratificacion_tope_imm_anual`, `p.sis`, `p.mutual_basica`, `p.aporte_empleador_reforma`, `p.tope_indemnizacion_uf`, `p.tope_anios_indemnizacion`, `p.feriado_anual_habiles`, `p.tasa_hipotecaria_referencia`, `p.carga_financiera_maxima` (y cualquier clave que se agregue después a `contexto_parametros`) |
| `uf_hoy`, `utm_hoy` | valor de la UF de hoy y de la UTM del mes |
| `dolar` | tupla `(fecha, valor)` del último dólar observado |
| `feriados` | `set` de `datetime.date` con los feriados nacionales de `hoy.year - 2` a `hoy.year + 1` (incluidos los de `feriados_extra`), para `calc.finiquito(..., feriados, ...)` o `calc.dias_corridos_de_feriado(...)` |
| `calc` | el módulo `lucas.calculos`: `calc.sueldo_liquido(1000000, p)`, `calc.finiquito(...)`, `calc.honorarios_desde_bruto(...)`, `calc.dividendo(...)`, `calc.simular_hipotecario(...)`, `calc.impuesto_unico(...)`, `calc.gratificacion_legal(...)`, `calc.proyectar_ahorro(...)`, `calc.sumar_meses(...)` |
| `ruta('/x/')` | ruta interna correcta (con la base del sitio) |
| `sitio` | `sitio.nombre`, `sitio.url` |

Se usa el mismo entorno Jinja del sitio, así que también están sus demás globales (`cabecera`,
`demo`...), pero las guías deben limitarse a las variables de esta tabla.

Filtros (los mismos del sitio, formato chileno): `pesos(decimales=0)` → `$1.234.567`, `numero(decimales=0)` → `1.234,5`, `porcentaje(decimales=1, signo=False)` (recibe fracción: `0.1525|porcentaje(2)` → `15,25%`), `fecha_larga` → `12 de octubre de 2026`, `fecha_con_dia` → `lunes 12 de octubre de 2026`, `fecha_corta` → `12-10-2026`, `dia_mes` → `12 de octubre`, `dia_semana`, `nombre_mes` (recibe número de mes), `mes_anio` (recibe fecha) → `octubre 2026`, `mes_de_anio` (recibe fecha) → `octubre de 2026`, `capitalizar`, `monto_corto` → `1,5 millones`. También sirven los filtros y etiquetas estándar de Jinja (`dictsort`, `min`, `{% macro %}`, `{% set %}`...).

Ejemplo de cálculo vivo dentro de una guía:

```markdown
{% set r = calc.sueldo_liquido(1000000, p) %}
Con un sueldo bruto de $1.000.000, AFP {{ p.nombres_afp['uno'] }} y Fonasa, el líquido es
**{{ r.liquido|pesos }}**: se descuentan {{ r.afp|pesos }} de AFP, {{ r.salud|pesos }} de salud
y {{ r.cesantia|pesos }} de seguro de cesantía.
```

Regla de oro: **todo número que cambie con el tiempo (UF, sueldo mínimo, tasas, topes, tabla de
impuesto) se escribe con variables**, para que la guía siga correcta cuando cambien los
parámetros. Los hechos históricos se escriben con su fecha ("desde el 26 de abril de 2026").

## Estilo

- Español neutro, trato de "tú" (como el resto del sitio). Nunca voseo ("vos", "tenés", "calculá").
- Frases cortas, ejemplos concretos, listas y tablas cuando ayuden. Nada de relleno ni frases
  genéricas de "inteligencia artificial" ("En el mundo actual...", "Es importante destacar...").
- Cita la norma exacta (ley y artículo) cuando corresponda y enlázala en `fuentes`.
- Advierte cuando algo depende del caso (contrato, causal, isapre) y recomienda la fuente oficial
  (Dirección del Trabajo, SII, etc.) para casos particulares. No es asesoría legal.
- Solo afirmaciones verificadas en fuentes oficiales. Si no puedes verificar algo, no lo escribas.
- Cada URL de `fuentes` debe existir (ábrela) y respaldar lo que citas. Nunca inventes URLs.

## Validación

```bash
python -m lucas guias                                        # todas las guías
python -m lucas guias contenido/guias/mi-guia.md --html      # una guía, mostrando el HTML generado
python -m lucas guias --demo                                 # con los datos de demostración
```

El comando renderiza cada guía igual que el sitio (con los datos de `data/` si existen y, si no,
con los de demostración) e imprime, por archivo, las palabras, los errores y los avisos. Además
avisa si una ruta de `calculadoras` no existe en el sitio. Termina con código 1 si hay errores.

`python -m lucas construir` aplica las mismas reglas: si una guía tiene errores, la construcción
se detiene e indica el archivo y el problema, y el sitio no se publica hasta corregirlo. Los
avisos (por ejemplo, una descripción fuera del largo ideal) no detienen nada. Las pruebas
(`python -m pytest`) validan todas las guías y revisan que no queden enlaces rotos.
