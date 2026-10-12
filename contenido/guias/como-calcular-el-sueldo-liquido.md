---
titulo: "Cómo calcular el sueldo líquido en Chile ({{ hoy.year }})"
descripcion: "Cómo pasar del sueldo bruto al líquido: AFP, salud, seguro de cesantía, impuesto único, tope imponible y gratificación, con ejemplos y tablas al día."
h1: "Cómo se calcula el sueldo líquido"
resumen: "Qué te descuentan del sueldo bruto (AFP, salud, seguro de cesantía e impuesto único), cómo funcionan el tope imponible y la gratificación, y ejemplos con los valores vigentes."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: trabajo
orden: 10
calculadoras:
  - /calculadoras/sueldo-liquido/
  - /sueldo-liquido/1000000/
  - /impuesto-unico/
fuentes:
  - nombre: "Comisiones de las AFP (Superintendencia de Pensiones)"
    url: "https://www.spensiones.cl/portal/institucional/594/w3-propertyvalue-9897.html"
  - nombre: "¿En qué consiste la comisión que cobra una AFP? (Superintendencia de Pensiones)"
    url: "https://www.spensiones.cl/portal/institucional/594/w3-article-2810.html"
  - nombre: "Topes imponibles 2026 (Superintendencia de Pensiones)"
    url: "https://www.spensiones.cl/portal/institucional/594/w3-article-16885.html"
  - nombre: "Límite máximo imponible: reajuste y UF con que se convierte (Compendio de Pensiones)"
    url: "https://www.spensiones.cl/portal/compendio/596/w3-propertyvalue-3629.html"
  - nombre: "Impuesto Único de Segunda Categoría 2026 (Servicio de Impuestos Internos)"
    url: "https://www.sii.cl/valores_y_fechas/impuesto_2da_categoria/impuesto2026.htm"
  - nombre: "Beneficios tributarios del APV (Superintendencia de Pensiones)"
    url: "https://www.spensiones.cl/portal/institucional/594/w3-article-5795.html"
  - nombre: "Código del Trabajo, artículos 41, 42 y 50 (Biblioteca del Congreso Nacional)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=207436"
  - nombre: "Dirección del Trabajo: monto de las asignaciones de colación y movilización"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60235.html"
  - nombre: "Cotizaciones del seguro de cesantía (Superintendencia de Pensiones)"
    url: "https://www.spensiones.cl/portal/institucional/594/w3-propertyvalue-9902.html"
  - nombre: "Dirección del Trabajo: ¿Durante cuánto tiempo se cotiza para el seguro de cesantía?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-95311.html"
  - nombre: "Seguro de Cesantía (AFC Chile)"
    url: "https://www.afc.cl/"
  - nombre: "Cotización de cargo del empleador (Superintendencia de Pensiones)"
    url: "https://www.spensiones.cl/portal/institucional/594/w3-propertyvalue-10906.html"
  - nombre: "Aportes del empleador al sistema de pensiones (ChileAtiende)"
    url: "https://www.chileatiende.gob.cl/fichas/130987-aportes-del-empleador-al-sistema-de-pensiones"
  - nombre: "Cómo se financia el seguro de accidentes del trabajo y la Ley SANNA (SUSESO)"
    url: "https://www.suseso.gob.cl/606/w3-article-18613.html"
faq:
  - pregunta: "¿Qué diferencia hay entre sueldo bruto y sueldo líquido?"
    respuesta: "El bruto es el total de tus haberes antes de descuentos. El líquido es lo que recibes: la remuneración imponible más las asignaciones no imponibles, menos AFP, salud, seguro de cesantía e impuesto único."
  - pregunta: "¿Cuánto me descuenta la AFP?"
    respuesta: "El {{ p.tasa_afp|porcentaje(0) }} de tu remuneración imponible, que va a tu cuenta individual, más la comisión de tu AFP. Hoy las comisiones van de {{ (p.comisiones_afp.values()|min)|porcentaje(2) }} a {{ (p.comisiones_afp.values()|max)|porcentaje(2) }}, así que el descuento total va de {{ (p.tasa_afp + p.comisiones_afp.values()|min)|porcentaje(2) }} a {{ (p.tasa_afp + p.comisiones_afp.values()|max)|porcentaje(2) }}."
  - pregunta: "¿Desde qué sueldo se paga impuesto único?"
    respuesta: "Desde que la base tributable (remuneración imponible menos las cotizaciones obligatorias) supera {{ p.tramos_impuesto[0].hasta|numero(1) }} UTM: {{ (p.tramos_impuesto[0].hasta * utm_hoy)|pesos }} en {{ hoy|mes_de_anio }}. Bajo ese monto la tasa es cero."
  - pregunta: "¿La colación y la movilización pagan cotizaciones o impuesto?"
    respuesta: "No, si son de un monto razonable. Son asignaciones que no constituyen remuneración (artículo 41 del Código del Trabajo): no se les descuenta AFP, salud, seguro de cesantía ni impuesto, y se suman completas al líquido."
  - pregunta: "¿Qué pasa si gano más que el tope imponible?"
    respuesta: "La AFP y la salud se calculan solo hasta el tope de {{ p.tope_imponible_uf|numero(1) }} UF al mes (unos {{ (p.tope_imponible_uf * p.uf_topes)|pesos }} en {{ hoy|mes_de_anio }}). Lo que ganes por sobre ese monto no paga esas cotizaciones, pero sí paga impuesto único."
