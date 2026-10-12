---
titulo: "Boleta de honorarios {{ hoy.year }}: retención, líquido y cotizaciones"
descripcion: "Cómo calcular el bruto y el líquido de una boleta de honorarios con la retención de {{ p.retencion_honorarios|porcentaje(2) }}, qué cotizaciones pagas y quién está exento."
h1: "Boleta de honorarios: retención, líquido y cotizaciones"
resumen: "En {{ hoy.year }} se retiene el {{ p.retencion_honorarios|porcentaje(2) }} de cada boleta. Cómo pasar de bruto a líquido, cómo sube la tasa hasta 2028 y cómo se usa la retención para pagar tus cotizaciones."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: impuestos
orden: 10
calculadoras:
  - /calculadoras/boleta-honorarios/
fuentes:
  - nombre: "SII: Boleta de honorarios, retención vigente y pago provisional mensual"
    url: "https://www.sii.cl/destacados/boletas_honorarios/index.html"
  - nombre: "SII: Aumento gradual de la retención de honorarios y protección social (Ley 21.133)"
    url: "https://www.sii.cl/destacados/boletas_honorarios/aumento_gradual.html"
  - nombre: "ChileAtiende: Cotización de trabajadores que emiten boletas de honorarios"
    url: "https://www.chileatiende.gob.cl/fichas/12016-cotizacion-de-trabajadores-que-emiten-boletas-de-honorarios"
  - nombre: "SII: Boleta de prestación de servicios de terceros electrónica"
    url: "https://www.sii.cl/ayudas/ayudas_por_servicios/2032-bte-2034.html"
faq:
  - pregunta: "¿Cuánto se retiene en una boleta de honorarios en {{ hoy.year }}?"
    respuesta: "En {{ hoy.year }} la retención es de {{ p.retencion_honorarios|porcentaje(2) }} del monto bruto de la boleta. La Ley 21.133 la sube cada año desde 2020, cuando fue de 10,75%, hasta llegar a 17% en 2028."
  - pregunta: "¿Cómo calculo el bruto de una boleta para recibir un monto líquido?"
    respuesta: "Divide el líquido que quieres recibir por {{ (1 - p.retencion_honorarios)|numero(4) }}, que es 1 menos la tasa de retención. Por ejemplo, para recibir $500.000 líquidos debes emitir la boleta por {{ calc.honorarios_desde_liquido(500000, p).bruto|pesos }}."
  - pregunta: "¿Me devuelven la retención de las boletas de honorarios?"
    respuesta: "En parte. En la Operación Renta de abril, las retenciones del año anterior se usan primero para pagar tus cotizaciones y después tu impuesto anual; si queda saldo, se te devuelve. Si no estás obligado a cotizar, la retención solo se descuenta del impuesto y el resto se devuelve."
  - pregunta: "¿Quiénes no están obligados a cotizar por sus boletas de honorarios?"
    respuesta: "Los hombres que tenían 55 años o más y las mujeres que tenían 50 o más al 1 de enero de 2018, los pensionados (salvo por invalidez parcial), quienes están en un régimen previsional distinto de las AFP y quienes emitieron boletas por menos de cinco ingresos mínimos mensuales en el año. A todos se les retiene igual."
  - pregunta: "¿Qué pasa si quien me paga la boleta no hace la retención?"
    respuesta: "Si emites la boleta sin retención, por ejemplo porque tu cliente es una persona que no está obligada a retener, tú debes declarar y pagar ese mismo porcentaje como pago provisional mensual (PPM) en tu Formulario 29 del mes siguiente."
---
{% set tasa = p.retencion_honorarios %}
{% set ejemplo = calc.honorarios_desde_bruto(1000000, p) %}
La boleta de honorarios es el documento con que cobras un trabajo independiente. En {{ hoy.year }}, quien te paga retiene el **{{ tasa|porcentaje(2) }}** del monto bruto: por una boleta de $1.000.000 recibes **{{ ejemplo.liquido|pesos }}**. Esa retención no se pierde: en la Operación Renta se usa para pagar tus cotizaciones de pensión y salud y tu impuesto anual, y lo que sobra se te devuelve.

## Qué es la boleta de honorarios

La boleta de honorarios electrónica la emiten las personas que trabajan en forma independiente, es decir, que obtienen rentas del ejercicio de una profesión u ocupación lucrativa (artículo 42 N°2 de la Ley sobre Impuesto a la Renta). Para emitirla necesitas haber dado aviso de inicio de actividades de segunda categoría en el SII, y se hace en línea desde sii.cl.

Toda boleta tiene tres montos:

- **Bruto**: el total que cobras, el que aparece en la boleta.
- **Retención**: el porcentaje que se descuenta y se paga al fisco ({{ tasa|porcentaje(2) }} en {{ hoy.year }}).
- **Líquido**: lo que efectivamente recibes.

