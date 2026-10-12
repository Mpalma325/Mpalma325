---
titulo: "Gratificación legal en Chile {{ hoy.year }}: cómo se calcula y su tope"
descripcion: "Qué es la gratificación legal, la diferencia entre el 30% de las utilidades y el 25% con tope de 4,75 ingresos mínimos, y cómo aparece en tu liquidación."
h1: "Gratificación legal: cómo se calcula"
resumen: "Los dos sistemas de gratificación legal: el 30% de las utilidades o el 25% de tus remuneraciones con tope de {{ p.gratificacion_tope_imm_anual|numero(2) }} ingresos mínimos al año. Cómo se paga mes a mes y cómo aparece en tu liquidación."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: trabajo
orden: 50
calculadoras:
  - /calculadoras/sueldo-liquido/
fuentes:
  - nombre: "Código del Trabajo, artículos 42, 46 a 52 y 172 (Biblioteca del Congreso Nacional)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=207436"
  - nombre: "Dirección del Trabajo: ¿Cuándo el empleador se encuentra en la obligación de pagar la gratificación legal?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60150.html"
  - nombre: "Dirección del Trabajo: la gratificación legal (artículo 50, tope e ingreso mínimo del 31 de diciembre)"
    url: "https://www.dt.gob.cl/portal/1626/w3-article-99034.html"
  - nombre: "Dirección del Trabajo: la gratificación (remuneración afecta a cotizaciones)"
    url: "https://www.dt.gob.cl/portal/1626/w3-article-100598.html"
  - nombre: "Dirección del Trabajo: gratificación proporcional a los meses trabajados"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60158.html"
  - nombre: "Dirección del Trabajo, Ord. N° 5401/370: reliquidación por reajuste del ingreso mínimo"
    url: "https://www.dt.gob.cl/legislacion/1624/w3-article-62451.html"
  - nombre: "Ley que fija el ingreso mínimo mensual vigente (Biblioteca del Congreso Nacional)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=1225354"
faq:
  - pregunta: "¿Cuánto es la gratificación legal en {{ hoy.year }}?"
    respuesta: "Si la empresa tuvo utilidades y usa el sistema del artículo 50, el {{ p.gratificacion_tasa|porcentaje(0) }} de tu remuneración mensual, con un tope de {{ (p.gratificacion_tope_imm_anual * p.imm / 12)|pesos }} al mes con el ingreso mínimo actual: {{ p.gratificacion_tope_imm_anual|numero(2) }} ingresos mínimos al año ({{ (p.gratificacion_tope_imm_anual * p.imm)|pesos }}) divididos en 12. Con el sistema del artículo 47, depende de las utilidades de la empresa."
  - pregunta: "¿La gratificación es obligatoria?"
    respuesta: "Sí, para las empresas con fines de lucro y las cooperativas que están obligadas a llevar contabilidad y obtienen utilidades líquidas en el año (artículo 47 del Código del Trabajo). Si tu contrato establece una gratificación, rige lo pactado, que nunca puede ser menor que la legal (artículo 46); si el contrato la garantiza, se debe aunque no haya utilidades."
  - pregunta: "¿La gratificación paga impuesto y cotizaciones?"
    respuesta: "Sí. La gratificación es remuneración, así que es imponible: sobre ella se descuentan AFP, salud y seguro de cesantía, y forma parte de la base del impuesto único."
  - pregunta: "¿Me corresponde gratificación si trabajé menos de un año?"
    respuesta: "Sí, en proporción a los meses trabajados (artículo 52 del Código del Trabajo); según la Dirección del Trabajo, solo cuentan los meses completos. Si tu empleador la paga mes a mes, la vas recibiendo en cada liquidación."
---
{% set tasa = p.gratificacion_tasa %}
{% set veces = p.gratificacion_tope_imm_anual %}
{% set tope_anual = veces * p.imm %}
{% set tope_mensual = tope_anual / 12 %}
{% set umbral = tope_mensual / tasa %}
La gratificación legal es la parte de las utilidades de la empresa que la ley obliga a repartir entre sus trabajadores. Hay dos formas de cumplirla, y la que normalmente aparece cada mes en las liquidaciones es la del artículo 50: el {{ tasa|porcentaje(0) }} de la remuneración mensual, con un tope de {{ veces|numero(2) }} ingresos mínimos al año, que hoy equivale a **{{ tope_mensual|pesos }} al mes**.

## Quién tiene derecho

