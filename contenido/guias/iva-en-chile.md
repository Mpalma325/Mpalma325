---
titulo: "IVA en Chile: tasa de {{ p.iva|porcentaje(0) }} y cómo agregarlo o quitarlo ({{ hoy.year }})"
descripcion: "Cómo agregar y quitar el IVA de {{ p.iva|porcentaje(0) }} a un precio, con fórmulas y ejemplos, qué son el débito y el crédito fiscal y qué servicios pagan IVA desde 2023."
h1: "IVA en Chile: cómo se calcula y quién lo paga"
resumen: "La tasa de {{ p.iva|porcentaje(0) }}, cómo sacar el neto desde un precio con IVA y al revés, qué son el débito y el crédito fiscal y qué cambió con el IVA a los servicios y a las compras en el extranjero."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: impuestos
orden: 30
calculadoras:
  - /calculadoras/iva/
fuentes:
  - nombre: "SII: Ley sobre Impuesto a las Ventas y Servicios (DL 825), texto actualizado"
    url: "https://www.sii.cl/normativa_legislacion/sobreventasyservicios.pdf"
  - nombre: "SII: ¿Cuál es la tasa del Impuesto al Valor Agregado (IVA)?"
    url: "https://www.sii.cl/preguntas_frecuentes/impuestos_mensuales/001_130_0572.htm"
  - nombre: "SII: Circular N° 47 de 2003, alza de la tasa del IVA a 19% (Ley 19.888)"
    url: "https://www.sii.cl/documentos/circulares/2003/circu47.htm"
  - nombre: "SII: IVA en la prestación de servicios, normativa y exenciones (Ley 21.420)"
    url: "https://www.sii.cl/destacados/iva_prestacion_servicios/"
  - nombre: "SII: Instrucciones para llenar el Formulario 29 (débito, crédito y remanente)"
    url: "https://www.sii.cl/servicios_online/instrucciones_f29_20241112.pdf"
  - nombre: "SII: IVA a bienes comprados en el extranjero por hasta 500 dólares (Ley 21.713)"
    url: "https://www.sii.cl/destacados/iva_bienes/index.html"
faq:
  - pregunta: "¿Cómo se calcula el IVA de un precio?"
    respuesta: "{% set e = calc.iva_desde_neto(10000, p) %}Multiplica el precio neto por {{ p.iva|numero(2) }} para obtener el IVA, o por {{ (1 + p.iva)|numero(2) }} para obtener el precio final con IVA. Por ejemplo, un neto de {{ e.neto|pesos }} tiene un IVA de {{ e.iva|pesos }} y un total de {{ e.total|pesos }}."
  - pregunta: "¿Cómo saco el IVA de un precio que ya lo incluye?"
    respuesta: "{% set e = calc.iva_desde_total(100000, p) %}Divide el precio final por {{ (1 + p.iva)|numero(2) }} para obtener el neto y resta el neto del total para obtener el IVA. Por ejemplo, {{ e.total|pesos }} con IVA son {{ e.neto|pesos }} netos y {{ e.iva|pesos }} de IVA."
  - pregunta: "¿Desde cuándo el IVA en Chile es de 19%?"
    respuesta: "Desde el 1 de octubre de 2003, cuando la Ley 19.888 lo subió desde 18%. Esa ley preveía volver a 18% en 2007, pero la Ley 20.102, de 2006, derogó esa rebaja. La tasa está en el artículo 14 de la Ley sobre Impuesto a las Ventas y Servicios (DL 825)."
  - pregunta: "¿Las boletas de honorarios pagan IVA?"
    respuesta: "No. Los ingresos de quienes trabajan a honorarios (artículo 42 N° 2 de la Ley sobre Impuesto a la Renta) están exentos de IVA por el artículo 12, letra E, N° 8 del DL 825, y la Ley 21.420 mantuvo esa exención. En su lugar, la boleta lleva una retención de impuesto: {{ p.retencion_honorarios|porcentaje(2) }} en {{ hoy.year }}."
  - pregunta: "¿Qué es el crédito fiscal del IVA?"
    respuesta: "Es el IVA que una empresa pagó en las compras y servicios de su giro, respaldado con facturas. Cada mes lo descuenta del IVA de sus ventas (el débito fiscal) en el Formulario 29 y paga solo la diferencia. Si el crédito es mayor, el saldo pasa al mes siguiente como remanente."
  - pregunta: "¿Las compras en tiendas extranjeras pagan IVA?"
    respuesta: "Sí. Desde el 25 de octubre de 2025, las compras remotas de bienes de hasta 500 dólares, incluido el envío, a vendedores o plataformas sin domicilio en Chile pagan IVA (Ley 21.713). Si la plataforma está inscrita en el SII, lo cobra al momento de la compra; si no, se paga al importar el producto."