---
{% set barata = calc.afp_mas_barata(p) %}
{% set r = calc.sueldo_liquido(1000000, p, afp=barata) %}
El sueldo líquido es lo que llega a tu cuenta: tu remuneración imponible, más las asignaciones no imponibles (como colación y movilización), menos las cotizaciones de AFP, salud y seguro de cesantía, y menos el impuesto único si corresponde. Por ejemplo, con un sueldo bruto de $1.000.000, contrato indefinido, AFP {{ p.nombres_afp[barata] }} y Fonasa, hoy recibes **{{ r.liquido|pesos }}** líquidos.

## Sueldo bruto, imponible y líquido

En tu liquidación aparecen tres montos distintos:

- **Sueldo bruto:** todo lo que te pagan en el mes, antes de descuentos.
- **Remuneración imponible:** la parte del bruto sobre la que se calculan las cotizaciones. Incluye el sueldo base, las horas extra, las comisiones, la gratificación y, en general, lo que recibes como pago por tu trabajo (artículos 41 y 42 del Código del Trabajo).
- **Haberes no imponibles:** la colación, la movilización, los viáticos y la asignación familiar legal, entre otros. No son remuneración (artículo 41), así que no pagan cotizaciones ni impuesto y se suman completos al líquido. La colación y la movilización deben ser de un monto razonable: según la Dirección del Trabajo, lo que exceda el gasto que compensan se considera remuneración.

La cuenta completa es: **líquido = imponible + no imponible − cotizaciones − impuesto único**. Tu empleador descuenta las cotizaciones y el impuesto, y los paga por ti cada mes.

## Los descuentos, paso a paso

### AFP: {{ p.tasa_afp|porcentaje(0) }} más la comisión

El {{ p.tasa_afp|porcentaje(0) }} de tu remuneración imponible va a tu cuenta de capitalización individual. A eso se suma la comisión de tu AFP, que es distinta en cada administradora y que, por ley, también se cobra como un porcentaje de la remuneración imponible. Estas son las comisiones vigentes, ordenadas de menor a mayor:

| AFP | Comisión | Descuento total |
|---|---:|---:|
{% for clave, comision in p.comisiones_afp|dictsort(by='value') -%}
| {{ p.nombres_afp[clave] }} | {{ comision|porcentaje(2) }} | {{ (p.tasa_afp + comision)|porcentaje(2) }} |
{% endfor %}

Con $1.000.000 imponibles, la diferencia de comisión entre la AFP más barata y la más cara es de {{ ((p.comisiones_afp.values()|max - p.comisiones_afp.values()|min) * 1000000)|pesos }} al mes. Ese dinero no va a tu cuenta: es el cobro de la administradora.

### Salud: {{ p.salud_obligatoria|porcentaje(0) }} para Fonasa o isapre

Se descuenta el {{ p.salud_obligatoria|porcentaje(0) }} de tu remuneración imponible. Si estás en Fonasa, ese es todo el descuento. Si estás en una isapre y tu plan cuesta más que ese {{ p.salud_obligatoria|porcentaje(0) }}, se descuenta el precio del plan: la diferencia es una cotización adicional que también sale de tu sueldo.

{% set ri = calc.sueldo_liquido(1500000, p, afp=barata, salud="isapre", plan_isapre_uf=4) %}
Por ejemplo, con $1.500.000 imponibles el {{ p.salud_obligatoria|porcentaje(0) }} es {{ (1500000 * p.salud_obligatoria)|pesos }}. Si tu plan de isapre cuesta 4 UF (unos {{ (4 * p.uf_topes)|pesos }} en {{ hoy|mes_de_anio }}), te descuentan {{ ri.salud|pesos }}: {{ ri.salud_adicional|pesos }} más que en Fonasa.