El artículo 47 del Código del Trabajo obliga a gratificar a los establecimientos mineros, industriales, comerciales o agrícolas, a las empresas y cualquier otro empleador que persiga fines de lucro, y a las cooperativas, siempre que:

- estén obligados a llevar libros de contabilidad, y
- obtengan utilidades o excedentes líquidos en su giro durante el año.

Según la Dirección del Trabajo, esos requisitos deben cumplirse todos a la vez: si la empresa no tuvo utilidad líquida en el año, no hay obligación legal de gratificar. La gratificación anual se paga a más tardar en abril del año siguiente, aunque el empleador puede adelantarla con anticipos mensuales o trimestrales.

Si trabajas en una de esas empresas, tienes derecho a gratificación aunque no completes el año: en ese caso se paga en proporción a los meses trabajados (artículo 52).

Tu contrato o un convenio colectivo puede establecer otra gratificación, llamada convencional. En ese caso rige lo pactado, pero nunca puede ser inferior a la gratificación legal (artículo 46). Si el contrato garantiza una gratificación, se debe aunque la empresa no tenga utilidades.

## Los dos sistemas: artículo 47 o artículo 50

La ley le da al empleador dos formas de cumplir:

| | Artículo 47 | Artículo 50 |
|---|---|---|
| Cuánto | Al menos el 30% de la utilidad líquida de la empresa | El {{ tasa|porcentaje(0) }} de lo que ganaste en el año por remuneraciones mensuales |
| Cómo se reparte | En proporción a lo que ganó cada trabajador en el año | A cada trabajador según su propia remuneración |
| Tope por trabajador | No tiene | {{ veces|numero(2) }} ingresos mínimos al año ({{ tope_anual|pesos }} hoy) |
| Depende de la utilidad | Sí: es un porcentaje de la utilidad, así que cambia cada año | Solo para que exista la obligación: si hubo utilidad líquida, el monto no depende de cuánta fue |

La **utilidad líquida** es la utilidad que determina el Servicio de Impuestos Internos para el impuesto a la renta, sin descontar pérdidas de años anteriores, menos un 10% del capital propio del empleador (artículo 48). Si el empleador paga el {{ tasa|porcentaje(0) }} del artículo 50, queda liberado de repartir el 30% del artículo 47, sea cual sea la utilidad líquida que obtuvo.

{% set planilla = 120000000 %}
{% set utilidad = 40000000 %}
{% set anual = 12000000 %}
{% set art47 = utilidad * 0.3 * anual / planilla %}
{% set art50 = [anual * tasa, tope_anual]|min %}
**Ejemplo.** Una empresa tuvo una utilidad líquida de {{ utilidad|pesos }} y pagó {{ planilla|pesos }} en remuneraciones en el año. Laura ganó {{ anual|pesos }} en el año, el {{ (anual / planilla)|porcentaje(0) }} de esa planilla.

- Con el artículo 47, la empresa reparte al menos {{ (utilidad * 0.3)|pesos }} (30% de la utilidad), y a Laura le corresponde el {{ (anual / planilla)|porcentaje(0) }}: **{{ art47|pesos }}** en el año.
- Con el artículo 50, a Laura le corresponde el {{ tasa|porcentaje(0) }} de {{ anual|pesos }}, es decir {{ (anual * tasa)|pesos }}, con el tope de {{ tope_anual|pesos }}: **{{ art50|pesos }}** en el año.

## Cuánto es mes a mes

Muchos empleadores pagan la gratificación del artículo 50 todos los meses, como anticipo. Cada mes recibes el {{ tasa|porcentaje(0) }} de tu remuneración mensual, con un tope mensual de {{ veces|numero(2) }} × {{ p.imm|pesos }} ÷ 12 = **{{ tope_mensual|pesos }}**. El tope se alcanza con una remuneración de {{ umbral|pesos }} al mes; desde ahí, la gratificación ya no sube.

| Remuneración mensual | Gratificación mensual | Total con gratificación |
|---|---:|---:|
{%- for sueldo in [p.imm, 700000, 850000, 1000000, 1500000] %}
| {{ sueldo|pesos }}{% if sueldo == p.imm %} (ingreso mínimo){% endif %} | {{ calc.gratificacion_legal(sueldo, p)|pesos }} | {{ (sueldo + calc.gratificacion_legal(sueldo, p))|pesos }} |
{%- endfor %}