---
{% set tasa = p.iva %}
{% set factor = 1 + tasa %}
El IVA (impuesto al valor agregado) grava en Chile la venta de bienes y la prestación de servicios con una tasa de **{{ tasa|porcentaje(0) }}** sobre el precio neto. Para agregarlo a un precio neto, multiplica por {{ factor|numero(2) }}; para quitarlo de un precio final, divide por {{ factor|numero(2) }}. Aquí tienes las fórmulas, ejemplos con redondeo y lo básico sobre quién lo paga y qué está exento.

## La tasa del IVA: {{ tasa|porcentaje(0) }}

La tasa general del IVA está en el artículo 14 de la Ley sobre Impuesto a las Ventas y Servicios (decreto ley 825, de 1974). Es de 19% desde el 1 de octubre de 2003, cuando la Ley 19.888 la subió desde 18%. Esa ley preveía volver a 18% el 1 de enero de 2007, pero la Ley 20.102, de 2006, derogó esa rebaja, así que la tasa de 19% no tiene fecha de término.

El IVA se calcula sobre el **precio neto**, es decir, el valor de la venta o del servicio sin el impuesto. El precio final que pagas en una boleta ya lo incluye.

## Cómo agregar el IVA a un precio neto

- IVA = neto × {{ tasa|numero(2) }}
- Precio con IVA = neto × {{ factor|numero(2) }}

{% set e = calc.iva_desde_neto(250000, p) %}
Por ejemplo, un servicio de {{ e.neto|pesos }} netos lleva un IVA de {{ e.iva|pesos }} y un total de {{ e.total|pesos }}.

| Neto | IVA ({{ tasa|porcentaje(0) }}) | Total |
|---:|---:|---:|
{% for monto in [1000, 10000, 84034, 250000, 1000000] -%}
{% set fila = calc.iva_desde_neto(monto, p) -%}
| {{ fila.neto|pesos }} | {{ fila.iva|pesos }} | {{ fila.total|pesos }} |
{% endfor %}

### Redondeo al peso

El IVA no lleva centavos. En la factura electrónica, el formato del SII lo define como el monto neto multiplicado por la tasa y exige que sea un número entero de pesos. En esta guía y en la calculadora, el IVA se redondea al peso más cercano.

## Cómo sacar el IVA de un precio que ya lo incluye

- Neto = precio con IVA ÷ {{ factor|numero(2) }}
- IVA = precio con IVA − neto

{% set d = calc.iva_desde_total(100000, p) %}
Por ejemplo, de un precio final de {{ d.total|pesos }}, el neto es {{ d.total|pesos }} ÷ {{ factor|numero(2) }} = {{ d.neto|pesos }} y el IVA es {{ d.iva|pesos }}. El neto se redondea al peso y el IVA se obtiene por diferencia, para que neto más IVA dé exactamente el precio.

Un error frecuente es restar el {{ tasa|porcentaje(0) }} al precio final: {{ d.total|pesos }} × {{ (1 - tasa)|numero(2) }} = {{ (d.total * (1 - tasa))|pesos }}, que no es el neto. El {{ tasa|porcentaje(0) }} se calcula sobre el neto, no sobre el total, así que el IVA es solo el {{ (tasa / factor)|porcentaje(2) }} del precio final.

| Precio con IVA | Neto | IVA incluido |
|---:|---:|---:|
{% for monto in [1000, 10000, 50000, 100000, 1000000] -%}
{% set fila = calc.iva_desde_total(monto, p) -%}
| {{ fila.total|pesos }} | {{ fila.neto|pesos }} | {{ fila.iva|pesos }} |
{% endfor %}

### Cuánto IVA pagas en tus compras

{% set g = calc.iva_desde_total(500000, p) %}
Como el IVA ya viene dentro del precio, puedes saber cuánto pagaste multiplicando el total por {{ (tasa * 100)|numero }} y dividiendo por {{ (100 + tasa * 100)|numero }}. Si en un mes gastas {{ g.total|pesos }} en productos y servicios afectos, {{ g.iva|pesos }} corresponden a IVA. No necesitas calcularlo en cada compra: la boleta electrónica debe indicar por separado el monto del IVA incluido en el total.

### Descuentos

{% set lista = calc.iva_desde_neto(100000, p) %}
{% set rebajado = calc.iva_desde_neto(90000, p) %}
Da lo mismo aplicar un descuento antes o después de agregar el IVA: un 10% de descuento sobre {{ lista.neto|pesos }} netos deja {{ rebajado.neto|pesos }} netos y {{ rebajado.total|pesos }} con IVA, lo mismo que descontar 10% a {{ lista.total|pesos }}. Lo que sí es un error es sumar el IVA dos veces: si un precio dice "IVA incluido", no le agregues otro {{ tasa|porcentaje(0) }}.

