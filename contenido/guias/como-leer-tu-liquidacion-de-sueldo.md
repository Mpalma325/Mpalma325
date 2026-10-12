---
titulo: "Cómo leer tu liquidación de sueldo: haberes, descuentos y líquido"
descripcion: "Qué significa cada línea de tu liquidación de sueldo: haberes imponibles y no imponibles, descuentos de AFP, salud, cesantía e impuesto, y cómo revisarla."
h1: "Cómo leer tu liquidación de sueldo"
resumen: "Haberes imponibles y no imponibles, descuentos legales y otros descuentos, líquido a pagar: qué significa cada línea de tu liquidación, un ejemplo completo y dónde reclamar si algo no calza."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: trabajo
orden: 20
calculadoras:
  - /calculadoras/sueldo-liquido/
fuentes:
  - nombre: "Código del Trabajo, artículos 41, 42, 54 y 58 (Biblioteca del Congreso Nacional)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=207436"
  - nombre: "Superintendencia de Pensiones: comisiones de las AFP"
    url: "https://www.spensiones.cl/portal/institucional/594/w3-propertyvalue-9897.html"
  - nombre: "Superintendencia de Pensiones: seguro de cesantía"
    url: "https://www.spensiones.cl/portal/institucional/594/w3-propertyvalue-9894.html"
  - nombre: "Servicio de Impuestos Internos: impuesto único de segunda categoría"
    url: "https://www.sii.cl/valores_y_fechas/impuesto_2da_categoria/impuesto2026.htm"
faq:
  - pregunta: "¿Qué descuentos son obligatorios en la liquidación de sueldo?"
    respuesta: "La cotización de AFP ({{ p.tasa_afp|porcentaje(0) }} más la comisión de tu AFP), la de salud ({{ p.salud_obligatoria|porcentaje(0) }}, o el valor de tu plan de isapre si es mayor), el seguro de cesantía si tienes contrato indefinido ({{ p.cesantia_trabajador.indefinido|porcentaje(1) }}) y el impuesto único, si tu sueldo supera el tramo exento."
  - pregunta: "¿La colación y la movilización pagan impuesto?"
    respuesta: "No. Las asignaciones de colación y movilización no son remuneración (artículo 41 del Código del Trabajo), así que no pagan cotizaciones ni impuesto y se suman completas al líquido."
  - pregunta: "¿Cuánto me pueden descontar del sueldo por otros conceptos?"
    respuesta: "Además de los descuentos que exige la ley, el empleador solo puede descontar las sumas que acuerden por escrito, y esos descuentos, en general, no pueden superar el 15% de tu remuneración total (artículo 58 del Código del Trabajo)."
  - pregunta: "¿El empleador está obligado a entregarme la liquidación?"
    respuesta: "Sí. Junto con el pago debe entregarte un comprobante con el monto pagado, la forma en que se calculó y las deducciones efectuadas (artículo 54 del Código del Trabajo)."
  - pregunta: "¿Dónde reclamo si mi liquidación está mal?"
    respuesta: "Primero pide una explicación a tu empleador. Si no se resuelve, puedes consultar o denunciar en la Inspección del Trabajo. Revisa también en tu AFP que las cotizaciones que te descontaron se hayan pagado."
---
{% set barata = calc.afp_mas_barata(p) %}
{% set nombre_afp = p.nombres_afp[barata] %}
{% set comisiones = p.comisiones_afp.values()|list %}
{% set base = 1200000 %}
{% set grat = calc.gratificacion_legal(base, p) %}
{% set colacion = 50000 %}
{% set movilizacion = 40000 %}
{% set anticipo = 100000 %}
{% set r = calc.sueldo_liquido(base + grat, p, afp=barata, no_imponible=colacion + movilizacion) %}
{% set plazo_fijo = calc.sueldo_liquido(base + grat, p, afp=barata, contrato='plazo_fijo', no_imponible=colacion + movilizacion) %}
La liquidación de sueldo es el comprobante que tu empleador debe entregarte junto con el pago. Muestra cuánto ganaste en el mes (haberes), cuánto se descontó y por qué, y el líquido que recibes. Así se lee cada parte, con un ejemplo completo.

## Las partes de una liquidación

El artículo 54 del Código del Trabajo exige que, junto con el pago, el empleador entregue un comprobante con el monto pagado, la forma en que se determinó y los descuentos efectuados. El formato cambia de una empresa a otra, pero casi todas las liquidaciones tienen estas partes:

