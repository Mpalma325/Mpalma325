---
titulo: "Jornada de {{ p.jornada_semanal_horas|int }} horas y horas extra en Chile: cómo se calculan"
descripcion: "Calendario de la Ley 40 horas, qué cambia con la reducción de jornada, cuántas horas extra puedes hacer y cómo calcular su valor con la fórmula de la DT."
h1: "Jornada de {{ p.jornada_semanal_horas|int }} horas y horas extra"
resumen: "Calendario de la Ley 40 horas, qué cambia con la reducción de jornada, cuántas horas extra puedes hacer, cómo se calcula su valor y cuándo puedes cambiarlas por días libres."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: trabajo
orden: 40
calculadoras:
  - /calculadoras/horas-extra/
  - /calculadoras/sueldo-liquido/
fuentes:
  - nombre: "Ley 21.561, que reduce la jornada laboral a 40 horas (Biblioteca del Congreso Nacional)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=1191554"
  - nombre: "Código del Trabajo, artículos 22 a 32 (Biblioteca del Congreso Nacional)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=207436"
  - nombre: "Dirección del Trabajo: ¿Cómo se implementa la reducción de la jornada de 45 a 40 horas?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-125909.html"
  - nombre: "Dirección del Trabajo: cálculo de la hora extraordinaria con sueldo mensual"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-95182.html"
faq:
  - pregunta: "¿Desde cuándo rige la jornada de 42 horas?"
    respuesta: "Desde el 26 de abril de 2026, por la Ley 21.561. Entre el 26 de abril de 2024 y esa fecha el máximo era de 44 horas, y el 26 de abril de 2028 pasa a 40 horas semanales."
  - pregunta: "¿Cuántas horas extra se pueden hacer al día?"
    respuesta: "Hasta dos horas extraordinarias por día, solo en faenas que no perjudiquen tu salud y con un pacto escrito que dura hasta tres meses y se puede renovar (artículos 31 y 32 del Código del Trabajo)."
  - pregunta: "¿Cómo se calcula el valor de una hora extra?"
    respuesta: "Divide tu sueldo mensual por 30, multiplícalo por 28 y divide el resultado por 4 veces tu jornada semanal ({{ 4 * p.jornada_semanal_horas|int }} con jornada de {{ p.jornada_semanal_horas|int }} horas). Eso es la hora ordinaria; la hora extra vale al menos 1,5 veces ese monto."
  - pregunta: "¿Me pueden bajar el sueldo por la reducción de jornada?"
    respuesta: "No. La reducción de jornada de la Ley 21.561 no puede significar una rebaja de tu remuneración, y las partes tampoco pueden acordar esa rebaja."
  - pregunta: "¿Puedo cambiar horas extra por días libres?"
    respuesta: "Sí, si lo acuerdas por escrito con tu empleador: cada hora extra se compensa con una hora y media de descanso, con un máximo de cinco días hábiles adicionales de feriado al año, que debes usar dentro de los seis meses siguientes."
---
{% set jornada = p.jornada_semanal_horas|int %}
{% set divisor = 4 * jornada %}
{% set factor = 1.5 * 28 / (30 * divisor) %}
{% if jornada == 42 %}Desde el 26 de abril de 2026, la jornada ordinaria máxima en Chile es de **42 horas semanales**, y el 26 de abril de 2028 bajará a 40.{% else %}Desde el 26 de abril de 2028, la jornada ordinaria máxima en Chile es de **40 horas semanales**.{% endif %} Así lo establece la Ley 21.561, conocida como Ley de 40 horas. Lo que trabajes por sobre tu jornada son horas extra: como máximo dos por día y con un recargo de al menos 50%.

## Calendario de la Ley 40 horas

La Ley 21.561 se publicó el 26 de abril de 2023 y reduce la jornada de forma gradual:

| Desde | Jornada ordinaria máxima |
|---|---|
| Antes del 26 de abril de 2024 | 45 horas semanales |
| 26 de abril de 2024 | 44 horas semanales |
| 26 de abril de 2026 | 42 horas semanales{% if jornada == 42 %} (vigente){% endif %} |
| 26 de abril de 2028 | 40 horas semanales{% if jornada == 40 %} (vigente){% endif %} |

Son plazos máximos: un empleador puede adelantar la reducción. La ley rige para quienes trabajan bajo el Código del Trabajo; no se aplica a funcionarios regidos por el Estatuto Administrativo ni a quienes trabajan a honorarios.

## Qué cambia con la reducción