### Seguro de cesantía

Las cotizaciones las pagan tú y tu empleador, en proporciones que dependen del tipo de contrato (Ley 19.728):

| Tipo de contrato | Pagas tú | Paga tu empleador |
|---|---:|---:|
| Indefinido | {{ p.cesantia_trabajador.indefinido|porcentaje(1) }} | {{ p.cesantia_empleador.indefinido|porcentaje(1) }} |
| Plazo fijo o por obra | {{ "No pagas" if p.cesantia_trabajador.plazo_fijo == 0 else p.cesantia_trabajador.plazo_fijo|porcentaje(1) }} | {{ p.cesantia_empleador.plazo_fijo|porcentaje(1) }} |
| Indefinido, después de 11 años con el mismo empleador | {{ "No pagas" if p.cesantia_trabajador.indefinido_11 == 0 else p.cesantia_trabajador.indefinido_11|porcentaje(1) }} | {{ p.cesantia_empleador.indefinido_11|porcentaje(1) }} |

Tu cotización y la parte que tu empleador deposita en tu cuenta individual se pagan por un máximo de 11 años en cada relación laboral; después, el empleador sigue pagando solo su aporte al Fondo de Cesantía Solidario, mientras dure el contrato.

Se calcula sobre la remuneración imponible con un tope propio, más alto que el de la AFP: {{ p.tope_cesantia_uf|numero(1) }} UF al mes (unos {{ (p.tope_cesantia_uf * p.uf_topes)|pesos }} en {{ hoy|mes_de_anio }}).

### El tope imponible

La AFP y la salud se calculan sobre un máximo de {{ p.tope_imponible_uf|numero(1) }} UF al mes. Si ganas más, lo que excede ese monto no paga esas cotizaciones, aunque sí paga impuesto. Para pasar el tope a pesos se usa la [UF]({{ ruta('/uf/') }}) del último día del mes al que corresponde la remuneración: en {{ hoy|mes_de_anio }} son unos {{ (p.tope_imponible_uf * p.uf_topes)|pesos }}. La Superintendencia de Pensiones reajusta su valor en UF una vez al año, según la variación del Índice de Remuneraciones Reales; si esa variación es negativa, el tope se mantiene.

## El impuesto único de segunda categoría

El impuesto único no se calcula sobre el bruto, sino sobre la **base tributable**: tu remuneración imponible menos las cotizaciones de AFP, salud (hasta el {{ p.salud_obligatoria|porcentaje(0) }}) y seguro de cesantía. Si ahorras en APV régimen B y tu empleador lo descuenta de tu sueldo, ese ahorro también se descuenta de la base, hasta {{ p.tope_apv_mensual_uf|numero }} UF al mes.

La tabla está en UTM, así que sus montos en pesos cambian cada mes. Con la UTM de {{ hoy|mes_de_anio }} ({{ utm_hoy|pesos }}) queda así:

| Base tributable mensual | Factor | Cantidad a rebajar |
|---|---:|---:|
{% for t in p.tramos_impuesto -%}
| {% if loop.first %}Hasta {{ (t.hasta * utm_hoy)|pesos }}{% elif t.hasta is none %}Más de {{ (loop.previtem.hasta * utm_hoy)|pesos }}{% else %}De {{ (loop.previtem.hasta * utm_hoy)|pesos }} a {{ (t.hasta * utm_hoy)|pesos }}{% endif %} | {{ "Exento" if t.factor == 0 else t.factor|porcentaje(1) }} | {{ "—" if t.rebaja == 0 else (t.rebaja * utm_hoy)|pesos(2) }} |
{% endfor %}

Para calcular el impuesto, ubica tu base tributable en la tabla, multiplícala por el factor del tramo y réstale la cantidad a rebajar.

{% set r2 = calc.sueldo_liquido(2000000, p, afp=barata) %}
{% set tramo = p.tramos_impuesto[r2.tramo] %}
Un ejemplo con $2.000.000 brutos: la AFP ({{ r2.afp|pesos }}), la salud ({{ r2.salud|pesos }}) y el seguro de cesantía ({{ r2.cesantia|pesos }}) dejan una base tributable de {{ r2.base_tributable|pesos }}. {% if r2.impuesto > 0 %}Ese monto cae en el tramo de {{ tramo.factor|porcentaje(1) }}, así que el impuesto es {{ r2.base_tributable|pesos }} × {{ tramo.factor|porcentaje(1) }} − {{ (tramo.rebaja * utm_hoy)|pesos(2) }} = **{{ r2.impuesto|pesos }}**. El factor es tu tasa marginal: la tasa efectiva es bastante menor, {{ (r2.impuesto / r2.base_tributable)|porcentaje(1) }} de la base en este caso.{% else %}Ese monto está dentro del tramo exento, así que no paga impuesto.{% endif %} La tabla completa de cada mes está en la página del [impuesto único]({{ ruta('/impuesto-unico/') }}).