1. **Encabezado:** tus datos y los del empleador, el mes, los días trabajados, tu AFP y tu sistema de salud.
2. **Haberes imponibles:** las remuneraciones del mes.
3. **Haberes no imponibles:** asignaciones como colación y movilización.
4. **Descuentos legales:** AFP, salud, seguro de cesantía e impuesto.
5. **Otros descuentos:** anticipos, cuotas y descuentos autorizados.
6. **Líquido a pagar:** lo que efectivamente recibes.

## Haberes imponibles

Son tus remuneraciones del mes, y sobre su total se calculan las cotizaciones y el impuesto. Los más comunes son las formas de remuneración del artículo 42:

- **Sueldo base:** el monto fijo mensual. Con jornada completa, no puede ser menor que el ingreso mínimo ({{ p.imm|pesos }} para trabajadores de 18 a 65 años).
- **Gratificación:** si se paga mes a mes con el sistema del artículo 50, es el {{ p.gratificacion_tasa|porcentaje(0) }} de tu remuneración con un tope de {{ (p.gratificacion_tope_imm_anual * p.imm / 12)|pesos }} al mes. Lo explicamos en la guía de [gratificación legal]({{ ruta('/guias/gratificacion-legal/') }}).
- **Horas extra:** se pagan con un recargo de al menos 50%; revisa cómo se calculan en la guía de [jornada y horas extra]({{ ruta('/guias/jornada-laboral-42-horas-y-horas-extra/') }}).
- **Comisiones, bonos y participaciones**, según tu contrato.

Las cotizaciones de AFP y salud tienen un tope de {{ p.tope_imponible_uf|numero(1) }} UF imponibles ({{ (p.tope_imponible_uf * uf_hoy)|pesos }} con la UF de hoy), y la del seguro de cesantía, uno de {{ p.tope_cesantia_uf|numero(1) }} UF ({{ (p.tope_cesantia_uf * uf_hoy)|pesos }}). Lo que ganes por sobre esos topes no paga esas cotizaciones, pero sí impuesto.

## Haberes no imponibles

Las asignaciones de colación, movilización, pérdida de caja y desgaste de herramientas, los viáticos y la asignación familiar no son remuneración (artículo 41). No pagan cotizaciones ni impuesto y se suman completas a lo que recibes.

## Descuentos legales

| Descuento | Cuánto | Sobre qué monto |
|---|---|---|
| AFP | {{ p.tasa_afp|porcentaje(0) }} para tu cuenta más la comisión de tu AFP: entre {{ (p.tasa_afp + comisiones|min)|porcentaje(2) }} y {{ (p.tasa_afp + comisiones|max)|porcentaje(2) }} en total | Total imponible, hasta {{ p.tope_imponible_uf|numero(1) }} UF |
| Salud | {{ p.salud_obligatoria|porcentaje(0) }} para Fonasa o tu isapre; si tu plan cuesta más, se descuenta el valor del plan | Total imponible, hasta {{ p.tope_imponible_uf|numero(1) }} UF |
| Seguro de cesantía | {{ p.cesantia_trabajador.indefinido|porcentaje(1) }} con contrato indefinido; nada con contrato a plazo fijo o por obra | Total imponible, hasta {{ p.tope_cesantia_uf|numero(1) }} UF |
| Impuesto único | Según la tabla mensual del SII; exento hasta {{ (p.tramos_impuesto[0].hasta * p.utm)|pesos }} | Total imponible menos AFP, salud (hasta el {{ p.salud_obligatoria|porcentaje(0) }}) y seguro de cesantía |

Algunas liquidaciones muestran también las cotizaciones que paga el empleador, como su parte del seguro de cesantía o su aporte al sistema de pensiones. Esas no se descuentan de tu sueldo: son un costo adicional para la empresa.

## Otros descuentos

Además de los descuentos legales, en tu liquidación pueden aparecer anticipos de sueldo, cuotas sindicales, cuotas de créditos con una caja de compensación, ahorro previsional voluntario (APV) o seguros complementarios.

El artículo 58 obliga al empleador a descontar los impuestos, las cotizaciones de seguridad social, las cuotas sindicales y las obligaciones con instituciones de previsión o con organismos públicos. Los demás descuentos requieren un **acuerdo escrito** entre tú y el empleador y, en general, no pueden superar el **15% de tu remuneración total**.

El empleador tampoco puede descontarte por arriendo de habitación, luz, agua, uso de herramientas, medicamentos o atención médica, ni multas que no estén en el reglamento interno de la empresa.

## Ejemplo completo

