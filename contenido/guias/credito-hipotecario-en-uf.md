---
titulo: "Crédito hipotecario en UF: dividendo, pie y seguros ({{ hoy.year }})"
descripcion: "Cómo funciona un crédito hipotecario en Chile: pie, cálculo del dividendo en UF con ejemplos, seguros obligatorios, CAE, renta exigida y subsidios."
h1: "Cómo funciona un crédito hipotecario en UF"
resumen: "Cuánto pie necesitas, cómo se calcula el dividendo en UF, qué seguros son obligatorios, cómo comparar ofertas con la CAE y qué apoyos del Estado existen para comprar."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: vivienda
orden: 20
calculadoras:
  - /calculadoras/credito-hipotecario/
  - /uf/proyeccion/
fuentes:
  - nombre: "¿Cuánto cuesta un crédito hipotecario y en qué debe fijarse? (CMF Educa)"
    url: "https://www.cmfchile.cl/educa/621/w3-article-27374.html"
  - nombre: "¿Hay seguros obligatorios en los créditos hipotecarios? (CMF Educa)"
    url: "https://www.cmfchile.cl/educa/621/w3-article-27508.html"
  - nombre: "¿Qué es la Carga Anual Equivalente (CAE)? (SERNAC)"
    url: "https://www.sernac.cl/portal/607/w3-article-2463.html"
  - nombre: "Subsidio al Crédito Hipotecario (Ministerio de Vivienda y Urbanismo)"
    url: "https://www.minvu.gob.cl/nuevo-subsidio-al-credito-hipotecario/"
faq:
  - pregunta: "¿Cuánto pie se necesita para un crédito hipotecario?"
    respuesta: "Lo habitual es un 20% del valor de la vivienda, porque los bancos suelen financiar hasta el 80%. Para viviendas nuevas, la garantía estatal FOGAES permite financiar hasta el 90%. Además del pie, necesitas dinero para la tasación, la notaría, el impuesto de timbres y la inscripción en el Conservador de Bienes Raíces."
  - pregunta: "¿Qué seguros son obligatorios en un crédito hipotecario?"
    respuesta: "El de desgravamen y el de incendio. El seguro de sismo no es obligatorio: es una cobertura adicional que se contrata junto con la póliza de incendio. Puedes tomar una póliza individual en vez de la colectiva del banco, siempre que tenga al menos la misma cobertura."
  - pregunta: "¿Cuánto es el dividendo de un crédito de 2.400 UF?"
    respuesta: "Con una tasa de {{ p.tasa_hipotecaria_referencia|porcentaje(2) }} anual a 25 años, el dividendo sin seguros es de {{ calc.dividendo(2400, p.tasa_hipotecaria_referencia, 25)|numero(2) }} UF, unos {{ (calc.dividendo(2400, p.tasa_hipotecaria_referencia, 25) * uf_hoy)|pesos }} con la UF de hoy. A 30 años baja a {{ calc.dividendo(2400, p.tasa_hipotecaria_referencia, 30)|numero(2) }} UF, pero pagas más intereses en total."
  - pregunta: "¿Qué es la CAE de un crédito hipotecario?"
    respuesta: "Es la carga anual equivalente: un porcentaje que muestra el costo anual del crédito, cualquiera sea su plazo, incluyendo la tasa de interés, los seguros asociados y los gastos. Con igual monto y plazo, el crédito con menor CAE es el más barato."
  - pregunta: "¿Por qué mi dividendo en pesos sube todos los meses?"
    respuesta: "Porque el dividendo está expresado en UF y la UF se reajusta cada día según la inflación. Con tasa fija, tu dividendo en UF no cambia, pero cada mes se paga con una UF que vale un poco más en pesos."
---
{% set tasa = p.tasa_hipotecaria_referencia %}
{% set r20 = calc.simular_hipotecario(3000, 0.2, tasa, 20, p) %}
{% set r25 = calc.simular_hipotecario(3000, 0.2, tasa, 25, p) %}
{% set r30 = calc.simular_hipotecario(3000, 0.2, tasa, 30, p) %}
{% set primer_anio = calc.saldos_anuales(r25.credito_uf, tasa, 25)[0] %}
Un crédito hipotecario es un préstamo de largo plazo para comprar una vivienda, que queda hipotecada como garantía. En Chile lo habitual es pactarlo en UF: la deuda y el dividendo se expresan en UF y cada mes pagas su equivalente en pesos. Aquí verás cuánto pie necesitas, cómo se calcula el dividendo y qué costos no aparecen en la fórmula.

## Cómo funciona un crédito en UF

