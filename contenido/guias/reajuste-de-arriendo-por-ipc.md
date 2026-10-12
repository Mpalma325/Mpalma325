---
titulo: "Reajuste de arriendo por IPC: cómo calcularlo ({{ hoy.year }})"
descripcion: "Cómo se reajusta un arriendo según el IPC: qué dice la ley, cláusulas semestrales y anuales, qué meses usar y cómo componer las variaciones, con ejemplos."
h1: "Cómo se reajusta un arriendo por IPC"
resumen: "Qué meses del IPC usar, por qué las variaciones mensuales se multiplican y no se suman, cuándo publica el INE y en qué se diferencia un arriendo en pesos de uno en UF."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: vivienda
orden: 10
calculadoras:
  - /calculadoras/reajuste-arriendo-ipc/
  - /ipc/
fuentes:
  - nombre: "Ley de arriendo (Ley 18.101), guía Ley Fácil de la Biblioteca del Congreso Nacional"
    url: "https://www.bcn.cl/portal/leyfacil/recurso/ley-de-arriendo"
  - nombre: "Preguntas frecuentes del IPC base 2023=100 (INE)"
    url: "https://www.ine.gob.cl/docs/default-source/%C3%ADndice-de-precios-al-consumidor/metodologias/base-anual-2023-100/2---preguntas-frecuentes-ipc-2023.pdf"
  - nombre: "Cálculo de variaciones en la Calculadora IPC (INE)"
    url: "https://www.ine.gob.cl/docs/default-source/%C3%ADndice-de-precios-al-consumidor/metodologias/base-anual-2023-100/5---uso-calculadora-ipc.pdf"
  - nombre: "Metodología de cálculo de la Unidad de Fomento (Banco Central de Chile)"
    url: "https://si3.bcentral.cl/estadisticas/Principal1/Metodologias/EMF/UF.pdf"
faq:
  - pregunta: "¿Cada cuánto se puede reajustar el arriendo?"
    respuesta: "Cuando lo diga el contrato: la ley de arriendo no fija una periodicidad ni un índice. Lo habitual es reajustar cada 6 o cada 12 meses según la variación del IPC. Si el contrato no tiene cláusula de reajuste, la renta no se reajusta sola."
  - pregunta: "¿Qué meses del IPC se usan para reajustar el arriendo?"
    respuesta: "Los que indique el contrato. Si dice «los últimos seis meses», usa los seis últimos meses con IPC ya publicado a la fecha del reajuste. El INE publica el IPC de cada mes el día 8 del mes siguiente, a las 08:00 (o el día hábil anterior si el 8 no es hábil)."
  - pregunta: "¿Se suman las variaciones mensuales del IPC?"
    respuesta: "No. Se multiplican los factores (1 + variación) de cada mes y al resultado se le resta 1. Si todas las variaciones son positivas, sumarlas da un reajuste algo menor que el correcto, y la diferencia crece con el número de meses."
  - pregunta: "¿Me pueden subir el arriendo más que el IPC?"
    respuesta: "Mientras el contrato esté vigente, rige el reajuste pactado. En un contrato mes a mes o indefinido, el arrendador puede ponerle término con un desahucio judicial o notificado por notario, con un aviso de dos meses más uno por cada año completo que hayas vivido ahí (máximo seis meses). Una renta distinta requiere un nuevo acuerdo."
  - pregunta: "¿Qué conviene más, un arriendo en UF o en pesos con reajuste por IPC?"
    respuesta: "Ambos siguen la inflación. En UF el monto en pesos cambia un poco todos los días; en pesos con reajuste pagas lo mismo durante 6 o 12 meses y luego hay un salto. La UF es más simple de calcular; el arriendo en pesos es más fácil de presupuestar mes a mes."
---
Si tu contrato dice que la renta «se reajustará según la variación del IPC», el nuevo arriendo es la renta actual × (1 + variación **acumulada** del IPC en los meses que fija el contrato). Lo importante es elegir bien esos meses y componer las variaciones mensuales: no se suman.

## Qué dice la ley sobre el reajuste del arriendo