Valentina tiene contrato indefinido, AFP {{ nombre_afp }} y Fonasa. Gana un sueldo base de {{ base|pesos }}, más gratificación legal y asignaciones de colación y movilización. Este mes pidió un anticipo de {{ anticipo|pesos }}.

| Concepto | Monto |
|---|---:|
| Sueldo base | {{ base|pesos }} |
| Gratificación legal | {{ grat|pesos }} |
| **Total imponible** | **{{ r.imponible|pesos }}** |
| Colación | {{ colacion|pesos }} |
| Movilización | {{ movilizacion|pesos }} |
| **Total haberes** | **{{ (r.bruto + r.no_imponible)|pesos }}** |
| AFP {{ nombre_afp }} ({{ r.tasa_afp_total|porcentaje(2) }}) | -{{ r.afp|pesos }} |
| Salud, Fonasa ({{ p.salud_obligatoria|porcentaje(0) }}) | -{{ r.salud|pesos }} |
| Seguro de cesantía ({{ p.cesantia_trabajador.indefinido|porcentaje(1) }}) | -{{ r.cesantia|pesos }} |
| Impuesto único | {% if r.impuesto %}-{{ r.impuesto|pesos }}{% else %}$0 (exento){% endif %} |
| **Total descuentos legales** | **-{{ r.total_descuentos|pesos }}** |
| Anticipo de sueldo | -{{ anticipo|pesos }} |
| **Líquido a pagar** | **{{ (r.liquido - anticipo)|pesos }}** |

La gratificación es el tope mensual, porque el {{ p.gratificacion_tasa|porcentaje(0) }} de {{ base|pesos }} lo supera. {% if r.impuesto %}El impuesto se calcula sobre {{ r.base_tributable|pesos }}, que es el total imponible menos AFP, salud y seguro de cesantía. Ese monto cae en el tramo con tasa de {{ r.tasa_marginal|porcentaje(0) }}: {{ r.base_tributable|pesos }} × {{ r.tasa_marginal|porcentaje(0) }} menos la rebaja del tramo ({{ (p.tramos_impuesto[r.tramo].rebaja * p.utm)|pesos }}) da {{ r.impuesto|pesos }}.{% else %}La base del impuesto ({{ r.base_tributable|pesos }}) queda en el tramo exento, así que no paga impuesto único.{% endif %} La colación y la movilización no tienen descuentos.

Sin el anticipo, su líquido sería {{ r.liquido|pesos }}. Si su contrato fuera a plazo fijo, no le descontarían seguro de cesantía y el líquido sin anticipo sería {{ plazo_fijo.liquido|pesos }}. Puedes repetir el cálculo en la [calculadora de sueldo líquido]({{ ruta('/calculadoras/sueldo-liquido/') }}): ingresa {{ r.imponible|pesos }} como sueldo bruto y {{ (colacion + movilizacion)|pesos }} como colación y movilización.

## Cómo revisar tu liquidación

1. **Días y período:** que correspondan al mes pagado. Las ausencias y los días de licencia médica reducen lo que paga el empleador.
2. **Sueldo base:** el mismo de tu contrato.
3. **Gratificación:** el {{ p.gratificacion_tasa|porcentaje(0) }} de tu remuneración o el tope mensual, si es lo que pactaste.
4. **Horas extra:** que coincidan con las horas trabajadas y con el valor que corresponde.
5. **AFP y salud:** la tasa debe ser {{ p.tasa_afp|porcentaje(0) }} más la comisión de tu AFP, y la salud, {{ p.salud_obligatoria|porcentaje(0) }} o el valor de tu plan.
6. **Seguro de cesantía:** solo se descuenta con contrato indefinido.
7. **Impuesto:** compáralo con la [tabla del impuesto único]({{ ruta('/impuesto-unico/') }}) del mes.
8. **Otros descuentos:** que los hayas autorizado por escrito.
9. **Cotizaciones pagadas:** pide el certificado de cotizaciones en tu AFP y revisa que aparezca lo que te descontaron.

## Dónde reclamar

Si algo no calza, pide primero una explicación a tu empleador o al área de remuneraciones. Si no se resuelve, puedes consultar o presentar una denuncia en la Inspección del Trabajo, de forma presencial o en el sitio de la Dirección del Trabajo. Si te descontaron cotizaciones que no aparecen pagadas, infórmalo también a tu AFP, que debe cobrarlas al empleador.

Este ejemplo es referencial. Tu liquidación puede incluir otros conceptos según tu contrato, como bonos, comisiones o asignación familiar.
