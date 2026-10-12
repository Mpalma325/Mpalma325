---
titulo: "Vacaciones en Chile {{ hoy.year }}: días, feriado progresivo y proporcional"
descripcion: "Cuántos días de vacaciones te corresponden, cuándo tienes feriado progresivo, cómo fraccionar o acumular días y cómo se pagan las vacaciones proporcionales."
h1: "Vacaciones en Chile: cuántos días te corresponden"
resumen: "Feriado legal de {{ p.feriado_anual_habiles|numero }} días hábiles, días extra por feriado progresivo y en zonas extremas, reglas para fraccionar y acumular, y cómo se calculan las vacaciones proporcionales."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: trabajo
orden: 30
calculadoras:
  - /calculadoras/vacaciones-proporcionales/
  - /calculadoras/dias-habiles/
fuentes:
  - nombre: "Código del Trabajo, artículos 67 a 73 (Biblioteca del Congreso Nacional)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=207436"
  - nombre: "Dirección del Trabajo: ¿Cómo se calcula el feriado proporcional?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60200.html"
  - nombre: "Dirección del Trabajo: ¿En qué consiste el derecho al feriado progresivo?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60194.html"
  - nombre: "Dirección del Trabajo: feriado anual en Magallanes, Aysén y la Provincia de Palena"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-98885.html"
  - nombre: "Dirección del Trabajo: ¿Cómo se acreditan los años trabajados para el feriado progresivo?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60195.html"
  - nombre: "Dirección del Trabajo, Ord. N° 4350: compensación en dinero del feriado progresivo"
    url: "https://dt.gob.cl/legislacion/1624/w3-article-117579.html"
  - nombre: "Dirección del Trabajo, Ord. N° 2813: el feriado básico no se compensa en dinero"
    url: "https://www.dt.gob.cl/legislacion/1624/w3-article-103667.html"
  - nombre: "Dirección del Trabajo: ¿Puede el empleador disponer el fraccionamiento del feriado?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60180.html"
  - nombre: "Dirección del Trabajo: compensar horas extraordinarias con días adicionales de feriado"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-125917.html"
  - nombre: "Dirección del Trabajo, Ord. N° 199/5: los días compensados se usan en días completos"
    url: "https://www.dt.gob.cl/legislacion/1624/w3-article-125738.html"
  - nombre: "Dirección del Trabajo, Ord. N° 81/2: días compensados que no se usan"
    url: "https://www.dt.gob.cl/legislacion/1624/w3-article-125559.html"
faq:
  - pregunta: "¿Cuántos días de vacaciones me corresponden al año?"
    respuesta: "{{ p.feriado_anual_habiles|numero }} días hábiles con remuneración íntegra si llevas más de un año en la empresa, o 20 si trabajas en Magallanes, Aysén o la Provincia de Palena. Para las vacaciones el sábado nunca es día hábil, así que se cuentan de lunes a viernes, sin feriados."
  - pregunta: "¿Desde cuántos años tengo vacaciones progresivas?"
    respuesta: "Desde que sumas 13 años de trabajo: los primeros 10, con uno o más empleadores, y 3 años nuevos. Después ganas un día más por cada 3 años adicionales. De empleadores anteriores solo se cuentan hasta 10 años."
  - pregunta: "¿Puedo cambiar mis vacaciones por plata?"
    respuesta: "El feriado básico no, mientras sigas trabajando: no se puede compensar en dinero (artículo 73 del Código del Trabajo). Los días de feriado progresivo sí se pueden compensar en dinero si lo acuerdas con tu empleador, según la Dirección del Trabajo. Al terminar el contrato, el feriado pendiente y el proporcional se pagan en el finiquito."
  - pregunta: "¿Puedo acumular vacaciones de un año para otro?"
    respuesta: "Sí, si lo acuerdas con tu empleador, y hasta por dos períodos consecutivos. Antes de que cumplas el año que te daría un tercer período, el empleador debe darte al menos el primero de los acumulados."
  - pregunta: "¿Me pueden obligar a tomar las vacaciones en partes?"
    respuesta: "No. El feriado debe ser continuo y solo los días que exceden de 10 días hábiles se pueden fraccionar, siempre de común acuerdo. El empleador no puede dividirlo por su cuenta."
