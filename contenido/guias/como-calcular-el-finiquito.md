---
titulo: "Finiquito en Chile {{ hoy.year }}: cómo se calcula y qué te corresponde"
descripcion: "Qué incluye el finiquito según la causal de término y cómo se calculan los años de servicio, el aviso previo y las vacaciones, con un ejemplo y los plazos legales."
h1: "Cómo se calcula el finiquito"
resumen: "Indemnización por años de servicio, aviso previo y vacaciones: qué te corresponde según la causal de término, cómo se calcula cada monto, el plazo de pago y cómo se firma."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: trabajo
orden: 10
calculadoras:
  - /calculadoras/finiquito/
  - /calculadoras/vacaciones-proporcionales/
fuentes:
  - nombre: "Código del Trabajo, artículos 159 a 177 (Biblioteca del Congreso Nacional)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=207436"
  - nombre: "Dirección del Trabajo: ¿Cuáles son las causales legales de terminación de contrato?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60570.html"
  - nombre: "Dirección del Trabajo: límite de la remuneración para la indemnización por años de servicio"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60604.html"
  - nombre: "Dirección del Trabajo, Ord. N° 5717: el tope de 90 UF rige también para el aviso previo"
    url: "https://www.dt.gob.cl/legislacion/1624/w3-article-108022.html"
  - nombre: "Dirección del Trabajo: indemnización sin tope de años (contratos anteriores al 14 de agosto de 1981)"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60600.html"
  - nombre: "Dirección del Trabajo, Ord. N° 3747/137: el tope de 90 UF rige también para esos contratos"
    url: "https://www.dt.gob.cl/legislacion/1624/w3-article-68684.html"
  - nombre: "Dirección del Trabajo: ¿Cómo se calcula el feriado proporcional?"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60200.html"
  - nombre: "Dirección del Trabajo: aviso de despido por necesidades de la empresa"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60533.html"
  - nombre: "Dirección del Trabajo: descuento del aporte al seguro de cesantía en la indemnización por años de servicio"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-95307.html"
  - nombre: "Dirección del Trabajo: descuento del aporte al seguro de cesantía en la indemnización por obra o faena"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-128656.html"
  - nombre: "Dirección del Trabajo: indemnización por término de obra o faena (Ley 21.122)"
    url: "https://dt.gob.cl/legislacion/1624/w3-article-119662.html"
  - nombre: "Dirección del Trabajo: ratificación de un finiquito de trabajo"
    url: "https://www.dt.gob.cl/portal/1626/w3-article-117245.html"
  - nombre: "Dirección del Trabajo: plazo para pagar el finiquito electrónico aceptado"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-120399.html"
  - nombre: "Dirección del Trabajo: pago de la indemnización en cuotas"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60584.html"
  - nombre: "Dirección del Trabajo: plazo para demandar por despido injustificado"
    url: "https://www.dt.gob.cl/portal/1628/w3-article-60507.html"
  - nombre: "Dirección del Trabajo, Ord. N° 2653: recargos del artículo 168"
    url: "https://www.dt.gob.cl/legislacion/1624/w3-article-103617.html"
faq:
  - pregunta: "¿Cuánto me pagan de finiquito si renuncio?"
    respuesta: "Si renuncias no te corresponde indemnización por años de servicio, salvo que tu contrato la pacte. Sí te deben pagar las vacaciones pendientes y proporcionales, los días trabajados que aún no te pagan y cualquier otra remuneración adeudada."
  - pregunta: "¿Cuánto es la indemnización por años de servicio?"
    respuesta: "Una remuneración mensual (30 días) por cada año trabajado y fracción superior a seis meses, con un máximo de {{ p.tope_anios_indemnizacion }} años y una remuneración tope de {{ p.tope_indemnizacion_uf|numero }} UF (unos {{ (p.tope_indemnizacion_uf * p.uf_indemnizaciones)|pesos }} si el pago se hace en {{ hoy|mes_de_anio }}). Corresponde si te despiden por necesidades de la empresa o desahucio y llevas al menos un año."
  - pregunta: "¿Cuál es el plazo para pagar el finiquito?"
    respuesta: "El empleador debe otorgar el finiquito y poner el pago a tu disposición dentro de 10 días hábiles contados desde la separación del trabajador (artículo 177 del Código del Trabajo). Solo puede pagar las indemnizaciones en cuotas si ambos lo acuerdan y ese pacto se ratifica ante la Inspección del Trabajo."
  - pregunta: "¿Qué hago si no estoy de acuerdo con el finiquito?"
    respuesta: "No lo firmes, o fírmalo con reserva de derechos, y consulta en la Inspección del Trabajo. Si crees que el despido fue injustificado, tienes 60 días hábiles desde la separación para demandar; si reclamas antes en la Inspección, el plazo se suspende, pero nunca puede pasar de 90 días hábiles."
  - pregunta: "¿Me pueden descontar el seguro de cesantía del finiquito?"
    respuesta: "Sí, en dos casos: si te despiden por necesidades de la empresa o desahucio, y si tu contrato por obra o faena termina porque concluyó la obra. El empleador puede descontar de la indemnización lo que él aportó a tu cuenta individual del seguro de cesantía, más su rentabilidad. Nunca puede descontar tus propios aportes, y no procede si renunciaste."