- **Tu sueldo no baja.** La reducción no puede traducirse en una rebaja de la remuneración, y las partes tampoco pueden acordarla.
- **Cómo se quitan las horas.** Se puede acordar con el empleador o a través del sindicato, al inicio o al término de la jornada diaria. Sin acuerdo, la rebaja se aplica al final de la jornada: con una jornada de cinco días, en el paso de 44 a 42 horas se trabaja una hora menos en dos días distintos de la semana, que define el empleador.
- **Límite diario.** La jornada ordinaria no puede superar 10 horas por día.
- **Jornada en promedio.** Por acuerdo, la jornada semanal puede cumplirse en promedio en ciclos de hasta cuatro semanas. Ninguna semana puede superar 45 horas ordinarias ni estar en ese límite más de dos semanas seguidas, y debe haber un calendario acordado. Si estás sindicalizado, se requiere además el acuerdo del sindicato. Si el contrato termina y trabajaste más horas que el promedio, esas horas se pagan.
- **Bandas horarias.** Madres, padres y quienes tengan el cuidado personal de niños menores de 12 años pueden adelantar o atrasar hasta en una hora el inicio de su jornada, cumpliendo igual el total de horas.

## Horas extra: límites y pacto

Los artículos 30 a 32 del Código del Trabajo fijan las reglas:

- **Qué son:** las horas que exceden la jornada máxima legal o la pactada en tu contrato, si es menor.
- **Máximo:** dos horas extra por día, y solo en faenas que no perjudiquen tu salud.
- **Pacto escrito:** solo se pueden pactar para atender necesidades o situaciones temporales de la empresa, por escrito y con una vigencia de hasta tres meses, renovable.
- **Sin pacto igual se pagan:** si trabajas más allá de tu jornada con conocimiento del empleador, esas horas son extraordinarias aunque no haya pacto escrito.
- **Recargo:** al menos 50% sobre el sueldo convenido para tu jornada ordinaria. Si no hay sueldo convenido o es menor que el ingreso mínimo ({{ p.imm|pesos }}), el recargo se calcula sobre el ingreso mínimo. Se pagan junto con las remuneraciones del mismo período, y las partes pueden pactar un recargo mayor.
- **No son horas extra** las que trabajas para compensar un permiso, si lo pediste por escrito y el empleador lo autorizó.

## Cómo calcular el valor de la hora extra

La Dirección del Trabajo calcula el valor de la hora para quien tiene sueldo mensual en tres pasos:

1. Divide el sueldo mensual por 30 y multiplícalo por 28: es lo que ganas en cuatro semanas.
2. Divide ese monto por las horas de cuatro semanas, es decir, 4 veces tu jornada semanal. Con {{ jornada }} horas, el divisor es {{ divisor }}. El resultado es el valor de la hora ordinaria.
3. Multiplica la hora ordinaria por 1,5 para obtener la hora extra con el recargo de 50%.

El ejemplo de la propia Dirección del Trabajo, con jornada de 42 horas: $800.000 ÷ 30 × 28 ÷ 168 = $4.444,4 por hora ordinaria, y con el recargo la hora extra vale unos $6.667.

Los tres pasos se resumen en un solo multiplicador por jornada:

| Jornada semanal | Divisor | Multiplica tu sueldo por | Hora extra con el ingreso mínimo |
|---|---:|---:|---:|
{%- for h in [45, 44, 42, 40] %}
| {{ h }} horas{% if h == jornada %} (vigente){% endif %} | {{ 4 * h }} | {{ (1.5 * 28 / (120 * h))|numero(7) }} | {{ (p.imm * 1.5 * 28 / (120 * h))|pesos }} |
{%- endfor %}

Con el mismo sueldo y menos horas, cada hora vale más: por eso el valor de la hora extra sube con cada etapa de la reducción de jornada.

**Ejemplo.** Si tu sueldo base es de {{ 1000000|pesos }} y este mes hiciste 10 horas extra con jornada de {{ jornada }} horas: {{ 1000000|pesos }} × {{ factor|numero(7) }} × 10 = **{{ (1000000 * factor * 10)|pesos }}** brutos. Las horas extra son remuneración, así que pagan cotizaciones e impuesto; puedes ver cuánto suben tu líquido en la [calculadora de sueldo líquido]({{ ruta('/calculadoras/sueldo-liquido/') }}).

## Cambiar horas extra por días libres

La Ley 21.561 permite acordar por escrito que las horas extra se compensen con días adicionales de feriado en vez de pagarse:

- Por cada hora extra corresponde una hora y media de descanso.
- Se pueden sumar hasta cinco días hábiles adicionales al año.
- Debes usarlos dentro de los seis meses siguientes, avisando al empleador con 48 horas de anticipación, y puedes juntarlos con tus vacaciones.
- Si el contrato termina antes de que los uses, se pagan como el feriado pendiente.

Por ejemplo, 10 horas extra compensadas equivalen a 15 horas de descanso. Revisa el resto de las reglas del feriado en la [guía de vacaciones]({{ ruta('/guias/vacaciones-en-chile/') }}).

## Si no te pagan las horas extra

Revisa en tu liquidación de sueldo cuántas horas extra te pagaron y a qué valor. Si no coinciden con las que trabajaste, primero pídele al empleador el registro de asistencia; si no se resuelve, puedes consultar o denunciar en la Inspección del Trabajo. En la guía sobre [cómo leer tu liquidación de sueldo]({{ ruta('/guias/como-leer-tu-liquidacion-de-sueldo/') }}) verás dónde aparecen.