### Quién paga la retención

Si tu cliente es una empresa o una institución, descuenta la retención, te paga el líquido y declara lo retenido en su Formulario 29. Si emites la boleta sin retención, por ejemplo porque tu cliente es una persona que no está obligada a retener, recibes el bruto completo y tú debes declarar y pagar ese mismo porcentaje como pago provisional mensual (PPM) en tu Formulario 29 del mes siguiente.

## Cómo calcular el bruto y el líquido

Con la tasa de {{ hoy.year }}, las fórmulas son:

- Retención = bruto × {{ tasa|porcentaje(2) }}
- Líquido = bruto − retención = bruto × {{ (1 - tasa)|numero(4) }}
- Bruto = líquido ÷ {{ (1 - tasa)|numero(4) }}

{% set desde_liquido = calc.honorarios_desde_liquido(800000, p) %}
**Del bruto al líquido.** Si cobras $1.000.000 brutos, la retención es $1.000.000 × {{ tasa|porcentaje(2) }} = {{ ejemplo.retencion|pesos }} y recibes {{ ejemplo.liquido|pesos }}.

**Del líquido al bruto.** Si acordaste recibir $800.000 líquidos, divide 800.000 por {{ (1 - tasa)|numero(4) }}: la boleta debe ser por **{{ desde_liquido.bruto|pesos }}**, con una retención de {{ desde_liquido.retencion|pesos }}. Como la retención se redondea al peso, a veces hay que ajustar el bruto en $1 para que el líquido calce exacto.

| Bruto | Retención ({{ tasa|porcentaje(2) }}) | Líquido |
|---:|---:|---:|
{% for monto in [100000, 250000, 500000, 1000000, 1500000, 2000000] -%}
{% set h = calc.honorarios_desde_bruto(monto, p) -%}
| {{ h.bruto|pesos }} | {{ h.retencion|pesos }} | {{ h.liquido|pesos }} |
{% endfor %}

En la [calculadora de boleta de honorarios]({{ ruta('/calculadoras/boleta-honorarios/') }}) puedes hacer el cálculo con cualquier monto, en ambos sentidos.

## La retención sube cada año hasta 2028

La Ley 21.133, publicada el 2 de febrero de 2019, incorporó a quienes emiten boletas de honorarios a la seguridad social. Para reunir el dinero de esas cotizaciones, la retención, que hasta 2019 era de 10%, sube en forma gradual: 0,75 puntos por año desde 2020 y 1 punto en 2028, cuando llega a 17%.

| Año | Retención |
|---|---:|
{% for anio, valor in [(2020, 0.1075), (2021, 0.115), (2022, 0.1225), (2023, 0.13), (2024, 0.1375), (2025, 0.145), (2026, 0.1525), (2027, 0.16), (2028, 0.17)] -%}
| {{ anio }}{% if anio == 2028 %} en adelante{% endif %}{% if anio == hoy.year or (anio == 2028 and hoy.year > 2028) %} (este año){% endif %} | {{ valor|porcentaje(2) }} |
{% endfor %}

El aumento de la retención no es un impuesto nuevo: es la forma de juntar durante el año lo que después se paga en cotizaciones.

## Para qué se usa la retención: tus cotizaciones

Desde la Ley 21.133, quienes emiten boletas de honorarios deben cotizar para la seguridad social, sin opción de renunciar. No pagas nada mes a mes: el pago es anual y se hace con tus retenciones en la Operación Renta. Las cotizaciones cubren:

- **Pensión**: {{ p.tasa_afp|porcentaje(0) }} para tu cuenta individual en la AFP, más la comisión de tu AFP.
- **Seguro de Invalidez y Sobrevivencia (SIS)**.
- **Salud**: {{ p.salud_obligatoria|porcentaje(0) }}, para Fonasa o tu isapre.
- **Seguro de accidentes del trabajo y enfermedades profesionales** (Ley 16.744).
- **Seguro para el acompañamiento de niños y niñas (Ley SANNA)**, que financia un permiso con subsidio para que madres y padres acompañen a un hijo o hija con una condición grave de salud.

### Cómo se calcula

{% set tope = p.tope_imponible_uf %}
{% set decimales_tope = 0 if tope == tope|round else 1 %}
1. El SII suma tus honorarios brutos del año y calcula la **renta imponible, que es el 80%** de ese total.
2. Sobre esa renta calcula cada cotización, con un tope anual de 12 veces el tope imponible mensual (con el tope actual de {{ tope|numero(decimales_tope) }} UF, son {{ (12 * tope)|numero(decimales_tope) }} UF al año).
3. Las cotizaciones se pagan con tus retenciones a través de la Tesorería, que las deposita en tu AFP, tu sistema de salud y los seguros.

