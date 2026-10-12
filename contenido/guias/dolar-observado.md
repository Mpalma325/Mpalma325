---
titulo: "Qué es el dólar observado y cómo se calcula ({{ hoy.year }})"
descripcion: "Qué es el dólar observado, cómo lo calcula y publica el Banco Central, en qué se diferencia del precio de bancos y casas de cambio y para qué se usa."
h1: "Qué es el dólar observado"
resumen: "El tipo de cambio de referencia que publica el Banco Central para cada día hábil bancario: cómo se calcula, por qué no es el precio al que compras dólares y cuándo se usa."
publicada: 2026-10-12
revisada: 2026-10-12
categoria: indicadores
orden: 30
calculadoras:
  - /dolar/
  - /dolar/100-dolares-en-pesos/
fuentes:
  - nombre: "Dólar observado: definición y cobertura (Banco Central de Chile)"
    url: "https://www.bcentral.cl/documents/33528/2546026/Dolar_Observado.pdf/d8d86d97-9939-b71e-1d93-afe4eab3f743?version=1.3&t=1676491832517&download=true"
  - nombre: "Ley Orgánica Constitucional del Banco Central de Chile, artículo 44 (Banco Central de Chile)"
    url: "https://www.bcentral.cl/documents/33528/133463/LOC_bcch.pdf/d6c54763-4007-7883-c1fa-c8fb40c0226a?t=1645128472723"
  - nombre: "Indicadores diarios (Banco Central de Chile)"
    url: "https://si3.bcentral.cl/Bdemovil/BDE/IndicadoresDiarios"
  - nombre: "Dólar observado 2026 (Servicio de Impuestos Internos)"
    url: "https://www.sii.cl/valores_y_fechas/dolar/dolar2026.htm"
faq:
  - pregunta: "¿Qué es el dólar observado?"
    respuesta: "Es el tipo de cambio de referencia del dólar en pesos chilenos que calcula el Banco Central de Chile para cada día hábil bancario. Corresponde al promedio ponderado de las compras y ventas de dólares al contado que hicieron los bancos y las corredoras de bolsa del Mercado Cambiario Formal el día hábil bancario anterior."
  - pregunta: "¿Por qué el dólar observado es distinto del dólar en tiempo real?"
    respuesta: "Porque el dólar observado de un día es un promedio de las operaciones del día hábil bancario anterior y no cambia durante la jornada. El dólar spot, en cambio, se mueve minuto a minuto según la oferta y la demanda."
  - pregunta: "¿Hay dólar observado los fines de semana y feriados?"
    respuesta: "No. Cada valor rige para un día hábil bancario, así que los sábados, domingos y feriados bancarios no tienen uno propio. Para esos días, el Banco Central muestra en sus indicadores diarios el último dato disponible. Si un contrato fija otra regla, se aplica la del contrato."
  - pregunta: "¿Cuánto son 100 dólares en pesos chilenos?"
    respuesta: "Con el dólar observado del {{ dolar[0]|fecha_larga }} ({{ dolar[1]|pesos(2) }}), 100 dólares equivalen a {{ (100 * dolar[1])|pesos }}. Si compras dólares en un banco o casa de cambio, el monto dependerá del precio de venta que fije esa institución."
  - pregunta: "¿Por qué mi banco me cobra más que el dólar observado?"
    respuesta: "Porque bancos y casas de cambio fijan su propio precio de venta, por sobre el valor de mercado, y uno de compra, por debajo. La diferencia entre ambos (el spread) es su margen. El dólar observado es un promedio de referencia, no una cotización a la que puedas comprar."
---
El **dólar observado** es el tipo de cambio de referencia entre el dólar de Estados Unidos y el peso chileno que calcula y publica el Banco Central de Chile para cada día hábil bancario. El último valor disponible, del {{ dolar[0]|fecha_larga }}, es **{{ dolar[1]|pesos(2) }}** por dólar.

## Qué es el dólar observado

No es el precio al que puedes comprar dólares, sino un **promedio** de lo que transaron bancos y corredoras de bolsa el día hábil bancario anterior. Por eso sirve como referencia neutral: es el mismo para todos y no depende del precio de una institución en particular.

Su base legal está en el artículo 44 de la Ley Orgánica Constitucional del Banco Central, que obliga al Banco a publicar cada día el tipo de cambio de las monedas extranjeras de general aceptación en los mercados internacionales, a partir de las transacciones del Mercado Cambiario Formal del día hábil inmediatamente anterior. Las reglas de detalle están en el Capítulo I del Compendio de Normas de Cambios Internacionales del Banco Central.

Como es un valor público y verificable, se usa como referencia cuando hay que convertir dólares a pesos: en contratos, trámites tributarios y estadísticas. En la página del [dólar de hoy]({{ ruta('/dolar/') }}) puedes ver su valor, su variación y el gráfico de los últimos 12 meses.

## Cómo se calcula y cuándo se publica

Según el Banco Central, el dólar observado es el **promedio ponderado por monto** de las operaciones de compra y venta de dólares al contado (spot) que hicieron las empresas bancarias y las corredoras de bolsa del Mercado Cambiario Formal durante el **día hábil bancario inmediatamente anterior**. Se expresa con dos decimales y, una vez calculado y publicado, no se revisa.

La publicación tiene dos momentos:

- **En el sitio web del Banco Central**, como referencia, a partir de las 17:30 del día hábil bancario anterior.
- **En el Diario Oficial**, el mismo día hábil bancario en que rige.

Esto tiene dos consecuencias prácticas:

- **El observado de hoy refleja el mercado de ayer.** Si el dólar se mueve mucho durante la mañana, el observado del día no lo recoge: aparecerá en el del día hábil bancario siguiente.
- **Los fines de semana y feriados bancarios no tienen dólar observado propio.** Para un día no hábil, el Banco Central muestra en sus indicadores diarios el último dato disponible. Si un contrato debe convertir un pago en un día no hábil, revisa qué fecha fija.

| Día de las operaciones | Día en que rige el dólar observado que generan |
|---|---|
| Lunes | Martes |
| Jueves | Viernes |
| Viernes | Siguiente día hábil bancario (normalmente, el lunes) |

## Dólar observado, dólar spot y precio de bancos

Cuando se habla del «precio del dólar» pueden ser tres cosas distintas:

| Tipo de cambio | Quién lo fija | Cuándo cambia | Para qué sirve |
|---|---|---|---|
| Dólar observado | Banco Central, con las operaciones del día hábil bancario anterior | Una vez por día hábil bancario | Referencia para contratos, trámites e impuestos |
| Dólar spot | El mercado, por oferta y demanda | Durante toda la jornada | Operaciones entre bancos e inversionistas |
| Precio comprador y vendedor | Cada banco o casa de cambio | Cuando lo decida la institución | Lo que pagas o recibes al cambiar dinero |

Cuando cambias dinero, la institución te ofrece dos precios: uno **comprador**, lo que te paga por tus dólares, y uno **vendedor**, lo que te cobra por venderte dólares. La diferencia entre ambos, el **spread**, es su margen. Cada institución fija el suyo, así que conviene comparar antes de cambiar montos grandes.

{% set margen = 0.02 %}
Un ejemplo con un margen **hipotético** de {{ margen|porcentaje(0) }} sobre el observado: comprar 100 dólares te costaría {{ (100 * dolar[1] * (1 + margen))|pesos }} en vez de {{ (100 * dolar[1])|pesos }}, es decir, {{ (100 * dolar[1] * margen)|pesos }} más. Si vendieras 100 dólares con un margen igual bajo el observado, recibirías {{ (100 * dolar[1] * (1 - margen))|pesos }}.

## Para qué se usa el dólar observado

- **Contratos en dólares que se pagan en pesos.** Un contrato puede fijar que la conversión se haga con el dólar observado de una fecha determinada, por ejemplo, la del día de pago. Revisa qué fecha fija el tuyo.
- **Impuestos.** El Servicio de Impuestos Internos (SII) publica en su sitio el dólar observado de cada día y, en sus instrucciones, lo usa como referencia para convertir a pesos montos en moneda extranjera.
- **Créditos reajustables.** El Banco Central autoriza el dólar observado como uno de los sistemas de reajuste de las operaciones de crédito en moneda nacional.
- **Estadísticas.** Es la serie con la que el Banco Central informa el tipo de cambio del peso con el dólar en su Base de Datos Estadísticos.

Si un documento no dice qué tipo de cambio usar, pregunta antes de pagar o facturar: en montos grandes, la diferencia entre el observado y el precio de un banco puede ser importante.

## Qué significa que el dólar suba o baje

El dólar observado dice cuántos pesos se necesitan para comprar un dólar. Cuando **sube**, el peso vale menos frente al dólar; cuando **baja**, el peso se fortalece.

{% set alza = 0.05 %}
- **Si sube el dólar,** todo lo que pagas en dólares cuesta más pesos: compras por internet en moneda extranjera, pasajes, viajes y productos importados. Quien recibe ingresos en dólares, como un exportador, obtiene más pesos por cada dólar.
- **Si baja el dólar,** ocurre lo contrario: lo importado se abarata en pesos y quien recibe dólares obtiene menos pesos.

Por ejemplo, una compra de US$200 cuesta hoy {{ (200 * dolar[1])|pesos }}. Si el dólar subiera {{ alza|porcentaje(0) }}, a {{ (dolar[1] * (1 + alza))|pesos(2) }}, la misma compra costaría {{ (200 * dolar[1] * (1 + alza))|pesos }}: {{ (200 * dolar[1] * alza)|pesos }} más sin que cambie el precio en dólares.

Las variaciones diarias suelen ser pequeñas, pero se acumulan. En la página del [dólar]({{ ruta('/dolar/') }}) puedes revisar cuánto ha cambiado en los últimos 12 meses y sus valores máximo y mínimo del año.

## Cómo convertir dólares a pesos

Para pasar de dólares a pesos, multiplica por el dólar observado; para pasar de pesos a dólares, divide por él.

> Pesos = dólares × dólar observado
>
> Dólares = pesos ÷ dólar observado

Con el valor del {{ dolar[0]|fecha_larga }}:

| Dólares | Pesos chilenos |
|---:|---:|
{% for monto in [1, 10, 50, 100, 500, 1000] -%}
| US${{ monto|numero }} | {{ (monto * dolar[1])|pesos(2) if monto == 1 else (monto * dolar[1])|pesos }} |
{% endfor %}

Como el dólar observado tiene dos decimales, en montos grandes esos decimales importan: US$10.000 a {{ dolar[1]|pesos(2) }} son {{ (10000 * dolar[1])|pesos }}, y cada centavo de diferencia en el tipo de cambio suma $100.

Al revés, $100.000 equivalen a US${{ (100000 / dolar[1])|numero(2) }}. Para un monto puntual, usa el [conversor de 100 dólares a pesos]({{ ruta('/dolar/100-dolares-en-pesos/') }}) o el de la página del [dólar]({{ ruta('/dolar/') }}).

Recuerda que estas conversiones usan el valor de referencia. Si vas a comprar o vender dólares, el monto final dependerá del precio de tu banco o casa de cambio.