---
{% set dias = p.feriado_anual_habiles %}
{% set por_mes = dias / 12 %}
{% set inicio = hoy.replace(year=2025, month=3, day=1) %}
{% set termino = hoy.replace(year=2026, month=9, day=15) %}
{% set feriados = [hoy.replace(year=2026, month=9, day=18), hoy.replace(year=2026, month=9, day=19)] %}
{% set sueldo = 900000 %}
{% set prop = calc.feriado_proporcional(inicio, termino, p) %}
{% set conv = calc.dias_corridos_de_feriado(prop.dias_habiles, termino, feriados) %}
{% set pago = calc.finiquito(inicio, termino, sueldo, 'renuncia', p, feriados) %}
Si llevas más de un año en tu trabajo, cada año tienes derecho a {{ dias|numero }} días hábiles de vacaciones pagadas, lo que la ley llama feriado anual; son 20 si trabajas en Magallanes, Aysén o la Provincia de Palena. Con muchos años de trabajo se suman días por feriado progresivo, y si el contrato termina te pagan los días que no alcanzaste a usar.

## Cuántos días te corresponden

El artículo 67 del Código del Trabajo da a quienes tienen **más de un año de servicio** un feriado de **{{ dias|numero }} días hábiles con remuneración íntegra**. Tres reglas determinan cuánto duran en la práctica:

- **El sábado nunca es hábil para el feriado** (artículo 69), aunque trabajes los sábados. Tampoco cuentan los domingos ni los feriados. Sin feriados de por medio, {{ dias|numero }} días hábiles equivalen a {{ (dias / 5)|numero }} semanas de lunes a viernes.
- **Zonas extremas:** si trabajas en la Región de Magallanes y de la Antártica Chilena, en la Región de Aysén o en la Provincia de Palena, el feriado básico es de **20 días hábiles**.
- **Remuneración íntegra** (artículo 71): si tienes sueldo fijo, se te paga el sueldo; si tu remuneración es variable, el promedio de lo ganado en los últimos tres meses trabajados; si es mixta, el sueldo más ese promedio de las partes variables.

La ley pide que el feriado se otorgue de preferencia en primavera o verano, considerando las necesidades del servicio (artículo 67).

## Feriado progresivo

El artículo 68 agrega **un día hábil por cada tres nuevos años trabajados**, una vez que cumples **10 años de trabajo** para uno o más empleadores, continuos o no. Solo puedes hacer valer **hasta 10 años con empleadores anteriores**: los años que den derecho a días adicionales deben sumarse con tu empleador actual. La ley agrega que estos días adicionales son susceptibles de negociación individual o colectiva.

| Años de trabajo | Días hábiles de feriado | En Magallanes, Aysén y Palena |
|---|---:|---:|
| Menos de 13 | {{ dias|numero }} | 20 |
{%- for desde in [13, 16, 19, 22, 25] %}
| {{ desde }} a {{ desde + 2 }} | {{ (dias + loop.index)|numero }} | {{ 20 + loop.index }} |
{%- endfor %}

Dos ejemplos:

- **Pedro** trabajó 8 años en otra empresa y lleva 5 en la actual: suma 13 años, así que este año tiene {{ (dias + 1)|numero }} días hábiles.
- **Ana** trabajó 15 años en otras empresas y lleva 2 en la actual: de los anteriores solo se cuentan 10, suma 12 y todavía no tiene días progresivos. El primero lo gana al cumplir 3 años con su empleador actual.

Para que te los reconozcan, debes acreditar los años con empleadores anteriores, por ejemplo con el certificado de cotizaciones de tu AFP, una certificación de la Inspección del Trabajo u otro instrumento público. Según la Dirección del Trabajo, tienes que hacerlo antes de usar el feriado de ese año; si no, pierdes el día adicional de ese período y no puedes sumarlo a los siguientes.

## Fraccionar, acumular y cambiar por dinero

- **Fraccionar:** el feriado debe ser continuo. Solo la parte que excede de 10 días hábiles se puede dividir, y siempre de común acuerdo: el empleador no puede fraccionarlo por su cuenta (artículo 70).
- **Acumular:** con acuerdo de ambos, puedes acumular hasta dos períodos consecutivos. Si tienes dos acumulados, el empleador debe darte al menos el primero antes de que completes el año que te daría un tercero (artículo 70).
- **Cambiar por dinero:** el feriado básico no se puede compensar en dinero mientras sigas trabajando (artículo 73). La excepción son los días de feriado progresivo: según la Dirección del Trabajo, puedes acordar con tu empleador que te los pague en dinero. Todo lo demás solo se paga en dinero cuando el contrato termina.