---
{% set inicio = hoy.replace(year=2020, month=3, day=2) %}
{% set termino = hoy.replace(year=2026, month=9, day=30) %}
{% set feriados = [hoy.replace(year=2026, month=10, day=12)] %}
{% set sueldo = 1200000 %}
{% set ej = calc.finiquito(inicio, termino, sueldo, 'necesidades_empresa', p, feriados, aviso_dado=False) %}
{% set conversion = calc.dias_corridos_de_feriado(ej.feriado_habiles, termino, feriados) %}
{% set tope = p.tope_indemnizacion_uf * p.uf_indemnizaciones %}
El finiquito es el documento que cierra la relación laboral y detalla lo que el empleador te paga al salir. Siempre incluye los días trabajados que no te han pagado y las vacaciones pendientes y proporcionales. La indemnización por años de servicio y la del aviso previo dependen de la causal de término: corresponden cuando te despiden por necesidades de la empresa o por desahucio. Los contratos por obra o faena tienen una indemnización propia.

## Qué te corresponde según la causal

Las causales de término están, principalmente, en tres artículos del Código del Trabajo:

- **Artículo 159** (causas objetivas): mutuo acuerdo, renuncia (con aviso de al menos 30 días, salvo que el empleador acepte un plazo menor), muerte del trabajador, vencimiento del plazo convenido, conclusión del trabajo o servicio que dio origen al contrato y caso fortuito o fuerza mayor.
- **Artículo 160** (conducta del trabajador): falta de probidad, acoso sexual o laboral, injurias, ausencias injustificadas, abandono del trabajo, actos que afecten la seguridad e incumplimiento grave del contrato, entre otras. El contrato termina sin derecho a indemnización.
- **Artículo 161** (decisión del empleador): necesidades de la empresa, como racionalización, modernización, bajas en la productividad o cambios en el mercado, y el desahucio escrito, que solo se aplica a gerentes y otros representantes con facultades generales de administración, a cargos de exclusiva confianza y a trabajadores de casa particular (que tienen un sistema propio de indemnización).

| Causal | Años de servicio | Aviso previo | Vacaciones |
|---|---|---|---|
| Necesidades de la empresa o desahucio (art. 161) | Sí, con un año o más | Sí, si no te avisaron con 30 días | Sí |
| Renuncia o mutuo acuerdo (art. 159) | No, salvo pacto | No | Sí |
| Vencimiento del plazo (art. 159 N° 4) | No | No | Sí |
| Término de la obra o faena (art. 159 N° 5) | 2,5 días por mes trabajado (Ley 21.122) | No | Sí |
| Despido disciplinario (art. 160) | No, salvo que un juez lo declare injustificado | No, salvo que un juez lo declare injustificado | Sí |

Los contratos **por obra o faena** tienen una regla propia: si terminan porque la obra concluyó y duraron al menos un mes, el empleador debe pagar **2,5 días de remuneración por cada mes trabajado y fracción superior a 15 días**, con el mismo tope de {{ p.tope_indemnizacion_uf|numero }} UF (artículo 163, agregado por la Ley 21.122).

## Indemnización por años de servicio

Si el empleador te despide por el artículo 161 y el contrato estuvo vigente un año o más, debe pagarte la indemnización pactada en tu contrato o, si no hay pacto (o es menor), la legal del artículo 163: **30 días de tu última remuneración mensual por cada año de servicio y fracción superior a seis meses**, con un máximo de 330 días, es decir, {{ p.tope_anios_indemnizacion }} años. Ese límite de años no se aplica a quienes fueron contratados antes del 14 de agosto de 1981 y tenían su contrato vigente el 1 de diciembre de 1990.