El banco te presta un monto en UF, que devuelves en dividendos mensuales durante el plazo que pactes (por ejemplo, 20, 25 o 30 años). Con la UF del {{ hoy|fecha_larga }} ({{ uf_hoy|pesos(2) }}), un dividendo de 13 UF equivale a **{{ (13 * uf_hoy)|pesos }}**.

Como la UF sube con la inflación, ese mismo dividendo cuesta un poco más en pesos cada mes, aunque en UF no cambie. Si la UF sube 4% en un año, tu dividendo en pesos también sube 4%. La [UF proyectada]({{ ruta('/uf/proyeccion/') }}) te ayuda a estimar cuánto pagarás en pesos durante los próximos meses.

## Pie: cuánto financia el banco

Lo habitual es que el crédito cubra hasta el **80% del valor de tasación** de la vivienda, así que el pie suele ser de al menos 20%. Para una vivienda de {{ 3000|numero }} UF:

| Concepto | En UF | En pesos hoy |
|---|---:|---:|
| Valor de la vivienda | {{ 3000|numero }} UF | {{ (3000 * uf_hoy)|pesos }} |
| Pie (20%) | {{ r25.pie_uf|numero }} UF | {{ (r25.pie_uf * uf_hoy)|pesos }} |
| Crédito (80%) | {{ r25.credito_uf|numero }} UF | {{ (r25.credito_uf * uf_hoy)|pesos }} |

Además del pie, necesitas dinero para los **gastos operacionales**. Según la Comisión para el Mercado Financiero (CMF), incluyen la tasación de la propiedad, el estudio de títulos y la redacción de la escritura, la notaría, el impuesto de timbres y estampillas y la inscripción en el Conservador de Bienes Raíces. El impuesto de timbres varía, entre otras cosas, según si la vivienda es nueva o usada y si está acogida al DFL 2.

Para viviendas nuevas existe una garantía estatal (FOGAES) que permite al banco financiar hasta el 90% del valor, con un pie de 10%, siempre sujeto a su evaluación. La explicamos más abajo, en la sección de subsidios.

## Cómo se calcula el dividendo en UF

Con tasa fija, el dividendo es una cuota constante en UF que se calcula con la fórmula de cuota fija (sistema francés), la misma que usa nuestro [simulador de crédito hipotecario]({{ ruta('/calculadoras/credito-hipotecario/') }}):

> Dividendo = C × r ÷ [1 − (1 + r)⁻ⁿ]

- **C:** monto del crédito en UF.
- **r:** tasa de interés mensual. En el simulador es la tasa anual dividida por 12.
- **n:** número de dividendos (años × 12).

Con un crédito de {{ r25.credito_uf|numero }} UF a una tasa de {{ tasa|porcentaje(2) }} anual (una tasa de referencia para el ejemplo, no una oferta) y 25 años: r = {{ (tasa / 12)|numero(4) }} y n = 300. El dividendo resulta en **{{ r25.dividendo_uf|numero(2) }} UF**, unos {{ r25.dividendo_pesos|pesos }} con la UF de hoy.

### El plazo cambia mucho el costo total

| Plazo | Dividendo | Dividendo hoy | Intereses totales | Renta sugerida |
|---|---:|---:|---:|---:|
{% for r in [r20, r25, r30] -%}
| {{ [20, 25, 30][loop.index0] }} años | {{ r.dividendo_uf|numero(2) }} UF | {{ r.dividendo_pesos|pesos }} | {{ r.intereses_uf|numero }} UF | {{ r.renta_minima|pesos }} |
{% endfor %}

Montos sin seguros, para un crédito de {{ r25.credito_uf|numero }} UF a {{ tasa|porcentaje(2) }} anual. Alargar el plazo de 20 a 30 años baja el dividendo en {{ (r20.dividendo_uf - r30.dividendo_uf)|numero(2) }} UF, pero los intereses suben de {{ r20.intereses_uf|numero }} a {{ r30.intereses_uf|numero }} UF.

En los primeros años, la mayor parte del dividendo se va en intereses. En el ejemplo a 25 años, durante el primer año pagas {{ primer_anio.intereses|numero(1) }} UF de intereses y solo {{ primer_anio.amortizacion|numero(1) }} UF de capital.

## Seguros obligatorios y otros costos del dividendo

El dividendo que cobra el banco es mayor que el de la fórmula, porque se le suman las primas de los seguros. Según la CMF, la normativa exige que los créditos hipotecarios estén protegidos por dos seguros:

- **Desgravamen:** paga el saldo de la deuda si el deudor fallece.
- **Incendio:** protege la vivienda que garantiza el crédito.

