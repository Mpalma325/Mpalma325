---
titulo: "Qué es la CAE de un crédito de consumo y cómo comparar ofertas"
descripcion: "Qué es la carga anual equivalente (CAE), en qué se diferencia de la tasa de interés y del costo total, qué costos incluye y cómo comparar créditos de consumo."
h1: "Qué es la CAE y cómo usarla para comparar créditos de consumo"
resumen: "La CAE resume en un porcentaje anual el costo de un crédito: intereses, seguros, gastos e impuesto. Cómo se calcula, un ejemplo con cifras y qué revisar antes de firmar."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: ahorro
orden: 10
calculadoras:
  - /calculadoras/credito-consumo/
fuentes:
  - nombre: "Decreto 43 de 2012 del Ministerio de Economía: reglamento sobre información al consumidor de créditos de consumo (BCN)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=1041744"
  - nombre: "SERNAC: ¿Qué es la Carga Anual Equivalente (CAE)?"
    url: "https://www.sernac.cl/portal/607/w3-article-2463.html"
  - nombre: "SERNAC: Productos y servicios financieros, guía explicativa (CAE, costo total y hoja resumen)"
    url: "https://www.sernac.cl/portal/619/articles-5551_archivo_01.pdf"
  - nombre: "SII: Impuesto de timbres y estampillas en las operaciones de crédito de dinero"
    url: "https://www.sii.cl/preguntas_frecuentes/otros_impuestos/001_390_1689.htm"
  - nombre: "Ley 18.010 sobre operaciones de crédito de dinero (BCN)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=29438"
  - nombre: "CMF Educa: ¿Es posible pagar anticipadamente un crédito de consumo?"
    url: "https://www.cmfchile.cl/educa/621/w3-article-27324.html"
  - nombre: "SERNAC: en los créditos de consumo no existen seguros obligatorios"
    url: "https://www.sernac.cl/portal/604/w3-article-4982.html"
faq:
  - pregunta: "¿Qué es la CAE de un crédito?"
    respuesta: "La carga anual equivalente (CAE) es un indicador que, expresado como porcentaje, muestra el costo de un crédito en un período de un año, cualquiera sea su plazo. Incluye los intereses, los seguros, los gastos y el impuesto del crédito. Sirve para comparar créditos del mismo monto y plazo."
  - pregunta: "¿Qué diferencia hay entre la tasa de interés y la CAE?"
    respuesta: "La tasa de interés solo mide el precio del dinero prestado. La CAE suma además los demás costos del crédito, como seguros, gastos e impuesto de timbres. Por eso es igual o mayor que la tasa de interés mensual multiplicada por 12."
  - pregunta: "¿Cómo se calcula la CAE?"
    respuesta: "Se busca la tasa mensual con la que el valor presente de todo lo que pagarás (cuotas, seguros y gastos) es igual al monto líquido que recibes, y se multiplica por 12. Es el método del reglamento de información al consumidor de créditos de consumo (Decreto 43 de 2012 del Ministerio de Economía)."
  - pregunta: "¿Puedo pagar antes un crédito de consumo?"
    respuesta: "Sí. Según la CMF, en los créditos de hasta 5.000 UF puedes prepagar aun sin el acuerdo del acreedor, pagando el capital, los intereses hasta ese día y una comisión de prepago de hasta un mes de intereses sobre el capital que prepagas (mes y medio si el crédito es reajustable, como los créditos en UF). Un prepago parcial menor al 10% del saldo requiere el acuerdo del acreedor."
  - pregunta: "¿Qué es la tasa máxima convencional?"
    respuesta: "Es el interés más alto que se puede pactar en un crédito. Se calcula a partir de la tasa de interés corriente, que la CMF determina y publica cada mes según el tipo, el monto y el plazo de la operación. Si se pacta un interés mayor, ese pacto se tiene por no escrito y los intereses se reducen al interés corriente (artículo 8 de la Ley 18.010)."
  - pregunta: "¿Los seguros de un crédito de consumo son obligatorios?"
    respuesta: "No. Según el SERNAC, en los créditos de consumo los seguros son voluntarios: puedes rechazarlos o contratarlos con la compañía que elijas. La excepción son los créditos sociales de las cajas de compensación, que pueden exigir un seguro de desgravamen. Si contratas un seguro, su costo entra en la CAE."