| Tiempo trabajado | Años que se pagan |
|---|---|
| 11 meses | 0: no alcanza el año |
| 1 año y 5 meses | 1 |
| 1 año y 7 meses | 2 |
| 3 años y 6 meses exactos | 3: la fracción debe superar los seis meses |
| 14 años | {{ p.tope_anios_indemnizacion }}: se aplica el tope |

La base de cálculo es la última remuneración mensual (artículo 172). Incluye las cotizaciones de cargo del trabajador y las regalías en especie, y deja fuera la asignación familiar, las horas extra y los beneficios que se pagan de forma esporádica o una vez al año, como las gratificaciones anuales o los aguinaldos. Si tu remuneración es variable, se usa el promedio de los últimos tres meses calendario.

Esa remuneración tiene un **tope de {{ p.tope_indemnizacion_uf|numero }} UF**, según el valor de la UF del último día del mes anterior al pago. Si el pago se hace en {{ hoy|mes_de_anio }}, se usa la UF del último día del mes anterior ({{ p.uf_indemnizaciones|pesos(2) }}) y el tope equivale a {{ tope|pesos }}. Según la Dirección del Trabajo, este tope rige también para quienes fueron contratados antes del 14 de agosto de 1981.

## Aviso previo

Para despedir por necesidades de la empresa o desahucio, el empleador debe avisarte por escrito, con copia a la Inspección del Trabajo, con al menos 30 días de anticipación. Si no lo hace, debe pagarte la **indemnización sustitutiva del aviso previo**: una última remuneración mensual, con el mismo tope de {{ p.tope_indemnizacion_uf|numero }} UF (así lo confirmó la Dirección del Trabajo en su Ord. N° 5717).

## Vacaciones pendientes y proporcionales

Al terminar el contrato se pagan las vacaciones que no alcanzaste a usar, cualquiera sea la causal (artículo 73):

- **Pendientes:** los días de feriado de años completos que no tomaste.
- **Proporcionales:** las que ganaste desde tu último aniversario en la empresa: {{ (p.feriado_anual_habiles / 12)|numero(2) }} días hábiles por mes con el feriado básico de {{ p.feriado_anual_habiles|numero }} días al año (más si tienes feriado progresivo) y la parte proporcional por cada día adicional.

Estos días hábiles se pagan como **días corridos**: se cuentan desde el día siguiente al término del contrato y se suman los sábados, domingos y feriados que caen entre medio. Cada día vale tu remuneración diaria: con sueldo fijo, el sueldo mensual dividido por 30; con remuneración variable, se usa el promedio de los últimos tres meses trabajados. Lo explicamos con detalle en la [guía de vacaciones]({{ ruta('/guias/vacaciones-en-chile/') }}).

## Ejemplo: despido por necesidades de la empresa

Camila entró a trabajar el {{ inicio|fecha_larga }} y la despidieron por necesidades de la empresa, sin aviso previo, con término el {{ termino|fecha_larga }}. Su última remuneración mensual era de {{ sueldo|pesos }}.

| Concepto | Cálculo | Monto |
|---|---|---:|
| Años de servicio | {{ ej.anios_indemnizacion }} años × {{ sueldo|pesos }} | {{ ej.indemnizacion_anios|pesos }} |
| Aviso previo | Una remuneración mensual | {{ ej.aviso_previo|pesos }} |
| Vacaciones proporcionales | {{ ej.feriado_corridos|numero(2) }} días corridos × {{ (sueldo / 30)|pesos }} | {{ ej.feriado|pesos }} |
| **Total bruto** | | **{{ ej.total|pesos }}** |

Camila trabajó {{ ej.tiempo.anios }} años, {{ ej.tiempo.meses }} meses y {{ ej.tiempo.dias }} días. Los {{ ej.tiempo.meses }} meses y {{ ej.tiempo.dias }} días son una fracción superior a seis meses, así que se pagan {{ ej.anios_indemnizacion }} años. Desde su último aniversario ganó {{ ej.feriado_habiles|numero(2) }} días hábiles de vacaciones; contados desde el día siguiente al término, llegan hasta el {{ conversion.hasta|fecha_larga }}, porque en medio hay dos fines de semana y el feriado del 12 de octubre: {{ ej.feriado_inhabiles }} días que se suman.

