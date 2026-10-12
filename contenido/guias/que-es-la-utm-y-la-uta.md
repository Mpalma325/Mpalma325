---
titulo: "Qué es la UTM y la UTA y cómo se reajustan ({{ hoy.year }})"
descripcion: "Qué son la UTM y la UTA, cómo se reajusta la UTM con el IPC, para qué se usan en impuestos y multas y cuánto valen hoy, con ejemplos de conversión a pesos."
h1: "Qué es la UTM y la UTA"
resumen: "La UTM cambia cada mes según el IPC de dos meses antes y la UTA equivale a 12 UTM. Para qué sirven, cómo convertirlas a pesos y cuánto valen este mes."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: indicadores
orden: 20
calculadoras:
  - /utm/
  - /impuesto-unico/
fuentes:
  - nombre: "Código Tributario (DL 830), artículo 8 N° 10 (BCN)"
    url: "https://www.bcn.cl/leychile/navegar?idNorma=6374"
  - nombre: "UTM, UTA e IPC 2026 (Servicio de Impuestos Internos)"
    url: "https://www.sii.cl/valores_y_fechas/utm/utm2026.htm"
  - nombre: "UTM, UTA e IPC 2025 (Servicio de Impuestos Internos)"
    url: "https://www.sii.cl/valores_y_fechas/utm/utm2025.htm"
  - nombre: "IPC de junio de 2025: variación mensual de -0,4% (INE)"
    url: "https://www.ine.gob.cl/sala-de-prensa/prensa/general/noticia/2025/07/08/%C3%ADndice-de-precios-al-consumidor-(ipc)-de-junio-present%C3%B3-una-variaci%C3%B3n-mensual-de--0-4"
  - nombre: "Impuesto Único de Segunda Categoría 2026: tablas mensuales (SII)"
    url: "https://www.sii.cl/valores_y_fechas/impuesto_2da_categoria/impuesto2026.htm"
  - nombre: "Guía práctica de la Declaración de Renta 2026 (SII)"
    url: "https://www.sii.cl/servicios_online/renta/guia_practica_renta_2026.pdf"
  - nombre: "Seguridad en vehículos motorizados: multas de tránsito, guía Ley Fácil (BCN)"
    url: "https://www.bcn.cl/portal/leyfacil/recurso/seguridad-en-vehiculos-motorizados"
faq:
  - pregunta: "¿Cuánto vale la UTM hoy?"
    respuesta: "En {{ hoy|mes_de_anio }}, la UTM vale {{ utm_hoy|pesos }} y la UTA, {{ (utm_hoy * 12)|pesos }}. El valor rige todo el mes y cambia el día 1 del mes siguiente."
  - pregunta: "¿Cómo se calcula la UTM del próximo mes?"
    respuesta: "Se multiplica la UTM del mes en curso por 1 más la variación del IPC del mes anterior, y se redondea al peso. Por ejemplo, la UTM de noviembre es la de octubre reajustada por el IPC de septiembre, que el INE publica el 8 de octubre (o el día hábil anterior, si el 8 no es hábil)."
  - pregunta: "¿La UTM puede bajar?"
    respuesta: "Sí. Si el IPC que se aplica es negativo, la UTM baja. Ocurrió en agosto de 2025: el IPC de junio de 2025 fue -0,4% y, según el SII, la UTM pasó de $68.923 en julio a $68.647 en agosto."
  - pregunta: "¿Qué diferencia hay entre la UTM y la UF?"
    respuesta: "La UF la calcula el Banco Central, cambia todos los días y se usa sobre todo en créditos y contratos. La UTM la publica el SII, cambia una vez al mes y se usa en impuestos, multas y otros montos fijados por ley."
  - pregunta: "¿Qué es la UTA y cómo se calcula?"
    respuesta: "La unidad tributaria anual equivale a 12 UTM. El Código Tributario la define como la UTM vigente en el último mes del año comercial, multiplicada por 12 (o por el número de meses de ese año comercial). Con la UTM de este mes, son {{ (utm_hoy * 12)|pesos }}."
---
{% set tramos = p.tramos_impuesto %}
{% set ejemplo = calc.impuesto_unico(1500000, p) %}
La **UTM** (unidad tributaria mensual) es un monto en pesos que se reajusta cada mes según la inflación y que sirve para fijar impuestos, multas y otros valores en la ley. La **UTA** (unidad tributaria anual) equivale a 12 UTM. En {{ hoy|mes_de_anio }}, la UTM vale **{{ utm_hoy|pesos }}** y la UTA, **{{ (utm_hoy * 12)|pesos }}**.