---
{# Ejemplo hipotético (no es una oferta). Las cifras salen de la misma función de la calculadora. #}
{% set monto = 3000000 %}
{% set meses = 36 %}
{% set tasa = 0.015 %}
{% set a = calc.credito_consumo(monto, meses, tasa, p) %}
{% set b = calc.credito_consumo(monto, meses, tasa, p, seguros=4000, gastos=30000, financiar=True) %}
{% set c = calc.credito_consumo(monto, meses, 0.014, p, seguros=6000) %}
La **CAE (carga anual equivalente)** es un porcentaje que resume cuánto te cuesta de verdad un crédito en un año: además de los intereses, incluye los seguros, los gastos y el impuesto del crédito. Por eso es la cifra que debes mirar para comparar créditos de consumo del mismo monto y plazo: a menor CAE, más barato es el crédito.

## Qué es la CAE

La CAE está definida en el reglamento sobre información al consumidor de créditos de consumo (Decreto 43 de 2012 del Ministerio de Economía), que se dictó a partir de la Ley 20.555, conocida como ley del SERNAC Financiero. Según ese reglamento, la CAE es un indicador que, expresado en forma de porcentaje, revela el costo de un crédito en un período anual, cualquiera sea el plazo pactado.

El reglamento obliga a informar la CAE y el costo total del crédito en toda publicidad de créditos de consumo que muestre una cuota o una tasa de interés, y la CAE también debe aparecer en las cotizaciones. El SERNAC recomienda usarla para comparar créditos de igual monto y número de cuotas.

## Tasa de interés, CAE y costo total del crédito

Son tres cifras distintas que conviene no confundir:

| Indicador | Qué mide | Para qué te sirve |
|---|---|---|
| Tasa de interés | Solo el precio del dinero prestado (en los créditos de consumo suele informarse como tasa mensual) | Saber cuánto pagas en intereses |
| CAE | Intereses más todos los costos del crédito, como porcentaje anual | Comparar ofertas del mismo monto y plazo |
| Costo total del crédito | Todo lo que pagarás, en pesos, sumando cuotas y cargos | Saber cuánto te cuesta el crédito de principio a fin |

Como la CAE suma todos los costos, siempre es igual o mayor que la tasa de interés mensual multiplicada por 12. Si una oferta tiene una tasa baja pero una CAE alta, el crédito trae costos adicionales importantes.

## Qué costos incluye la CAE

Además del capital, la tasa de interés y el plazo, la CAE considera:

- **Los seguros asociados** al crédito, como el de desgravamen, y los demás productos o servicios que contrates voluntariamente con él.
- **Los gastos o cargos propios del crédito**, como los notariales.
- **El impuesto de timbres y estampillas** (decreto ley 3.475): {{ p.timbres_tasa_mensual|porcentaje(3) }} del monto del crédito por cada mes o fracción hasta el último vencimiento, con un máximo de {{ p.timbres_tope|porcentaje(1) }}. Como 12 meses suman {{ (12 * p.timbres_tasa_mensual)|porcentaje(3) }}, un crédito de 13 meses o más paga el máximo.

## Ejemplo: misma tasa, distinta CAE

Imagina que necesitas recibir **{{ monto|pesos }}** a **{{ meses }} meses**, con una tasa de interés de **{{ tasa|porcentaje(1) }} mensual** ({{ (tasa * 12)|porcentaje(0) }} anual). Las cifras son hipotéticas, no una oferta real, y en ambos casos el impuesto y los gastos se suman al crédito.

- **Oferta A**, solo con el impuesto de timbres: el monto del crédito sube a {{ a.monto_bruto|pesos }}, porque incluye {{ a.impuesto|pesos }} de impuesto, y la cuota es de {{ a.cuota_total|pesos }}.
- **Oferta B**, con la misma tasa, más un seguro de desgravamen de {{ b.seguros|pesos }} al mes y {{ b.gastos|pesos }} de gastos de otorgamiento: la cuota sube a {{ b.cuota_total|pesos }}.

| Concepto | Oferta A | Oferta B |
|---|---:|---:|
| Dinero que recibes | {{ a.monto_liquido|pesos }} | {{ b.monto_liquido|pesos }} |
| Monto del crédito | {{ a.monto_bruto|pesos }} | {{ b.monto_bruto|pesos }} |
| Cuota mensual | {{ a.cuota_total|pesos }} | {{ b.cuota_total|pesos }} |
| Costo total del crédito | {{ a.costo_total|pesos }} | {{ b.costo_total|pesos }} |
| Pagas por sobre lo recibido | {{ a.sobrecosto|pesos }} | {{ b.sobrecosto|pesos }} |
| Tasa de interés anual | {{ (tasa * 12)|porcentaje(0) }} | {{ (tasa * 12)|porcentaje(0) }} |
| CAE | **{{ a.cae|porcentaje(2) }}** | **{{ b.cae|porcentaje(2) }}** |

Las dos ofertas tienen la misma tasa, pero la B cuesta {{ (b.costo_total - a.costo_total)|pesos }} más y su CAE es {{ ((b.cae - a.cae) * 100)|numero(1) }} puntos más alta. Incluso la oferta A tiene una CAE mayor que la tasa anual, solo por el impuesto de timbres.

### Cómo se calcula

La CAE es la tasa mensual que iguala el valor presente de todo lo que pagarás (cuotas, seguros y gastos) con el monto líquido que recibes, multiplicada por 12. En la oferta B, esa tasa es {{ (b.cae / 12)|porcentaje(3) }} mensual, que por 12 da {{ b.cae|porcentaje(2) }}. Es una anualización simple: la tasa mensual se multiplica por 12, no se capitaliza. Si pagas algo al contado al firmar, se resta de lo que recibes.

No necesitas hacer este cálculo a mano: la [calculadora de crédito de consumo]({{ ruta('/calculadoras/credito-consumo/') }}) usa el mismo método con tus cifras.

## Cómo comparar ofertas de crédito

1. **Pide cotizaciones del mismo monto y plazo.** La CAE solo sirve para comparar créditos equivalentes. La cotización debe informar, entre otros datos, el monto líquido, el plazo y la CAE.
2. **Compara la CAE y el costo total, no solo la tasa o la cuota.** Una oferta C con una tasa más baja, de {{ 0.014|porcentaje(1) }} mensual, pero con un seguro de {{ c.seguros|pesos }} al mes, tiene una CAE de {{ c.cae|porcentaje(2) }} y un costo total de {{ c.costo_total|pesos }}: es más cara que la oferta A, con {{ a.cae|porcentaje(2) }}. Una cuota más baja también puede venir de un plazo más largo, con más intereses en total.
3. **Revisa los seguros.** Según el SERNAC, en los créditos de consumo los seguros son voluntarios (la excepción son los créditos sociales de las cajas de compensación, que pueden exigir un seguro de desgravamen): puedes rechazarlos o contratarlos con la compañía que elijas.
4. **Lee la hoja resumen.** Tienes derecho a conocer la CAE y el costo total del crédito, y al firmar el contrato te deben entregar una hoja resumen con sus principales condiciones.
5. **Simula antes de firmar** con la [calculadora de crédito de consumo]({{ ruta('/calculadoras/credito-consumo/') }}).

## Tasa máxima convencional

En Chile hay un límite legal para los intereses: la **tasa máxima convencional (TMC)**. Se calcula a partir de la tasa de interés corriente, que la Comisión para el Mercado Financiero (CMF) determina y publica cada mes para distintos tipos de operación, según su moneda, monto y plazo. Si un crédito pacta un interés mayor que el máximo, ese pacto se tiene por no escrito y los intereses se reducen al interés corriente (artículo 8 de la Ley 18.010). Revisa la TMC vigente en el sitio de la CMF antes de firmar.

## Derecho a pagar antes (prepago)

Si te sobra dinero, puedes pagar tu crédito antes de tiempo, total o parcialmente. Según la CMF, en los créditos de hasta 5.000 UF puedes hacerlo aun contra la voluntad del acreedor, pagando:

- el capital que prepagas,
- los intereses hasta el día del pago, y
- una **comisión de prepago**, que no puede superar un mes de intereses sobre el capital que prepagas en los créditos no reajustables, como los créditos en pesos, ni mes y medio en los reajustables, como los créditos en UF (artículo 10 de la Ley 18.010).

Un prepago parcial menor al 10% del saldo requiere el acuerdo del acreedor, y el derecho a prepagar es irrenunciable: no se puede eliminar en el contrato. Antes de prepagar, pide a tu banco el monto exacto y compáralo con los intereses que te ahorras.

Esta guía es informativa y no reemplaza la información oficial. Para casos particulares, consulta en el SERNAC o en la CMF.