Como el tope depende del ingreso mínimo, sube cada vez que se reajusta el sueldo mínimo. Por ejemplo, con los $539.000 que rigieron entre enero y abril de 2026, el tope mensual era de {{ (veces * 539000 / 12)|pesos }}; con el ingreso mínimo actual ({{ p.imm|pesos }}) es de {{ tope_mensual|pesos }}. Puedes ver el valor vigente y su historial en la página del [sueldo mínimo]({{ ruta('/sueldo-minimo/') }}).

Los pagos mensuales son anticipos. Según la Dirección del Trabajo, el tope anual se calcula con el ingreso mínimo vigente al 31 de diciembre, y si el mínimo se reajustó durante el año, el empleador debe reliquidar y pagarte la diferencia. Por eso, si en algunos meses recibiste el tope calculado con un mínimo más bajo, al cerrar el año te corresponde ese ajuste.

## Cómo revisar si está bien calculada

1. Busca en tu liquidación la línea de gratificación y tu remuneración mensual imponible sin ella.
2. Si esa remuneración es menor que {{ umbral|pesos }}, la gratificación del artículo 50 debería ser el {{ tasa|porcentaje(0) }} de ese monto.
3. Si es igual o mayor, debería ser el tope: {{ tope_mensual|pesos }}.
4. Revisa que la gratificación sume en el total imponible, porque sobre ella se calculan tus cotizaciones.
5. Si tu contrato establece una gratificación distinta, compárala con lo pactado: no puede ser menor que la legal.

Por ejemplo, con una remuneración de {{ 600000|pesos }}, la gratificación mensual debería ser {{ calc.gratificacion_legal(600000, p)|pesos }}; con {{ 2000000|pesos }}, el tope de {{ calc.gratificacion_legal(2000000, p)|pesos }}. Si no te la pagan o el monto no calza, pide primero la explicación a tu empleador y, si no se resuelve, consulta en la Inspección del Trabajo.

## Cómo aparece en tu liquidación

La gratificación es una de las formas de remuneración que define el artículo 42 del Código del Trabajo. Por eso aparece entre los **haberes imponibles**, normalmente como «Gratificación legal» o «Gratificación art. 50», y sobre ella se descuentan AFP, salud y seguro de cesantía, además del impuesto único si corresponde.

{% set base = 700000 %}
{% set grat = calc.gratificacion_legal(base, p) %}
{% set r = calc.sueldo_liquido(base + grat, p, afp=calc.afp_mas_barata(p)) %}
Con un sueldo base de {{ base|pesos }}, AFP {{ p.nombres_afp[calc.afp_mas_barata(p)] }}, Fonasa y contrato indefinido:

| Concepto | Monto |
|---|---:|
| Sueldo base | {{ base|pesos }} |
| Gratificación legal ({{ tasa|porcentaje(0) }}) | {{ grat|pesos }} |
| **Total imponible** | **{{ r.imponible|pesos }}** |
| AFP, salud y seguro de cesantía | -{{ (r.afp + r.salud + r.cesantia)|pesos }} |
| Impuesto único | {% if r.impuesto %}-{{ r.impuesto|pesos }}{% else %}$0 (exento){% endif %} |
| **Sueldo líquido** | **{{ r.liquido|pesos }}** |

Si la calculas tú, recuerda que el porcentaje se aplica antes de los descuentos. En la [calculadora de sueldo líquido]({{ ruta('/calculadoras/sueldo-liquido/') }}) puedes marcar la opción de sumar la gratificación legal a tu sueldo base, y en la guía para [leer tu liquidación de sueldo]({{ ruta('/guias/como-leer-tu-liquidacion-de-sueldo/') }}) verás el resto de los haberes y descuentos.

## Si te vas antes de terminar el año

Si tu contrato termina antes de completar el año, tienes derecho a la gratificación en proporción a los meses trabajados (artículo 52). Según la Dirección del Trabajo, se cuentan solo los meses completos: los días que no alcanzan a formar un mes no se consideran. Si te la pagaban mes a mes, ya la fuiste recibiendo en cada liquidación; si tu empleador la paga una vez al año, revisa que la parte proporcional aparezca en el finiquito.

Cuando la gratificación se paga una vez al año, no forma parte de la base de cálculo de la indemnización por años de servicio: el artículo 172 excluye los beneficios que se pagan por una sola vez al año, y nombra expresamente las gratificaciones. Lo explicamos en la guía sobre [cómo se calcula el finiquito]({{ ruta('/guias/como-calcular-el-finiquito/') }}).

Las reglas de la gratificación tienen matices según la empresa y lo pactado en cada contrato. Si tienes dudas sobre tu caso, consulta en la Dirección del Trabajo.
