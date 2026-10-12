---
titulo: "Qué es la UF y cómo se calcula su valor ({{ hoy.year }})"
descripcion: "Qué es la Unidad de Fomento, para qué se usa, cómo se calcula su valor diario con el IPC y por qué se conoce por adelantado, con ejemplos en pesos."
h1: "Qué es la UF y cómo se calcula"
resumen: "La UF se reajusta día a día según el IPC del mes anterior. Para qué sirve, la fórmula con que se calcula y por qué su valor se conoce hasta con un mes de anticipación."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: indicadores
orden: 10
calculadoras:
  - /uf/
  - /uf/proyeccion/
  - /calculadoras/credito-hipotecario/
fuentes:
  - nombre: "Valores de la UF 2026 (Servicio de Impuestos Internos)"
    url: "https://www.sii.cl/valores_y_fechas/uf/uf2026.htm"
  - nombre: "UTM, UTA e IPC 2026 (Servicio de Impuestos Internos)"
    url: "https://www.sii.cl/valores_y_fechas/utm/utm2026.htm"
faq:
  - pregunta: "¿Cuánto vale la UF hoy?"
    respuesta: "Hoy, {{ hoy|fecha_larga }}, la UF vale {{ uf_hoy|pesos(2) }}. Su valor cambia todos los días, pero los valores hasta el día 9 del mes siguiente se conocen apenas el INE publica el IPC."
  - pregunta: "¿Quién calcula el valor de la UF?"
    respuesta: "El Banco Central de Chile, a partir de la variación del IPC que publica el Instituto Nacional de Estadísticas (INE). El Servicio de Impuestos Internos publica tablas con el valor de cada día."
  - pregunta: "¿La UF puede bajar?"
    respuesta: "Sí. Si el IPC de un mes es negativo, la UF baja levemente día a día en el período que va del día 10 del mes siguiente al día 9 del subsiguiente."
  - pregunta: "¿Cómo convierto UF a pesos?"
    respuesta: "Multiplica la cantidad de UF por el valor de la UF del día: hoy, 10 UF equivalen a {{ (10 * uf_hoy)|pesos }}. Para pasar de pesos a UF, divide el monto en pesos por el valor de la UF."
---
La UF (Unidad de Fomento) es una unidad de cuenta que se reajusta según la inflación: su valor en pesos cambia día a día de acuerdo con el IPC, para que los montos expresados en UF mantengan su poder de compra. Hoy, {{ hoy|fecha_larga }}, una UF equivale a **{{ uf_hoy|pesos(2) }}**.

## Qué es la UF

La UF no es una moneda: no hay billetes ni monedas de UF. Es una unidad de medida para fijar montos que después se pagan en pesos, al valor que tenga la UF ese día. Se creó en Chile en 1967 y se usa para que los contratos de largo plazo conserven su valor real.

La diferencia se nota con el tiempo. Un monto fijo en pesos pierde poder de compra a medida que suben los precios. Un monto en UF, en cambio, se ajusta solo: un arriendo de 15 UF cuesta hoy {{ (15 * uf_hoy)|pesos }}, y mientras haya inflación costará más pesos cada mes, pero alcanzará para comprar más o menos lo mismo.

## Para qué se usa la UF

- **Créditos hipotecarios:** el dividendo se pacta en UF y se paga en pesos al valor del día.
- **Arriendos:** muchos contratos fijan la renta en UF.
- **Planes de isapre y seguros:** sus precios se expresan en UF.
- **Otros contratos de largo plazo**, en los que ambas partes quieren protegerse de la inflación.
- **Montos fijados por ley:** el tope imponible para las cotizaciones de AFP y salud es de {{ p.tope_imponible_uf|numero(1) }} UF al mes (unos {{ (p.tope_imponible_uf * uf_hoy)|pesos }} con la UF de hoy), y la remuneración con que se calcula la indemnización por años de servicio tiene un tope de {{ p.tope_indemnizacion_uf|numero }} UF.

Si tienes un contrato en UF, revísalo: ahí se indica qué valor de la UF se usa para convertir el monto a pesos.

## Cómo se calcula el valor de la UF