## Días adicionales por horas extra

Desde la Ley 21.561 (Ley de 40 horas), puedes acordar por escrito con tu empleador que tus horas extra se compensen con días adicionales de feriado, en vez de pagarse:

- Cada hora extra equivale a una hora y media de descanso.
- El máximo es de **cinco días hábiles adicionales al año**.
- Debes usarlos dentro de los seis meses siguientes al ciclo o período en que hiciste las horas extra, avisando con 48 horas de anticipación. Según la Dirección del Trabajo, se usan en días completos, no en medios días ni en horas, y si coinciden con tus vacaciones puedes sumarlos a ellas.
- Si no los usas dentro de ese plazo, la Dirección del Trabajo indica que el empleador debe pagarlos con la remuneración del séptimo mes contado desde el ciclo en que se generaron.
- Si el contrato termina antes de que los uses, se pagan como el feriado pendiente.

Más detalles en la guía de [jornada laboral y horas extra]({{ ruta('/guias/jornada-laboral-42-horas-y-horas-extra/') }}).

## Vacaciones proporcionales al terminar el contrato

Si tu contrato termina, el empleador debe pagarte los días de feriado pendientes y los **proporcionales**: los que ganaste desde que entraste o desde tu último aniversario en la empresa (artículo 73). La Dirección del Trabajo los calcula así:

1. Divide tus días de feriado anual por 12; según la Dirección del Trabajo, se incluyen los días de feriado progresivo, si te corresponden. Con {{ dias|numero }} días son {{ por_mes|numero(2) }} días hábiles por mes.
2. Multiplica ese resultado por los meses trabajados desde el último aniversario y suma la fracción del mes: {{ por_mes|numero(2) }} ÷ 30 por cada día.
3. Cuenta esos días hábiles desde el día siguiente al término del contrato e incluye los sábados, domingos y feriados que caigan entre medio. El resultado son los días corridos que se pagan.
4. Multiplica los días corridos por el valor diario de tu remuneración.

**Ejemplo.** Daniela entró a trabajar el {{ inicio|fecha_larga }}, renunció con término el {{ termino|fecha_larga }} y ganaba {{ sueldo|pesos }} al mes. No tenía días pendientes.

| Paso | Resultado |
|---|---|
| Tiempo desde su último aniversario ({{ prop.desde|fecha_larga }}) | {{ prop.meses }} meses y {{ prop.dias }} días |
| Días hábiles ganados | {{ prop.meses }} × {{ por_mes|numero(2) }} + {{ prop.dias }} × {{ por_mes|numero(2) }} ÷ 30 = {{ prop.dias_habiles|numero(3) }} |
| Días corridos a pagar | {{ conv.dias_corridos|numero(3) }} |
| Valor diario | {{ sueldo|pesos }} ÷ 30 = {{ (sueldo / 30)|pesos }} |
| **Monto a pagar** | **{{ pago.feriado|pesos }}** |

Contados desde el día siguiente al término, los {{ prop.dias_habiles|int }} días hábiles completos llegan hasta el {{ conv.hasta|fecha_larga }}. En medio quedan el feriado del 18 de septiembre, dos sábados y dos domingos: {{ conv.inhabiles }} días que se suman, más la fracción de {{ (prop.dias_habiles - prop.dias_habiles|int)|numero(3) }} días. Por eso se pagan {{ conv.dias_corridos|numero(3) }} días corridos y no {{ prop.dias_habiles|numero(3) }}.

Para hacer tu propio cálculo con los feriados reales de cada año, usa la [calculadora de vacaciones proporcionales]({{ ruta('/calculadoras/vacaciones-proporcionales/') }}). Si además te corresponde indemnización, revisa la guía sobre [cómo se calcula el finiquito]({{ ruta('/guias/como-calcular-el-finiquito/') }}).

## Si algo no calza

Si tu empleador no te da vacaciones, te las fracciona sin acuerdo o no te paga el feriado al terminar el contrato, puedes consultar o reclamar en la Inspección del Trabajo. Los contratos y convenios colectivos pueden darte más días que la ley, pero nunca menos.
