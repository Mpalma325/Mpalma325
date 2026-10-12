# Mantención

El sitio se actualiza solo, pero las leyes cambian. Esta guía explica qué se actualiza automáticamente, qué hay que revisar a mano y cómo crecer el sitio.

## Qué se actualiza solo

| Qué | Cómo |
|---|---|
| UF, dólar, euro, UTM, IPC y otros indicadores | GitHub Actions los descarga dos veces al día |
| UF hasta el día 9 del mes siguiente | Se calcula con la fórmula oficial apenas se publica el IPC |
| UF proyectada | Se recalcula con la inflación de los últimos 12 meses |
| Feriados de cada año (incluidos los trasladados) | Se calculan con las reglas de la ley |
| Retención de honorarios 2027 (16%) y 2028 (17%) | Ya cargadas con su fecha de inicio |
| Aporte del empleador por la reforma de pensiones (agosto 2027, 2028, 2029) | Ya cargado con sus fechas |
| Versiones de las GitHub Actions | Dependabot abre un pull request una vez al mes |

## Cómo les avisa el sistema

Cuando hay algo que revisar, el workflow **Actualizar y publicar** termina en rojo y **GitHub les manda un correo**. El sitio igual se publica con lo último disponible. Los avisos posibles son:

- Llegó la fecha `revisar_antes_de` de algún grupo de `parametros/chile.yaml`.
- Los datos están atrasados (por ejemplo, el dólar no se actualiza hace más de 7 días).
- Falta la UF del día: es un error grave y el sitio no se publica hasta que se resuelva.

En el resumen del job (pestaña *Actions* → la ejecución en rojo → *Summary*) aparece exactamente qué revisar.

## Calendario de revisión manual

| Cuándo | Qué revisar | Dónde verificar |
|---|---|---|
| **Enero** | Reajuste del ingreso mínimo (la Ley 21.830 fija uno para el 1 de enero de 2027 según el IPC) | [bcn.cl](https://www.bcn.cl), [dt.gob.cl](https://www.dt.gob.cl) |
| **Febrero** | Topes imponibles (AFP, salud y seguro de cesantía) | [spensiones.cl](https://www.spensiones.cl), PDF de indicadores de [previred.com](https://www.previred.com) |
| **Cada vez que se anuncie** | Cambio de comisión de alguna AFP | [spensiones.cl](https://www.spensiones.cl/portal/institucional/594/w3-propertyvalue-9897.html) |
| **Mayo** (o cuando haya ley) | Sueldo mínimo | Diario Oficial, Dirección del Trabajo |
| **Cada trimestre** | Tasa hipotecaria de referencia (`credito_hipotecario`) | Simuladores de bancos, CMF |
| **Antes de cada elección** | Agregar el día de la elección a `feriados_extra` (próximas: 29-oct-2028 municipales y regionales; 18-nov-2029 presidencial) | [servel.cl](https://www.servel.cl) |
| **Fin de año** | Leyes nuevas de feriados o cambios en la tabla del impuesto único | [sii.cl](https://www.sii.cl), [bcn.cl](https://www.bcn.cl) |

> Tip: el **PDF mensual de Indicadores Previsionales de Previred** trae casi todo (UF, UTM, topes, comisiones AFP, SIS, sueldo mínimo, asignación familiar) en una sola página. Contrastarlo una vez al mes toma 5 minutos.

## Cómo actualizar un parámetro

1. Abran `parametros/chile.yaml`.
2. **No borren ni modifiquen la entrada anterior.** Agreguen una nueva al final de `vigencias`, con la fecha `desde` en que empieza a regir. Por ejemplo, para nuevos topes:

   ```yaml
   topes_imponibles:
     revisar_antes_de: 2028-02-01      # ← la próxima revisión
     vigencias:
       - desde: 2026-02-01
         afp_salud_uf: 90.0
         cesantia_uf: 135.2
       - desde: 2027-02-01             # ← nueva entrada
         afp_salud_uf: 92.3
         cesantia_uf: 138.6
   ```

3. Actualicen `revisar_antes_de` a la fecha de la próxima revisión.
4. Corran `python -m pytest`. Algunas pruebas usan valores de 2026 a propósito; si una falla por el cambio, revisen si es un error real o si la prueba debe actualizarse.
5. Hagan commit y push. El sitio se republica solo.

Se pueden cargar cambios **por adelantado**: el sitio usa cada valor solo desde su fecha `desde`.

## Cómo crecer el sitio

### Agregar montos a las páginas en serie

En `lucas/paginas.py`, editen las listas `MONTOS_UF`, `MONTOS_DOLAR`, `MONTOS_EURO` o `SUELDOS`. Cada monto nuevo genera una página nueva con su propio título y contenido.

### Agregar una calculadora nueva

1. **La fórmula en Python:** función en `lucas/calculos.py`.
2. **La misma fórmula en JavaScript:** en `estaticos/js/calculos.js`, con las mismas operaciones y en el mismo orden. Agréguenla al objeto que se exporta al final.
3. **Pruebas:** casos en `tests/test_calculos.py`, y un caso en `tests/test_paridad_js.py` para verificar que Python y JavaScript den lo mismo.
4. **La plantilla:** en `plantillas/` (copien una existente, por ejemplo `calc_honorarios.html`).
5. **La interfaz:** en `estaticos/js/app.js`, una función `calcAlgo(form, res)`, registrada en el objeto `calculadoras` de la función `iniciar`.
6. **La página:** en `lucas/paginas.py`, dentro de `paginas_calculadoras`, con título, descripción, preguntas frecuentes y `calculadora=True`. Agréguenla también a la lista de calculadoras de esa misma función.
7. Corran `python -m pytest` y revisen la página con `python -m lucas construir --demo && python -m lucas servir`.

### Ideas priorizadas

Ver la hoja de ruta en [PLAN_DE_NEGOCIO.md](PLAN_DE_NEGOCIO.md#6-hoja-de-ruta): finiquito y vacaciones proporcionales, permiso de circulación 2027, simulador de Operación Renta, licencia médica, horas extra y APV.

## Si algo falla

| Síntoma | Qué hacer |
|---|---|
| El paso "Descargar datos nuevos" muestra advertencias | Normalmente es temporal: la próxima ejecución lo resuelve. Si dura varios días, revisen si mindicador.cl cambió y configuren el respaldo de la CMF (`CMF_API_KEY`). |
| Falla `test_uf_contra_datos_reales` | La fuente entregó una UF que no calza con la fórmula oficial. Revisen el valor en sii.cl o bcentral.cl antes de publicar. |
| Falla `test_utm_contra_datos_reales` | Revisen `utm_se_mantiene_con_ipc_negativo` en `parametros/chile.yaml` y el valor en sii.cl. |
| Falla "Publicar en Cloudflare" | Revisen que los secretos `CLOUDFLARE_API_TOKEN` y `CLOUDFLARE_ACCOUNT_ID` existan y que el token no haya expirado. |
| El sitio muestra valores viejos | Revisen la pestaña *Actions*. Si el workflow programado está deshabilitado, vuelvan a habilitarlo. GitHub desactiva los workflows programados de repositorios públicos tras 60 días sin actividad. |
