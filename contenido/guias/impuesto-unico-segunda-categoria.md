---
titulo: "Impuesto único de segunda categoría: qué es y cómo se calcula ({{ hoy.year }})"
descripcion: "Qué es el impuesto único de segunda categoría, quién lo paga, la tabla vigente en pesos y en UTM y cómo calcularlo desde tu sueldo bruto, paso a paso y con ejemplos."
h1: "Impuesto único de segunda categoría: qué es y cómo se calcula"
resumen: "La tabla de {{ hoy|mes_de_anio }} en pesos y en UTM, cómo pasar de tu sueldo a la base tributable y cuándo debes reliquidar en la Operación Renta."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: impuestos
orden: 20
calculadoras:
  - /calculadoras/sueldo-liquido/
  - /impuesto-unico/
fuentes:
  - nombre: "SII: Tablas mensuales del Impuesto Único de Segunda Categoría 2026"
    url: "https://www.sii.cl/valores_y_fechas/impuesto_2da_categoria/impuesto2026.htm"
  - nombre: "SII: Circular N°2 de 2026, tabla del artículo 43 N°1 de la Ley sobre Impuesto a la Renta"
    url: "https://www.sii.cl/normativa_legislacion/circulares/2026/circu2.pdf"
  - nombre: "SII: Guía práctica de declaración de Renta 2026"
    url: "https://www.sii.cl/servicios_online/renta/guia_practica_renta_2026.pdf"
  - nombre: "SII Educa: ¿Cuáles son los impuestos directos en Chile?"
    url: "https://www.sii.cl/siieduca/aprende-con-nosotros/cuales-son-los-impuestos-directos.html"
faq:
  - pregunta: "¿Desde qué sueldo se paga impuesto único en {{ hoy.year }}?"
    respuesta: "{% set a = calc.afp_mas_barata(p) %}Se paga cuando la base tributable (sueldo imponible menos AFP, salud y seguro de cesantía) supera {{ p.tramos_impuesto[0].hasta|numero(1) }} UTM: en {{ hoy|mes_de_anio }}, {{ (p.tramos_impuesto[0].hasta * utm_hoy)|pesos }}. Como antes se descuentan las cotizaciones, el sueldo bruto exento es mayor: unos {{ (p.tramos_impuesto[0].hasta * utm_hoy / (1 - p.tasa_afp - p.comisiones_afp[a] - p.salud_obligatoria - p.cesantia_trabajador['indefinido']))|monto_corto }} de pesos con Fonasa, contrato indefinido y AFP {{ p.nombres_afp[a] }}."
  - pregunta: "¿Qué diferencia hay entre el impuesto único y el Global Complementario?"
    respuesta: "El impuesto único se aplica cada mes a los sueldos y pensiones, y lo retiene quien te paga. El Global Complementario es anual y reúne todas tus rentas, como honorarios o más de un sueldo. Si solo tienes un empleador, en general no debes hacer la declaración anual de renta."
  - pregunta: "¿Qué pasa si tengo dos empleadores al mismo tiempo?"
    respuesta: "Cada empleador retiene el impuesto como si su sueldo fuera tu único ingreso. Por eso en la Operación Renta de abril debes reliquidar: se suman tus sueldos del año, se calcula el impuesto anual y se descuenta lo ya retenido. Como la suma puede caer en un tramo más alto, lo habitual es que quede una diferencia por pagar."
  - pregunta: "¿El APV rebaja el impuesto único?"
    respuesta: "Sí, si eliges el régimen B. Lo que ahorras, hasta {{ p.tope_apv_mensual_uf|numero }} UF al mes, se descuenta de la base tributable antes de aplicar la tabla, así que pagas menos impuesto. En el régimen A no hay rebaja de impuesto: el Estado bonifica una parte de lo que ahorras."