{# Mes en que empezó el período vigente de la UF (del día 10 al día 9 del mes siguiente). #}
{% set mes_inicio = hoy.month if hoy.day >= 10 else (hoy.month - 2) % 12 + 1 %}
El Banco Central de Chile calcula la UF con una regla fija, que no depende de decisiones del día a día:

1. **Período:** la UF se reajusta todos los días entre el día 10 de cada mes y el día 9 del mes siguiente.
2. **Reajuste total:** en ese período, la UF varía exactamente lo mismo que el IPC del mes anterior al inicio del período. Por ejemplo, entre el 10 de {{ mes_inicio|nombre_mes }} y el 9 de {{ (mes_inicio % 12 + 1)|nombre_mes }} se aplica el IPC de {{ ((mes_inicio - 2) % 12 + 1)|nombre_mes }}.
3. **Reparto diario:** ese reajuste se reparte en forma geométrica entre los días del período, de modo que la UF sube (o baja) en la misma proporción cada día.

En fórmula:

<p><code>UF(día) = UF(día 9) × (1 + IPC)<sup>n/d</sup></code></p>

donde *n* es la cantidad de días transcurridos desde el día 9 y *d* la cantidad de días del período, que coincide con los días del mes en que el período comienza (31, 30, 29 o 28). El resultado se redondea a dos decimales.

### Un ejemplo con números redondos

Supón que la UF del 9 de abril fue de $40.000 y que el IPC de marzo fue de 0,5%. El período va del 10 de abril al 9 de mayo y tiene 30 días, porque abril tiene 30 días:

- **10 de abril** (n = 1): 40.000 × 1,005<sup>1/30</sup> = {{ (40000 * 1.005 ** (1 / 30))|pesos(2) }}
- **24 de abril** (n = 15): 40.000 × 1,005<sup>15/30</sup> = {{ (40000 * 1.005 ** (15 / 30))|pesos(2) }}
- **9 de mayo** (n = 30): 40.000 × 1,005 = {{ (40000 * 1.005)|pesos(2) }}

Al cierre del período la UF subió exactamente el 0,5% del IPC de marzo, y ese valor del 9 de mayo es el punto de partida del período siguiente. Es un ejemplo ilustrativo: los valores reales de cada día están en la página de la [UF de hoy]({{ ruta('/uf/') }}). Si el IPC del mes es 0%, la UF se mantiene constante todo el período; si es negativo, baja un poco cada día.

## Por qué la UF se conoce por adelantado

El INE publica el IPC de cada mes alrededor del día 8 del mes siguiente. En ese momento ya se conocen los dos datos de la fórmula —la UF del día 9 y la variación del IPC— y quedan determinados todos los valores de la UF hasta el día 9 del mes siguiente. Por eso las tablas oficiales muestran la UF hasta con un mes de anticipación, y puedes saber hoy cuánto pagarás en pesos por un dividendo o un arriendo que vence en las próximas semanas.

Más allá de ese día 9, la UF depende de un IPC que todavía no se publica, así que solo se puede estimar. En la página de la [UF proyectada]({{ ruta('/uf/proyeccion/') }}) calculamos escenarios con la inflación de los últimos 12 meses.

## Ejemplos con la UF de hoy

Con la UF del {{ hoy|fecha_larga }} ({{ uf_hoy|pesos(2) }}):

| Monto en UF | Equivale hoy a |
|---|---:|
{% for monto in [1, 10, 15, 100, 1000, 3000] -%}
| {{ monto|numero }} UF | {{ (monto * uf_hoy)|pesos(2 if monto == 1 else 0) }} |
{% endfor %}

Para el camino inverso, divide por el valor de la UF: $1.000.000 equivalen hoy a {{ (1000000 / uf_hoy)|numero(2) }} UF. Si buscas un monto en particular, revisa por ejemplo [cuánto son 1.000 UF en pesos]({{ ruta('/uf/1000-uf-en-pesos/') }}), con su valor en los próximos días y en el último año.

{% set h = calc.simular_hipotecario(3000, 0.2, p.tasa_hipotecaria_referencia, 25, p) %}
El caso más común es el crédito hipotecario. Si compras una vivienda de 3.000 UF con un pie de 20% y pides {{ h.credito_uf|numero }} UF a 25 años, con una tasa de referencia de {{ p.tasa_hipotecaria_referencia|porcentaje(1) }} anual, el dividendo es de **{{ h.dividendo_uf|numero(2) }} UF** al mes sin seguros: hoy, {{ h.dividendo_pesos|pesos }}. En un crédito a tasa fija ese dividendo en UF no cambia, pero su valor en pesos sube a medida que sube la UF. Puedes simular tu caso en el [simulador de crédito hipotecario]({{ ruta('/calculadoras/credito-hipotecario/') }}).

## UF, UTM e IPC: en qué se diferencian

Los tres se relacionan con la inflación, pero cumplen funciones distintas:

- El **IPC** (Índice de Precios al Consumidor) mide cada mes la variación de los precios de una canasta de bienes y servicios que consumen los hogares. Lo publica el INE y es la base del reajuste de la UF y de la UTM. Revisa el [IPC del último mes]({{ ruta('/ipc/') }}).
- La **UF** cambia todos los días y se usa sobre todo en créditos, arriendos y contratos.
- La **UTM** (Unidad Tributaria Mensual) cambia una vez al mes, según el IPC de dos meses antes, y se usa para impuestos, multas y otros montos fijados por ley. En {{ hoy|mes_de_anio }} vale {{ utm_hoy|pesos }}: mira la [UTM del mes]({{ ruta('/utm/') }}).

En resumen: el IPC mide la inflación, y la UF y la UTM la usan para que los montos que se expresan en ellas no pierdan valor.