Los arriendos de inmuebles urbanos se rigen por la [Ley 18.101](https://www.bcn.cl/leychile/navegar?idNorma=29526). Esa ley no fija cuánto ni cada cuánto sube la renta: según la guía Ley Fácil de la Biblioteca del Congreso Nacional, el contrato puede contener el valor de la renta, **la forma de reajuste** y su duración, entre otras cláusulas que acuerden las partes.

En la práctica, esto significa que:

- **Manda tu contrato.** El índice (IPC o UF), la frecuencia y los meses que se consideran son los que diga la cláusula de reajuste.
- **Sin cláusula, no hay reajuste automático.** La ley no agrega un reajuste por su cuenta; para cambiar la renta se necesita un nuevo acuerdo, por ejemplo al renovar el contrato.
- **El término del contrato tiene reglas.** En los contratos mes a mes o de duración indefinida, el arrendador solo puede dar el desahucio por vía judicial o con notificación personal de un notario. El plazo es de dos meses, más un mes por cada año completo que el arrendatario haya ocupado el inmueble, con un máximo de seis meses en total.

Conviene que el contrato conste por escrito y con las firmas autorizadas ante notario. Desde la [Ley 21.461](https://www.bcn.cl/leychile/navegar?idNorma=1178004) de 2022, ese contrato sirve como antecedente suficiente para cobrar rentas impagas mediante el procedimiento monitorio que creó esa ley. Si la cláusula de reajuste es clara, también será claro cuánto se debe.

Esto es una guía general, no asesoría legal. Para un caso con conflicto, consulta la guía Ley Fácil de la BCN o la Corporación de Asistencia Judicial de tu región.

## Cláusulas típicas: semestral o anual

En los contratos en pesos es común encontrar una de estas dos fórmulas:

| Tipo de cláusula | Redacción habitual | Meses que se componen |
|---|---|---|
| Semestral | «La renta se reajustará cada seis meses según la variación del IPC del semestre anterior» | 6 variaciones mensuales |
| Anual | «La renta se reajustará cada doce meses en el 100% de la variación del IPC de los últimos doce meses» | 12 variaciones mensuales |

Antes de calcular, revisa en tu cláusula:

1. **La frecuencia:** cada 6 o cada 12 meses, contados desde el inicio del contrato.
2. **Los meses del IPC:** si habla del «semestre anterior», de «los últimos seis meses» o de meses específicos.
3. **El porcentaje:** lo habitual es el 100% de la variación, pero el contrato puede fijar otro.
4. **La renta base:** el reajuste se aplica sobre la renta vigente, es decir, la que ya incluye los reajustes anteriores.

## Qué meses del IPC usar

El IPC lo calcula el Instituto Nacional de Estadísticas (INE). Según sus preguntas frecuentes, se publica a las **08:00 del día 8 de cada mes**, con el dato del mes anterior. Si el 8 no es día hábil, se publica el día hábil inmediatamente anterior.

Esto importa porque el reajuste suele cobrarse en los primeros días del mes, antes de que salga el IPC del mes recién terminado. Un ejemplo:

- Tu arriendo se reajusta en octubre y lo pagas el día 5.
- El IPC de septiembre se publica recién alrededor del 8 de octubre, así que todavía no existe.
- Los últimos seis meses con IPC publicado son **marzo a agosto**: esos son los que compones.

Si quieres el cálculo oficial con los índices del INE, usa la [Calculadora IPC del INE](https://calculadoraipc.ine.gob.cl/). Ojo con cómo se eligen los meses: el **mes de inicio es el mes anterior** al primer mes del período. Para el período de marzo a agosto, el mes de inicio es febrero y el de término, agosto. Para una variación en 12 meses, el mes de inicio y el de término son el mismo mes de dos años seguidos (por ejemplo, agosto a agosto).

No confundas la variación **en 12 meses** con la variación **acumulada en el año**: esta última se mide desde diciembre del año anterior, no desde hace doce meses.

## Cómo calcular la variación acumulada

Las variaciones mensuales se **componen**: cada mes, los precios suben sobre lo que ya habían subido. La fórmula es:

> Variación acumulada = (1 + v₁) × (1 + v₂) × … × (1 + vₙ) − 1

donde cada *v* es la variación mensual del IPC expresada como fracción (0,4% = 0,004).

{% set variaciones = [0.004, 0.003, 0.002, -0.001, 0.005, 0.003] %}
{% set meses_ipc = ["Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto"] %}
{% set r = calc.reajustar_por_ipc(500000, variaciones) %}
{% set suma = variaciones|sum %}

### Ejemplo con un arriendo de $500.000

Supón un reajuste semestral en octubre con estas variaciones mensuales (son **valores de ejemplo**; las reales están en la página del [IPC]({{ ruta('/ipc/') }})):

| Mes del IPC | Variación del mes | Factor (1 + v) | Variación acumulada |
|---|---:|---:|---:|
{% for v in variaciones -%}
| {{ meses_ipc[loop.index0] }} | {{ v|porcentaje(1, true) }} | {{ (1 + v)|numero(3) }} | {{ calc.variacion_acumulada(variaciones[:loop.index])|porcentaje(2, true) }} |
{% endfor %}

La variación acumulada del semestre es **{{ r.variacion|porcentaje(2, true) }}**. El nuevo arriendo es $500.000 × (1 + {{ r.variacion|numero(5) }}) = **{{ r.nuevo_monto|pesos }}**, un aumento de {{ r.diferencia|pesos }} al mes. Junio tuvo IPC negativo, y por eso la variación acumulada baja ese mes: el cálculo lo incorpora sin hacer nada especial.

### Por qué no se suman

Si sumaras las seis variaciones obtendrías {{ suma|porcentaje(1, true) }} y un arriendo de {{ (500000 * (1 + suma))|pesos }}: {{ (r.nuevo_monto - 500000 * (1 + suma))|pesos }} menos de lo que corresponde. La diferencia parece pequeña, pero crece con el número de meses y con la inflación. Con doce meses de 0,3% cada uno, la suma da 3,6% y la variación compuesta es {{ calc.variacion_acumulada([0.003] * 12)|porcentaje(2) }}.

Un detalle de redondeo: el INE publica las variaciones mensuales con un decimal. Su calculadora hace los cálculos internos con 12 decimales y entrega la variación del período con un decimal, así que su resultado puede diferir levemente del que obtienes al componer las variaciones mensuales. Para un acuerdo formal o un juicio, usa el resultado de la calculadora del INE.

### Paso a paso

1. Lee la cláusula de reajuste: frecuencia, índice y meses.
2. Identifica el último IPC publicado en la fecha del reajuste.
3. Anota las variaciones mensuales del período en la tabla del [IPC mensual]({{ ruta('/ipc/') }}).
4. Multiplica los factores (1 + variación) y resta 1.
5. Multiplica la renta vigente por (1 + variación acumulada) y redondea al peso.
6. Comunica el nuevo monto por escrito, con el detalle de los meses usados.

La [calculadora de reajuste de arriendo por IPC]({{ ruta('/calculadoras/reajuste-arriendo-ipc/') }}) hace los pasos 3 a 5 por ti con las variaciones publicadas por el INE.

## Arriendo en UF o en pesos con reajuste IPC

En un contrato en UF no hay que calcular reajustes: el monto en UF queda fijo y lo que cambia es su valor en pesos. La UF la calcula el Banco Central: se reajusta todos los días, desde el día 10 de cada mes hasta el día 9 del mes siguiente, según la variación del IPC del mes anterior. Al cerrar ese período, la UF subió exactamente lo que subió el IPC; si el IPC fue negativo, baja en la misma proporción.

Por ejemplo, con la UF del {{ hoy|fecha_larga }} ({{ uf_hoy|pesos(2) }}), un arriendo de 12 UF equivale a **{{ (12 * uf_hoy)|pesos }}**. Conviene que el contrato indique con la UF de qué día se convierte (por ejemplo, la del día de pago).

| | Arriendo en pesos con reajuste IPC | Arriendo en UF |
|---|---|---|
| Cuándo cambia lo que pagas | De una vez, cada 6 o 12 meses | Un poco cada día |
| Qué inflación recoge | La de los meses que fija el contrato | La del mes anterior, día a día |
| Cálculo | Hay que componer las variaciones del IPC | UF del día × monto en UF |
| Presupuesto mensual | Fijo entre reajustes | Varía levemente cada mes |

En el largo plazo, ambos siguen la inflación. La diferencia está en el momento en que se nota el alza y en lo fácil que es calcular. Puedes revisar el valor diario en la página de la [UF de hoy]({{ ruta('/uf/') }}).

## Errores comunes al reajustar

- **Sumar las variaciones mensuales** en vez de componerlas.
- **Incluir un mes que aún no se publica** o saltarse uno del período.
- **Reajustar sobre la renta original** en lugar de la renta vigente.
- **Usar la variación acumulada en el año** cuando el contrato habla de los últimos 12 meses.
- **No dejar el cálculo por escrito.** Enviar el detalle de los meses y las variaciones evita discusiones.