Con los mismos datos, el total cambia según la causal:

| Causal | Total bruto |
|---|---:|
| Necesidades de la empresa, sin aviso previo | {{ ej.total|pesos }} |
| Necesidades de la empresa, con 30 días de aviso | {{ calc.finiquito(inicio, termino, sueldo, 'necesidades_empresa', p, feriados, aviso_dado=True).total|pesos }} |
| Renuncia, mutuo acuerdo o despido por el artículo 160 | {{ calc.finiquito(inicio, termino, sueldo, 'renuncia', p, feriados).total|pesos }} |

{% set alto = calc.finiquito(inicio, termino, 5000000, 'necesidades_empresa', p, feriados, aviso_dado=False) %}
Si Camila ganara {{ 5000000|pesos }} y el pago se hiciera en {{ hoy|mes_de_anio }}, la indemnización por años de servicio no sería {{ ej.anios_indemnizacion }} × {{ 5000000|pesos }}, sino {{ ej.anios_indemnizacion }} veces el tope de {{ p.tope_indemnizacion_uf|numero }} UF (unos {{ tope|pesos }}): {{ alto.indemnizacion_anios|pesos }}. El aviso previo también quedaría en el tope: {{ alto.aviso_previo|pesos }}. Las vacaciones, en cambio, se pagan sobre la remuneración completa.

Son montos brutos y referenciales. Para tu caso, usa la [calculadora de finiquito]({{ ruta('/calculadoras/finiquito/') }}), que considera los feriados reales de Chile.

## Seguro de cesantía: el descuento permitido

Si el despido es por necesidades de la empresa o desahucio, el empleador puede descontar de la indemnización por años de servicio lo que él cotizó en tu cuenta individual del seguro de cesantía, más su rentabilidad (artículo 13 de la Ley 19.728). Según la Dirección del Trabajo, puede hacer lo mismo con la indemnización de un contrato por obra o faena que termina porque concluyó la obra. En ambos casos, no puede descontar lo que aportaste tú, y el descuento no procede si renunciaste. Por eso, en el finiquito puede aparecer una línea de descuento por este concepto.

## Plazo, firma y pago

- **Plazo:** el empleador tiene 10 días hábiles desde la separación para otorgar el finiquito y poner el pago a tu disposición (artículo 177). Solo puede pagar las indemnizaciones en cuotas si lo acuerdan y ese pacto se ratifica ante la Inspección del Trabajo. Las cuotas deben incluir intereses y reajustes, y si se atrasa una, puedes exigir de inmediato el pago de las que faltan.
- **Firma en papel:** el finiquito se ratifica ante un ministro de fe: un inspector del trabajo, un notario, un oficial del Registro Civil o el secretario municipal.
- **Finiquito electrónico:** el empleador puede proponerlo en el portal Mi DT de la Dirección del Trabajo. Tú lo revisas y lo aceptas, con o sin reserva de derechos, o lo rechazas. Si lo aceptas, el empleador tiene 5 días hábiles (de lunes a sábado) para pagar; si no paga, se emite un acta que sirve como título ejecutivo para cobrar ante los tribunales. Si no quieres usar esta vía, el finiquito se puede ratificar en papel ante un ministro de fe.

Antes de firmar, revisa cada monto. Si no estás de acuerdo con algo, deja una reserva de derechos para poder reclamarlo después.

## Despido injustificado: recargos del artículo 168

Si crees que la causal no corresponde, puedes demandar ante el juzgado del trabajo dentro de 60 días hábiles (de lunes a sábado, sin feriados) desde la separación. Si antes reclamas en la Inspección del Trabajo, el plazo se suspende mientras dura ese trámite, pero en ningún caso puedes demandar después de 90 días hábiles. Si el juez te da la razón, ordena pagar la indemnización sustitutiva del aviso previo y la indemnización por años de servicio, esta última con un recargo:

| Situación | Recargo sobre los años de servicio |
|---|---:|
| Necesidades de la empresa aplicada en forma improcedente | 30% |
| Causal del artículo 159 injustificada, o sin causal | 50% |
| Causal del artículo 160 aplicada indebidamente | 80% |
| Causales 1, 5 o 6 del artículo 160 sin motivo plausible | 100% |

Cada caso es distinto: esta guía no reemplaza la asesoría de la Dirección del Trabajo o de un abogado.