## Qué es la UTM

El artículo 8 N° 10 del Código Tributario define la unidad tributaria como «la cantidad de dinero cuyo monto, determinado por ley y permanentemente actualizado, sirve como medida o como punto de referencia tributario». En la práctica, es una forma de escribir montos en la ley sin que pierdan valor con la inflación.

Si una norma fija una multa en UTM, no hay que cambiar la ley cada año: basta con convertirla con el valor que corresponda. Hoy, 1 UTM son {{ utm_hoy|pesos }}; si hay inflación, dentro de un año serán más pesos, pero alcanzarán para comprar más o menos lo mismo.

El Servicio de Impuestos Internos (SII) publica el valor de cada mes, junto con la UTA y el IPC, en su sección de valores y fechas. La UTM se expresa en pesos, sin decimales.

## Cómo se reajusta la UTM

Cada mes, la UTM es la del mes anterior reajustada por la variación del IPC de **dos meses antes**, redondeada al peso:

> UTM del mes = UTM del mes anterior × (1 + variación del IPC de dos meses antes)

Por ejemplo:

- La UTM de **noviembre** es la de octubre reajustada por el IPC de **septiembre**.
- La UTM de **enero** es la de diciembre reajustada por el IPC de **noviembre**.

El INE publica el IPC de cada mes el día 8 del mes siguiente, a las 08:00, o el día hábil anterior si el 8 no es hábil. Desde ese momento ya se puede calcular la UTM del mes subsiguiente: con el IPC de septiembre, publicado en octubre, se conoce la UTM de noviembre. En la página de la [UTM]({{ ruta('/utm/') }}) verás el valor del próximo mes apenas se conoce.

### Cuando el IPC es negativo, la UTM baja

La UTM no solo sube. Si el IPC aplicado es negativo, la UTM disminuye en la misma proporción. Así ocurrió en 2025, según las tablas del SII y los datos del INE:

| Mes de la UTM | IPC aplicado | UTM |
|---|---|---:|
| Julio de 2025 | Mayo de 2025: +0,2% | $68.923 |
| Agosto de 2025 | Junio de 2025: -0,4% | $68.647 |

El IPC de junio de 2025 fue de -0,4%, así que la UTM de agosto quedó $276 por debajo de la de julio: $68.923 × (1 − 0,004) = $68.647. No es un error de cálculo: es la regla aplicada a una inflación negativa.

## Qué es la UTA

La **UTA** (unidad tributaria anual) se usa para montos anuales, como los de la Operación Renta. Equivale a 12 veces la UTM: con el valor de este mes, son **{{ (utm_hoy * 12)|pesos }}**. Es la cifra que el SII publica cada mes junto a la UTM.

Hay un matiz importante. Para las obligaciones anuales, el mismo artículo del Código Tributario define la UTA como la UTM vigente en el **último mes del año comercial**, multiplicada por 12 (o por el número de meses del año comercial, si es más corto). Para quien cierra su año en diciembre, eso significa usar la UTA de diciembre del año que se declara.

Un ejemplo con cifras del SII: en la Operación Renta 2026, el límite exento del impuesto global complementario, de 13,5 UTA, se calculó con la UTA de diciembre de 2025 y fue de $11.265.804.

Para aplicar multas expresadas en UTA, en cambio, el Código Tributario usa la UTM vigente al momento de aplicarse la sanción, multiplicada por 12.

## Para qué se usan la UTM y la UTA

| Uso | Unidad | Ejemplo |
|---|---|---|
| Impuesto único de segunda categoría (trabajadores dependientes) | UTM | La tabla mensual está en UTM: exento hasta {{ tramos[0].hasta|numero(1) }} UTM ({{ (tramos[0].hasta * utm_hoy)|pesos }} este mes) |
| Impuesto global complementario (declaración anual) | UTA | La tabla anual está en UTA |
| Multas de tránsito | UTM | Infracción gravísima: de 1,5 a 3 UTM ({{ (1.5 * utm_hoy)|pesos }} a {{ (3 * utm_hoy)|pesos }} este mes) |
| Multas tributarias | UTM o UTA | Varias sanciones del Código Tributario se expresan en unidades tributarias |