---
{# cifra(): sin decimales si el número es entero (30 UTM) y con uno si no lo es (13,5 UTM) #}
{% macro cifra(x) %}{{ x|numero(0 if x == x|round else 1) }}{% endmacro %}
{# tasa(): factor de la tabla como porcentaje (0.04 -> 4%, 0.135 -> 13,5%) #}
{% macro tasa(f) %}{% set pct = (f * 100)|round(6) %}{{ f|porcentaje(0 if pct == pct|round else 1) }}{% endmacro %}
{% set afp = calc.afp_mas_barata(p) %}
{% set primer_tramo = p.tramos_impuesto[0].hasta %}
El impuesto único de segunda categoría es el impuesto mensual a los sueldos y las pensiones. Lo descuenta tu empleador en la liquidación y solo se paga cuando tu base tributable supera {{ cifra(primer_tramo) }} UTM: en {{ hoy|mes_de_anio }}, **{{ (primer_tramo * utm_hoy)|pesos }}**. Aquí tienes la tabla vigente, cómo calcularlo paso a paso y cuándo debes revisarlo en la Operación Renta.

## Qué es y quién lo paga

El impuesto único grava las rentas del trabajo dependiente: sueldos, salarios y demás remuneraciones de un contrato de trabajo (artículo 42 N°1 de la Ley sobre Impuesto a la Renta). También se aplica a las pensiones, jubilaciones y montepíos. Sus características principales:

- **Es mensual**: se calcula sobre lo que recibes cada mes.
- **Es progresivo**: la tasa sube por tramos, desde 0% hasta 40% (artículo 43 N°1 de la misma ley).
- **Lo retiene quien te paga**: tu empleador, o quien te paga la pensión, lo descuenta y lo paga al fisco. Tú no haces ningún trámite mensual.
- **Es único**: la ley le da ese carácter respecto de las rentas a las que se aplica. Si solo tienes un empleador, en general no debes presentar declaración anual de renta.

Los trabajadores independientes no pagan este impuesto: sus honorarios tributan una vez al año en el Impuesto Global Complementario, como explica la [guía de la boleta de honorarios]({{ ruta('/guias/boleta-de-honorarios/') }}).

## Tabla del impuesto único de {{ hoy|mes_de_anio }}

La ley fija la tabla en unidades tributarias mensuales (UTM) y el SII la publica cada mes en pesos, multiplicando por la UTM del mes. Con la UTM de {{ hoy|mes_de_anio }} ({{ utm_hoy|pesos }}), la tabla queda así:

| Base tributable (UTM) | Base tributable (pesos) | Tasa | Cantidad a rebajar |
|---|---|---:|---:|
{% set ns = namespace(desde=0) -%}
{% for t in p.tramos_impuesto -%}
| {% if loop.first %}Hasta {{ cifra(t.hasta) }}{% elif t.hasta is none %}Más de {{ cifra(ns.desde) }}{% else %}Más de {{ cifra(ns.desde) }} hasta {{ cifra(t.hasta) }}{% endif %} | {% if loop.first %}Hasta {{ (t.hasta * utm_hoy)|pesos(2) }}{% elif t.hasta is none %}Más de {{ (ns.desde * utm_hoy)|pesos(2) }}{% else %}Más de {{ (ns.desde * utm_hoy)|pesos(2) }} hasta {{ (t.hasta * utm_hoy)|pesos(2) }}{% endif %} | {% if t.factor == 0 %}Exento{% else %}{{ tasa(t.factor) }}{% endif %} | {{ (t.rebaja * utm_hoy)|pesos(2) }} |
{% if t.hasta is not none %}{% set ns.desde = t.hasta %}{% endif -%}
{% endfor %}

En UTM, las cantidades a rebajar son fijas: {% for t in p.tramos_impuesto if t.factor > 0 %}{{ t.rebaja|numero(2) }}{% if loop.revindex == 2 %} y {% elif not loop.last %}; {% endif %}{% endfor %} UTM, de menor a mayor tramo. Como la UTM cambia cada mes, los montos en pesos también cambian: revisa la [tabla del impuesto único del mes]({{ ruta('/impuesto-unico/') }}) cuando necesites la de otro período.

## Cómo calcularlo paso a paso

1. **Parte de tu remuneración imponible**: sueldo base, gratificación, horas extra, comisiones y bonos imponibles.
2. **Resta las cotizaciones obligatorias**: AFP ({{ p.tasa_afp|porcentaje(0) }} más la comisión de tu AFP), salud ({{ p.salud_obligatoria|porcentaje(0) }}) y seguro de cesantía ({{ p.cesantia_trabajador['indefinido']|porcentaje(1) }} si tu contrato es indefinido). Si ganas más de {{ cifra(p.tope_imponible_uf) }} UF al mes, las cotizaciones se calculan solo hasta ese tope imponible. Lo que queda es la **base tributable**.
3. **Ubica tu tramo** en la tabla y aplica la fórmula: **impuesto = base tributable × tasa − cantidad a rebajar**.

### Ejemplo con un sueldo de $1.500.000

{% set s = calc.sueldo_liquido(1500000, p, afp=afp) %}
{% set tramo = p.tramos_impuesto[s.tramo] %}
Con contrato indefinido, Fonasa y AFP {{ p.nombres_afp[afp] }}:

| Concepto | Monto |
|---|---:|
| Sueldo bruto imponible | $1.500.000 |
| AFP {{ p.nombres_afp[afp] }} ({{ s.tasa_afp_total|porcentaje(2) }}) | −{{ s.afp|pesos }} |
| Salud ({{ p.salud_obligatoria|porcentaje(0) }}) | −{{ s.salud|pesos }} |
| Seguro de cesantía ({{ p.cesantia_trabajador['indefinido']|porcentaje(1) }}) | −{{ s.cesantia|pesos }} |
| **Base tributable** | **{{ s.base_tributable|pesos }}** |
| Impuesto único | **{{ s.impuesto|pesos }}** |

La base equivale a {{ (s.base_tributable / p.utm)|numero(1) }} UTM, así que cae en el tramo con tasa de {{ tasa(s.tasa_marginal) }}. El cálculo es {{ s.base_tributable|pesos }} × {{ tasa(s.tasa_marginal) }} − {{ (tramo.rebaja * p.utm)|pesos(2) }} = {{ s.impuesto|pesos }}, que se redondea al peso. Es el {{ (s.impuesto / 1500000)|porcentaje(2) }} del sueldo bruto, y el líquido del mes queda en {{ s.liquido|pesos }}.

### Tasa marginal y tasa efectiva

La tasa de tu tramo es tu **tasa marginal**: solo se aplica a la parte de la base que está dentro de ese tramo. La cantidad a rebajar descuenta lo que se cobraría de más sobre los tramos inferiores. Por eso, pasar a un tramo superior nunca reduce tu sueldo líquido: solo el exceso paga la tasa más alta. La **tasa efectiva**, es decir, el impuesto dividido por tu sueldo, siempre es bastante menor.

Con contrato indefinido, Fonasa y AFP {{ p.nombres_afp[afp] }}:

| Sueldo bruto | Base tributable | Impuesto | % del bruto |
|---:|---:|---:|---:|
{% for bruto in [800000, 1200000, 1500000, 2000000, 3000000, 4000000, 6000000] -%}
{% set r = calc.sueldo_liquido(bruto, p, afp=afp) -%}
| {{ bruto|pesos }} | {{ r.base_tributable|pesos }} | {{ r.impuesto|pesos }} | {{ (r.impuesto / bruto)|porcentaje(2) }} |
{% endfor %}

Sobre {{ (p.tope_imponible_uf * p.uf)|pesos }} ({{ cifra(p.tope_imponible_uf) }} UF) las cotizaciones dejan de crecer porque llegan al tope imponible, así que la base tributable sube más rápido. Para tu propio sueldo usa la [calculadora de sueldo líquido]({{ ruta('/calculadoras/sueldo-liquido/') }}), que aplica la tabla del mes, tu AFP y tu sistema de salud.

## Reliquidación anual: más de un empleador u honorarios

Con un solo empleador, el impuesto único es definitivo. Hay dos casos frecuentes en que debes revisar tu impuesto en la Operación Renta de abril del año siguiente:

- **Dos o más empleadores al mismo tiempo.** Cada uno retiene como si su sueldo fuera tu único ingreso, pero la suma de ambos sueldos puede caer en un tramo más alto. Por eso debes reliquidar: se suman las remuneraciones del año, se calcula el impuesto anual sobre el total y se descuenta lo que ya te retuvieron. Lo habitual es que quede una diferencia por pagar.
- **Sueldo y boletas de honorarios.** Los honorarios se declaran en el Impuesto Global Complementario, que suma todas tus rentas del año, incluido tu sueldo. Al impuesto que resulta se le descuentan el impuesto único que retuvo tu empleador y las retenciones de tus boletas; si te retuvieron de más, recibes una devolución.

En ambos casos el SII prepara una propuesta de declaración con la información que le entregan tus empleadores y quienes recibieron tus boletas. Revísala antes de aceptarla.

## El APV régimen B rebaja la base tributable

El ahorro previsional voluntario (APV) en el **régimen B** se descuenta de la base tributable, con un tope de {{ p.tope_apv_mensual_uf|numero }} UF al mes. Si lo ahorras con descuento por planilla, tu empleador lo rebaja cada mes antes de calcular el impuesto.

{% set sin_apv = calc.sueldo_liquido(3000000, p, afp=afp) %}
{% set con_apv = calc.sueldo_liquido(3000000, p, afp=afp, apv=100000) %}
Por ejemplo, con un sueldo de $3.000.000, un APV de $100.000 al mes baja la base tributable de {{ sin_apv.base_tributable|pesos }} a {{ con_apv.base_tributable|pesos }} y el impuesto de {{ sin_apv.impuesto|pesos }} a {{ con_apv.impuesto|pesos }}: pagas {{ (sin_apv.impuesto - con_apv.impuesto)|pesos }} menos de impuesto cada mes. El ahorro de impuesto es igual al APV multiplicado por tu tasa marginal, así que crece mientras más alto es tu tramo.

En el **régimen A**, en cambio, no rebajas impuesto: el Estado bonifica una parte de lo que ahorras. Por eso el régimen B suele convenir más a quien está en un tramo alto, y el A a quien paga poco o nada de impuesto único.

Esta guía es informativa y no reemplaza la asesoría del SII. Para casos particulares, revisa la información de tu declaración en sii.cl o consulta a un contador.