{% set anual = 12000000 %}
Por ejemplo, si en {{ hoy.year }} emites boletas por $12.000.000 brutos, te retendrán {{ (anual * tasa)|pesos }} en el año. En la Operación Renta {{ hoy.year + 1 }}, tu renta imponible será {{ (anual * 0.8)|pesos }}, y solo la pensión ({{ p.tasa_afp|porcentaje(0) }}) y la salud ({{ p.salud_obligatoria|porcentaje(0) }}) suman {{ (anual * 0.8 * (p.tasa_afp + p.salud_obligatoria))|pesos }}. A eso se agregan la comisión de la AFP y los seguros, que también se pagan con la retención.

### Cobertura total o parcial

Al pagar en la Operación Renta quedas cubierto desde el 1 de julio de ese año hasta el 30 de junio del año siguiente.
{% if hoy.year < 2028 %}
Mientras dura la transición de la ley puedes elegir entre dos opciones:

- **Cobertura total**: cotizas para salud y pensión sobre el 100% de la renta imponible.
- **Cobertura parcial**: cotizas para salud y pensión sobre una parte de la renta imponible (en la Operación Renta 2026 fue el 80%). Recibes una devolución mayor, pero ahorras menos para tu pensión y los subsidios por licencia médica se calculan sobre una renta más baja.

El SIS, el seguro de accidentes y la Ley SANNA siempre se pagan completos. El porcentaje de la cobertura parcial sube cada año y desde la Operación Renta 2028 solo existirá la cobertura total.
{% else %}
Desde la Operación Renta 2028 la cobertura es siempre total: cotizas para salud y pensión sobre el 100% de la renta imponible. Durante la transición de la Ley 21.133 existía además una cobertura parcial, que permitía cotizar sobre una parte de la renta a cambio de una devolución mayor.
{% endif %}
Si tienes isapre y tu plan cuesta más de lo que cotizas, la diferencia la pagas directamente a la isapre cada mes.

## La devolución en la Operación Renta

En tu declaración anual de renta, las retenciones del año anterior se aplican en este orden:

1. **Tus cotizaciones**, si estás obligado a cotizar.
2. **Tu impuesto anual** (Global Complementario), que se calcula sobre todas tus rentas del año. Por los honorarios puedes rebajar gastos presuntos de 30% del monto bruto, con un tope de 15 UTA (unos {{ (180 * utm_hoy)|pesos }} con la UTM de este mes), o tus gastos efectivos si puedes acreditarlos (artículo 50 de la Ley sobre Impuesto a la Renta).
3. **Si sobra dinero, se te devuelve.** Si falta, pagas la diferencia: el impuesto, en la misma declaración, y las cotizaciones que la retención no alcanzó a cubrir, directamente en las instituciones de previsión.

## Quiénes no están obligados a cotizar

Según la ley, no deben cotizar por sus honorarios:

- Los hombres que tenían 55 años o más y las mujeres que tenían 50 años o más al 1 de enero de 2018.
- Los pensionados, salvo quienes reciben una pensión de invalidez parcial.
- Quienes están afiliados a un régimen previsional distinto de las AFP, como el IPS, Dipreca o Capredena.
- Quienes en el año emitieron boletas por menos de cinco ingresos mínimos mensuales brutos. Con el ingreso mínimo actual de {{ p.imm|pesos }} son {{ (5 * p.imm)|pesos }}; el SII informa el monto exacto en cada Operación Renta.
- Quienes cotizaron como trabajadores dependientes por el tope imponible todos los meses del año.

Si además trabajas con contrato, tu sueldo cotiza primero y por los honorarios cotizas solo hasta completar el tope imponible anual. En todos estos casos la retención se aplica igual y se recupera en la Operación Renta, descontado el impuesto que corresponda.

## Boleta de prestación de servicios de terceros

Si prestas un servicio pero no tienes inicio de actividades y no puedes emitir boletas de honorarios, la empresa que te paga puede emitir por ti una **boleta de prestación de servicios de terceros electrónica**. La emiten las empresas y otros contribuyentes de primera categoría obligados a llevar contabilidad, las personas jurídicas en general, las instituciones fiscales y las municipalidades, entre otros.

Quien emite esta boleta retiene el mismo porcentaje que en una boleta de honorarios ({{ tasa|porcentaje(2) }} en {{ hoy.year }}) y lo paga al fisco. Para ti son rentas de honorarios: se declaran en la Operación Renta junto con tus boletas, y lo retenido se descuenta de lo que debas pagar; si sobra, se te devuelve.

Esta guía es informativa y no reemplaza la asesoría del SII. Antes de declarar, revisa en sii.cl el detalle de tus retenciones y del cálculo de tus cotizaciones.