En el caso del tránsito, según la guía Ley Fácil de la Biblioteca del Congreso Nacional, las multas van de 0,2 UTM, en las infracciones leves, a 3 UTM, en las gravísimas, como manipular el celular mientras se conduce.

### Ejemplo: la tabla del impuesto único

La tabla del impuesto único de segunda categoría se define en UTM y cada mes se convierte a pesos con la UTM vigente. Por eso los tramos en pesos cambian todos los meses, aunque la ley no cambie:

| Base tributable mensual | Hasta (en pesos, este mes) | Tasa marginal |
|---|---:|---:|
{% for t in tramos -%}
{% set desde = 0 if loop.first else loop.previtem.hasta -%}
| {% if t.hasta is none %}Más de {{ desde|numero }} UTM{% else %}{{ desde|numero(1) if desde % 1 else desde|numero }} a {{ t.hasta|numero(1) if t.hasta % 1 else t.hasta|numero }} UTM{% endif %} | {% if t.hasta is none %}Sin tope{% else %}{{ (t.hasta * utm_hoy)|pesos }}{% endif %} | {% if t.factor == 0 %}Exento{% else %}{{ t.factor|porcentaje(1) }}{% endif %} |
{% endfor %}

El impuesto del mes se calcula como base × factor − cantidad a rebajar, y la cantidad a rebajar también está en UTM. Con una base tributable de $1.500.000 (el sueldo imponible menos las cotizaciones obligatorias), el factor es {{ ejemplo.factor|porcentaje(1) }} y la rebaja, {{ ejemplo.rebaja|numero(2) }} UTM:

> $1.500.000 × {{ ejemplo.factor|porcentaje(1) }} − {{ ejemplo.rebaja|numero(2) }} × {{ utm_hoy|pesos }} = **{{ ejemplo.impuesto|pesos }}**

La tabla completa del mes, con las cantidades a rebajar en pesos, está en la página del [impuesto único]({{ ruta('/impuesto-unico/') }}).

## Cómo convertir UTM y UTA a pesos

Multiplica la cantidad de UTM por el valor del mes que corresponda. Para pasar de pesos a UTM, divide por ese valor.

| Cantidad | En pesos ({{ hoy|mes_de_anio }}) |
|---|---:|
{% for cantidad in [0.5, 1, 1.5, 3, 10] -%}
| {{ cantidad|numero(1) if cantidad % 1 else cantidad|numero }} UTM | {{ (cantidad * utm_hoy)|pesos }} |
{% endfor -%}
| 1 UTA | {{ (12 * utm_hoy)|pesos }} |

Usa siempre la UTM del mes que indique la norma o el documento: si usas la de otro mes, el monto en pesos no calzará. El [conversor de UTM a pesos]({{ ruta('/utm/') }}) hace la cuenta con el valor vigente.

## UTM, UTA y UF: en qué se diferencian

Las tres son unidades que siguen la inflación, pero no son intercambiables:

| | UTM | UTA | UF |
|---|---|---|---|
| Quién la publica | SII | SII | Banco Central |
| Cada cuánto cambia | Una vez al mes | Una vez al mes (12 × UTM) | Todos los días |
| Qué IPC usa | El de dos meses antes | El mismo de la UTM | El del mes anterior, repartido entre el día 10 y el día 9 |
| Uso habitual | Impuestos mensuales y multas | Impuestos y límites anuales | Créditos, arriendos y seguros |
| Valor hoy | {{ utm_hoy|pesos }} | {{ (utm_hoy * 12)|pesos }} | {{ uf_hoy|pesos(2) }} |

Si un contrato o una norma está en UF, usa el [valor de la UF del día]({{ ruta('/uf/') }}); si está en UTM, el valor del mes. En la guía [qué es la UF]({{ ruta('/guias/que-es-la-uf/') }}) está explicado su cálculo diario.

## Errores comunes

- **Usar la UTM de otro mes.** Cada mes tiene su valor; una multa o un impuesto se convierte con el que indique la norma.
- **Calcular la UTA con la UTM del mes actual para la declaración anual.** Para la Operación Renta se usa la UTA del último mes del año comercial: diciembre, si tu año termina en diciembre.
- **Confundir la UTM con la UF.** Aunque ambas siguen al IPC, la UF cambia a diario y la UTM una vez al mes.
- **Pensar que la UTM nunca baja.** Con IPC negativo, la UTM del mes siguiente baja; no es un error del cálculo.