## Gratificación y haberes no imponibles

### Gratificación legal

{% set g = calc.gratificacion_legal(800000, p) %}
Si tu empleador paga la gratificación según el artículo 50 del Código del Trabajo, te corresponde el {{ p.gratificacion_tasa|porcentaje(0) }} de tus remuneraciones, con un tope de {{ p.gratificacion_tope_imm_anual|numero(2) }} ingresos mínimos mensuales al año. Cuando se paga mes a mes, el tope mensual es de {{ (p.gratificacion_tope_imm_anual * p.imm / 12)|pesos }}, con el [ingreso mínimo]({{ ruta('/sueldo-minimo/') }}) actual de {{ p.imm|pesos }}.

La gratificación es remuneración imponible: se suma al sueldo base antes de calcular las cotizaciones y el impuesto. Con un sueldo base de $800.000, la gratificación mensual es de {{ g|pesos }}{% if g < 800000 * p.gratificacion_tasa %} (se aplicó el tope){% endif %} y la remuneración imponible queda en {{ (800000 + g)|pesos }}.

### Colación, movilización y otros haberes no imponibles

{% set rn = calc.sueldo_liquido(1000000, p, afp=barata, no_imponible=80000) %}
Como no son remuneración, estas asignaciones no pagan cotizaciones ni impuesto. Si al sueldo de $1.000.000 del ejemplo inicial le agregas $80.000 de colación y movilización, el líquido sube de {{ r.liquido|pesos }} a {{ rn.liquido|pesos }}: exactamente los $80.000.

## Ejemplos para distintos sueldos

Con contrato indefinido, Fonasa y AFP {{ p.nombres_afp[barata] }} (la de menor comisión), estos son los líquidos de hoy:

| Sueldo bruto | AFP, salud y cesantía | Impuesto único | Sueldo líquido |
|---|---:|---:|---:|
{% for bruto in [600000, 1000000, 1500000, 2500000, 4000000] -%}
{% set e = calc.sueldo_liquido(bruto, p, afp=barata) -%}
| [{{ bruto|pesos }}]({{ ruta('/sueldo-liquido/' ~ bruto ~ '/') }}) | {{ (e.afp + e.salud + e.cesantia)|pesos }} | {{ e.impuesto|pesos }} | {{ e.liquido|pesos }} |
{% endfor %}

{% if calc.sueldo_liquido(4000000, p, afp=barata).tope_aplicado %}Con $4.000.000 ya se aplica el tope imponible: la AFP y la salud se calculan sobre {{ p.tope_imponible_uf|numero(1) }} UF y no sobre el sueldo completo. {% endif %}Revisa el desglose de cada caso, por ejemplo el del [sueldo líquido de $1.000.000 bruto]({{ ruta('/sueldo-liquido/1000000/') }}), o calcula el tuyo en la [calculadora de sueldo líquido]({{ ruta('/calculadoras/sueldo-liquido/') }}), que también hace el cálculo inverso: cuánto bruto pedir para recibir un líquido.

## Lo que paga tu empleador aparte

{% set costo = calc.costo_empleador(1000000, p) %}
Tu empleador paga además cotizaciones que no se descuentan de tu sueldo: su parte del seguro de cesantía, la cotización básica del seguro de accidentes del trabajo junto con la del seguro de la Ley SANNA ({{ p.mutual_basica|porcentaje(2) }} entre ambas) y el aporte de la reforma de pensiones, hoy de {{ p.aporte_empleador_reforma|porcentaje(1) }}{% if p.sis == 0 %}, que incluye el seguro de invalidez y sobrevivencia{% else %}, más el seguro de invalidez y sobrevivencia ({{ p.sis|porcentaje(2) }}){% endif %}. Para un sueldo de $1.000.000 con contrato indefinido suman {{ costo.total_cotizaciones|pesos }} al mes, sin contar la cotización adicional del seguro de accidentes, que depende del riesgo de la empresa.

## Lo que este cálculo no incluye

Tu liquidación real puede ser distinta por bonos, horas extra, licencias médicas, anticipos, préstamos, cuotas sindicales o ahorro voluntario (APV). Si algo no te cuadra, pide a tu empleador el detalle de tu liquidación. Para casos particulares, la Dirección del Trabajo y el Servicio de Impuestos Internos son las fuentes oficiales.