El seguro de **sismo no es obligatorio**: es una cobertura adicional que solo se puede contratar junto con la póliza de incendio ([CMF Educa](https://www.cmfchile.cl/educa/621/w3-article-920.html)). Pregunta si la tuya lo incluye.

Los seguros que el banco contrata por cuenta de sus deudores se licitan en forma colectiva y se adjudican a la oferta de menor precio. Aun así, puedes contratar una póliza individual, siempre que tenga al menos la misma cobertura que la colectiva ([seguros asociados a créditos hipotecarios, CMF Educa](https://www.cmfchile.cl/educa/621/w3-article-1753.html)).

## Cómo comparar ofertas: CAE y tipo de tasa

La tasa de interés es el principal costo del crédito, pero no el único. Para comparar, usa la **CAE (carga anual equivalente)**: según el SERNAC, expresa en un porcentaje el costo anual del crédito, cualquiera sea su plazo, e incluye el capital, la tasa, el plazo, todos los seguros asociados y los gastos o cargos de productos contratados voluntariamente. Con el mismo monto y plazo, el crédito con menor CAE es el más barato.

La tasa puede ser fija, variable o mixta:

| Tipo de tasa | Cómo funciona | Riesgo para ti |
|---|---|---|
| Fija | La misma tasa durante todo el plazo | Ninguno de tasa: sabes desde el inicio cuánto pagarás en UF |
| Variable | Se ajusta periódicamente según lo que diga el contrato | Si suben las tasas, sube tu dividendo |
| Mixta | Fija durante un período inicial y luego variable | Tu dividendo puede subir cuando termine el período fijo |

Consejos para cotizar:

1. Pide al menos tres cotizaciones formales con el mismo monto, plazo y tipo de tasa.
2. Compara la CAE y el dividendo total con seguros, no solo la tasa.
3. Pregunta cuánto te cobrarían por prepagar (pagar por adelantado) parte o todo el crédito: te servirá si después quieres abonar capital o cambiarte de banco.
4. Revisa qué productos te ofrecen junto con el crédito y si son voluntarios.

## Qué renta te piden

Cada banco define qué parte de tu renta puede ir al dividendo y evalúa además tus otras deudas y tu historial de pagos. Como referencia, nuestro simulador considera que el dividendo no supere el **{{ p.carga_financiera_maxima|porcentaje(0) }} de tu renta líquida**:

> Renta sugerida = dividendo en pesos ÷ {{ p.carga_financiera_maxima|numero(2) }}

En el ejemplo a 25 años, un dividendo de {{ r25.dividendo_pesos|pesos }} requiere una renta de unos **{{ r25.renta_minima|pesos }}**. Si tus ingresos no alcanzan, puedes subir el pie, alargar el plazo o buscar una vivienda de menor valor. Recuerda que los seguros también suben el dividendo real.

## Subsidios y garantías del Estado

Si compras una vivienda **nueva**, revisa el subsidio al crédito hipotecario: rebaja la tasa de interés y viene con la garantía estatal FOGAES, que permite créditos con menos pie. Lo creó la Ley 21.748, publicada el 29 de mayo de 2025.
{% if hoy.year < 2028 or (hoy.year == 2028 and hoy.month <= 5) %}
En 2026 se amplió: según el Ministerio de Vivienda y Urbanismo, aplica a viviendas nuevas de hasta 6.000 UF compradas por personas naturales, con 80 mil cupos, hasta el 31 de mayo de 2028 o hasta que se agoten. Se pide en los bancos y entidades adscritas al beneficio: una vez aprobado el crédito, el subsidio se otorga automáticamente.
{% else %}
Según el Ministerio de Vivienda y Urbanismo, el programa ampliado tuvo vigencia hasta el 31 de mayo de 2028 o hasta agotar sus cupos. Revisa en minvu.gob.cl si existe un beneficio similar vigente.
{% endif %}

Otros programas del Ministerio de Vivienda y Urbanismo (Minvu):

| Programa | Para quién | Qué entrega |
|---|---|---|
| DS1, Subsidio para Sectores Medios | Familias de sectores medios; tiene tres tramos y exige un ahorro mínimo | Un monto en UF que se suma a tu ahorro y, si hace falta, a un crédito hipotecario |
| DS19, Integración Social y Territorial | Familias de distintos ingresos | Viviendas en proyectos bien ubicados, donde también puedes aplicar un DS1 o un DS49 |
| DS49, Fondo Solidario de Elección de Vivienda | Familias de menores ingresos | Subsidio para comprar o construir una vivienda |

Los llamados, montos y requisitos cambian cada año: revisa el sitio del [Minvu](https://www.minvu.gob.cl/) antes de postular.

Esta guía es informativa y no reemplaza la cotización formal de tu banco. Para simular con tus propios datos, usa el [simulador de crédito hipotecario]({{ ruta('/calculadoras/credito-hipotecario/') }}).