Si necesitas hacer estos cálculos seguido, usa la [calculadora de IVA]({{ ruta('/calculadoras/iva/') }}), que hace las dos operaciones con el mismo redondeo de esta guía.

## Quién paga el IVA: débito y crédito fiscal

El IVA va incluido en el precio que paga el comprador, pero quien lo declara y lo paga al fisco es el vendedor o el prestador del servicio, cada mes, en el Formulario 29. Para eso, las empresas llevan dos cuentas:

- **Débito fiscal**: el IVA de sus ventas y servicios del mes.
- **Crédito fiscal**: el IVA que pagaron en las compras y servicios de su giro, respaldado con las facturas de sus proveedores (artículo 23 del DL 825).

Si el débito es mayor, pagan la diferencia. Si el crédito es mayor, el saldo queda como **remanente** para usarlo el mes siguiente, reajustado como indica el artículo 27 del DL 825.

{% set venta = calc.iva_desde_neto(1000000, p) %}
{% set compra = calc.iva_desde_neto(400000, p) %}
Por ejemplo, si en el mes una empresa vende {{ venta.neto|pesos }} netos y compra insumos por {{ compra.neto|pesos }} netos, su débito fiscal es {{ venta.iva|pesos }}, su crédito fiscal es {{ compra.iva|pesos }} y paga {{ (venta.iva - compra.iva)|pesos }} de IVA: el {{ tasa|porcentaje(0) }} de los {{ (venta.neto - compra.neto)|pesos }} de valor que agregó. Así, cada empresa de la cadena paga el impuesto solo sobre el valor que agrega, y el consumidor final, que no tiene a quién descontárselo, termina pagándolo completo.

## IVA a los servicios desde 2023

Hasta 2022 solo pagaban IVA los servicios de algunas actividades, como las comerciales e industriales. La Ley 21.420 lo extendió a los servicios en general: desde el 1 de enero de 2023 se grava cualquier prestación que una persona realice para otra a cambio de una remuneración, salvo que la ley la exima expresamente.

Las principales exenciones son:

- **Trabajo a honorarios.** Los ingresos de las personas que emiten boletas de honorarios (rentas del artículo 42 N° 2 de la Ley sobre Impuesto a la Renta) siguen exentos por el artículo 12, letra E, N° 8 del DL 825. Su boleta no lleva IVA, sino una retención de impuesto ({{ p.retencion_honorarios|porcentaje(2) }} en {{ hoy.year }}), como explica la [guía de la boleta de honorarios]({{ ruta('/guias/boleta-de-honorarios/') }}).
- **Sociedades de profesionales.** La misma exención alcanza a las sociedades de profesionales que cumplen los requisitos del SII, aunque declaren en primera categoría. Entre otros requisitos, sus socios deben ser personas naturales u otras sociedades de profesionales, deben dedicarse solo a servicios o asesorías profesionales y deben estar registradas como sociedad de profesionales en el SII.
- **Salud ambulatoria.** La Ley 21.420 eximió las prestaciones de salud de carácter ambulatorio (artículo 12, letra E, N° 20). Según el SII, lo que importa es que la atención sea ambulatoria, no quién la presta; los servicios de laboratorio no entran en esta exención.
- **Educación.** Los establecimientos de educación, por los ingresos de su actividad docente propiamente tal (artículo 13 N° 4).
- **Transporte de pasajeros**, que siguió exento.

El arriendo de un inmueble sin amoblar tampoco paga IVA: solo se grava el arriendo de inmuebles amoblados o con instalaciones o maquinarias que permitan ejercer una actividad comercial o industrial.

Si prestas servicios y tienes dudas sobre tu actividad, revisa la página del SII sobre el IVA a los servicios o consulta a un contador.

## IVA en compras a tiendas extranjeras

Desde el 25 de octubre de 2025, la Ley 21.713 grava con IVA las compras remotas de bienes de hasta 500 dólares, incluidos el envío y otros cargos, a vendedores o plataformas sin domicilio en Chile. Si la plataforma está inscrita en el SII, cobra el IVA al momento de la compra y el producto no paga aranceles ni IVA al importarse. Si no lo cobra, o si la compra supera los 500 dólares, el impuesto se paga al importar, según el procedimiento de Aduanas.

Los servicios que empresas sin domicilio en Chile prestan en forma remota ya pagaban IVA desde la Ley 21.210.

## Boletas y facturas

- La **boleta** es el comprobante que recibes como consumidor, y su total incluye el IVA. Desde 2021, por la Ley 21.210, debe ser electrónica, salvo donde no hay acceso a internet o a la red eléctrica, y la boleta electrónica debe indicar por separado el monto del IVA.
- La **factura** separa el neto, el IVA y el total, y es el documento que permite al comprador usar ese IVA como crédito fiscal.

Esta guía es informativa y no reemplaza la asesoría del SII. Para casos particulares, revisa la normativa en sii.cl o consulta a un contador.
