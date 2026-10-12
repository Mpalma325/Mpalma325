# Plan de negocio: Lucas Claras

> **En una frase:** un sitio de herramientas financieras para Chile que atrae visitas desde Google y las convierte en ingresos por publicidad y referidos, funcionando en piloto automático.

Fecha: octubre de 2026. Las cifras de mercado vienen de fuentes públicas (Ahrefs, Semrush, prensa) y son aproximadas. **Las proyecciones de ingresos son estimaciones propias, no promesas.**

---

## 1. Por qué esta idea y no otra

Evaluamos las alternativas típicas de "ingresos automáticos":

| Opción | Inversión | ¿Automático? | Riesgo | Veredicto |
|---|---|---|---|---|
| Bot de trading o cripto | Capital propio | Sí | Muy alto: la mayoría pierde dinero | ❌ |
| Dropshipping / e-commerce | Capital + publicidad | No (clientes, devoluciones) | Alto | ❌ |
| Contenido masivo generado con IA | Bajo | Sí | Google lo penaliza; bajo valor | ❌ |
| Freelance de ciencia de datos | Tiempo | No | Bajo | ✅ como complemento, no es pasivo |
| SaaS para pymes (p. ej., remuneraciones) | Tiempo + ventas + soporte | Parcial | Medio | ⏳ fase 3 |
| **Sitio de herramientas con tráfico orgánico** | **~$10.000/año** | **Sí** | **Bajo** | ✅ **elegido** |

¿Por qué el sitio?

1. **Costo casi cero:** dominio y nada más. Hosting y automatización gratis.
2. **Se mantiene solo:** GitHub Actions descarga datos, prueba, construye y publica dos veces al día, y les avisa por correo si algo necesita atención.
3. **Aprovecha lo que ustedes saben:** datos, programación, finanzas personales y el contexto chileno (UF, AFP, Previred, feriados).
4. **Es un activo:** el tráfico se acumula con el tiempo, y un sitio con ingresos estables se puede vender. Los marketplaces de sitios web los valoran como un múltiplo de su utilidad mensual.

## 2. El mercado

La demanda existe y está validada por sitios independientes:

| Sitio | Tráfico estimado | Comentario |
|---|---|---|
| uf-hoy.com | ~255.000 visitas orgánicas/mes (Ahrefs, abr-2025) | Autoridad moderada (DR 36): un sitio independiente sin gran marca |
| feriados.cl | ~499.000 visitas orgánicas/mes (Ahrefs, jul-2025) | Un solo tema: feriados |
| calcular.cl | 400.000–536.000 visitas/mes (Semrush, ene–mar 2025) | Multicalculadora |
| valor-utm.cl | ~34.000 visitas orgánicas/mes (Ahrefs, abr-2025) | Solo UTM |

**Competencia:** desde 2025 aparecieron muchos sitios nuevos (monedario, finclaro, simplo, hacecuentas, contable.app...) que también generan páginas en serie. Por eso **nuestra ventaja no es tener muchas páginas, sino la exactitud, la velocidad y la actualización automática**:

- Encontramos errores públicos en competidores: Nubox publica 15% de retención de honorarios para 2026 (es 15,25%) y los calendarios de feriados 2027 se contradicen entre sitios.
- Nuestras fórmulas se prueban automáticamente contra valores oficiales (tabla del SII, UF publicada por el Banco Central, feriados de gob.cl).

**Huecos sin cubrir** (oportunidades):

1. ✅ **UF proyectada:** no encontramos competidores. Ya está construida (`/uf/proyeccion/`).
2. **Permiso de circulación por modelo y año** (temporada febrero–marzo): no hay calculadora privada.
3. **Licencia médica** ("¿cuánto me pagan?"): solo está el simulador de SUSESO.
4. ✅ **Vacaciones proporcionales con el calendario real de feriados:** los competidores usan la aproximación 7/5. Ya está construida (`/calculadoras/vacaciones-proporcionales/`).
5. ✅ **Finiquito por causal:** ya está construido (`/calculadoras/finiquito/`). Pendiente: modelo de carta y recargos por despido injustificado.

**Amenaza principal:** los resúmenes con IA de Google (AI Overviews) reducen los clics en búsquedas de "dato del día". Según Pew Research (jul-2025), con resumen de IA se hace clic en un 8% de las búsquedas, contra un 15% sin resumen. Por eso **priorizamos calculadoras interactivas**, que la IA no reemplaza, y usamos las páginas de datos como puerta de entrada y para enlaces internos.

## 3. Cómo se gana dinero

### 3.1 Publicidad (Google AdSense)

- Ingreso por cada 1.000 páginas vistas (RPM): **estimamos entre US$1 y US$5** para tráfico chileno de finanzas. No hay datos públicos confiables; se sabrá midiendo.
- AdSense paga cuando se acumulan **CLP 60.000** (cuenta en pesos) o US$100.
- Otras redes (Ezoic, Mediavine, Raptive) exigen tráfico de EE. UU. o volúmenes muy altos: **al principio, solo AdSense es viable**.

### 3.2 Referidos y afiliados (más valor por visita)

| Programa | Qué paga (según sus bases públicas, verificar) | Dónde encaja |
|---|---|---|
| Fintual | 1% anual del saldo promedio del referido durante su primer año (2 años en APV) | Interés compuesto, sueldo (APV) |
| Racional | 0,84% anual de lo invertido por el referido durante 1 año (tope 50 referidos) | Interés compuesto |
| Global66 (Afiliados) | Pago por cliente nuevo (hasta US$20 en Colombia; consultar Chile) | Dólar, euro |
| Buda.com | 20% de las comisiones de tus referidos durante 1 año | (si se agrega contenido cripto) |
| Mercado Libre Afiliados | Hasta 8% según categoría | Contenido de compras, ahorro |

> Ejemplo: un referido que invierte $1.000.000 en Fintual genera unos $10.000 al año. Con 10 referidos nuevos al mes, al cabo de un año son ~$1.200.000 anuales adicionales. Ojo: algunos programas están pensados para invitar a conocidos; lean sus bases antes de publicar enlaces.

### 3.3 Productos propios (fase 2)

- **Planilla de remuneraciones para pymes** (Google Sheets o Excel) que se actualiza con los parámetros del sitio (topes, AFP, impuesto). Venta por Gumroad (paga en pesos chilenos) o Hotmart.
- Plantillas de presupuesto familiar en UF, de control de arriendos, etc.

### 3.4 Patrocinios y captación de clientes (fase 3)

- Corredores hipotecarios (simulador de crédito), software de RR.HH. (sueldo líquido, costo empleador), abogados laborales (finiquito).

## 4. Proyección de ingresos (estimaciones)

Supuestos: 1,5 páginas por visita; RPM de US$2 (US$3 en el escenario optimista); dólar ≈ $950. Sin contar referidos.

| Escenario | Visitas/mes al mes 6 | Al mes 12 | Al mes 24 | Ingreso AdSense al mes 24 |
|---|---|---|---|---|
| Pesimista (Google no nos posiciona) | 500 | 2.000 | 5.000 | ~US$15/mes |
| **Base** | 5.000 | 30.000 | 100.000 | **~US$300/mes (~$285.000)** |
| Optimista | 20.000 | 100.000 | 300.000 | ~US$1.350/mes (~$1.280.000) |

**¿Cuándo llegamos al primer millón?** (de pesos, que en Chile también cuenta 😄)

- Escenario base: alrededor del **mes 17–18**, sumando lo acumulado.
- Escenario optimista: antes del mes 12.
- Para ser millonarios en dólares, este sitio solo no basta. Es realista como **primera pieza** de un portafolio de activos digitales, si se reinvierte lo que genere (ver sección 9).

Qué mueve la aguja: más calculadoras útiles (cada una es una nueva puerta de entrada desde Google), enlaces desde otros sitios, y ubicar bien los referidos.

## 5. Costos

| Ítem | Costo |
|---|---|
| Dominio `.cl` (NIC Chile) | ~$10.000 al año (verificar tarifa vigente) |
| Hosting (Cloudflare, plan gratuito) | $0, con uso comercial permitido |
| Automatización (GitHub Actions) | $0. El proyecto usa ~150 minutos al mes; el plan gratuito incluye 2.000 en repositorios privados |
| Datos (mindicador.cl, API CMF) | $0 |
| Tiempo de puesta en marcha | 10–15 horas |
| Mantención | 1–2 horas al mes, más el tiempo que quieran dedicar a crecer |

**Impuestos:** lo que paga AdSense o un programa de referidos es renta. Consulten con un contador o con el SII cómo declararlo (por ejemplo, si conviene iniciar actividades) antes de recibir los primeros pagos.

## 6. Hoja de ruta

Cada pieza se publica entre 4 y 8 semanas antes de su temporada alta.

| Cuándo | Qué | Por qué |
|---|---|---|
| Oct–nov 2026 | **Lanzamiento**: dominio, Cloudflare, Search Console. Feriados 2027 y días hábiles (ya incluidos) | Las búsquedas de "feriados 2027" suben desde octubre |
| Nov–dic 2026 | ✅ Finiquito y vacaciones proporcionales (ya construidos). Agregar modelo de carta de finiquito y páginas por causal | Enero es el mes de los finiquitos; poca competencia de calidad |
| Dic 2026 | Postular a AdSense; activar referidos | El sitio ya tendrá páginas indexadas |
| Ene 2027 | **Permiso de circulación 2027** por tasación del SII (páginas por marca, modelo y año) | Se paga en febrero–marzo; no hay calculadora privada. Gran oportunidad de páginas en serie con valor real |
| Feb 2027 | **Simulador Operación Renta** para honorarios | Abril: ¿me devuelven o pago cotizaciones? |
| Mar–abr 2027 | Licencia médica; horas extra (jornada de 42 horas) | Poca competencia |
| May 2027 | APV régimen A vs. B; comparador de comisiones AFP | Mucho valor por visita (referidos) |
| Jul 2027 | Costo empleador con el aporte de 4,25% (agosto 2027, ya cargado) | Pymes y contadores |
| Continuo | Newsletter semanal automática con los indicadores | Audiencia propia que no depende de Google |

## 7. Roles sugeridos

| Persona | Rol | Responsabilidades |
|---|---|---|
| **Laura** (Ing. Civil en Computación) | Dueña técnica | Nuevas calculadoras, automatizaciones (permiso de circulación con datos del SII, newsletter), rendimiento y calidad del código |
| **Marcelo** (Ing. Civil Industrial) | Dueño del negocio | Search Console, AdSense, alianzas de referidos, métricas (RPM, CTR, ingresos por sección), priorización, impuestos |
| **Ambos** (ciencia de datos) | Análisis | Proyecciones (UF e inflación), análisis de tráfico, experimentos con la ubicación de anuncios |
| **Mochi** 🐶 | Bienestar del equipo | Pausas activas obligatorias |

## 8. Métricas e hitos

| Hito | Métrica |
|---|---|
| Mes 1 | Sitio en línea, sitemap enviado, 100+ páginas indexadas |
| Mes 3 | 5.000+ impresiones/mes en Search Console; primeras palabras clave en top 20 |
| Mes 6 | 5.000+ visitas/mes; AdSense aprobado; primeros referidos |
| Mes 12 | 30.000+ visitas/mes; ingresos cubren 10+ años de dominio 😉 |

Revisen cada mes: páginas indexadas, impresiones, CTR, posición media (Search Console); visitas y páginas por visita (Cloudflare Web Analytics); RPM e ingresos por página (AdSense); conversiones de referidos.

## 9. Riesgos

| Riesgo | Mitigación |
|---|---|
| Google tarda en posicionar un dominio nuevo | Paciencia (3–12 meses), contenido único (UF proyectada, calculadoras exactas) y enlaces desde otros sitios (compartir en comunidades, LinkedIn, universidad) |
| Resúmenes con IA en Google | Priorizar herramientas interactivas por sobre datos sueltos |
| Error en un cálculo | Pruebas automáticas contra valores oficiales, avisos legales y correo de contacto |
| La API de datos se cae | Respaldo con la API de la CMF, datos guardados en el repositorio y aviso por correo |
| AdSense rechaza la solicitud | Esperar a tener más páginas indexadas, revisar las políticas y volver a postular |
| Cambios legales (tasas, topes) | Parámetros con fecha de vigencia y recordatorios automáticos (ver MANTENCION.md) |

## 10. ¿Y qué hacer con la plata?

El ingreso más pasivo que existe es el **interés compuesto**. Según la propia calculadora del sitio:

- $100.000 al mes durante 20 años suman $24 millones aportados.
- Al 3% anual llegan a ~$32,7 millones; al 5%, a ~$40,6 millones; al 7%, a ~$50,8 millones.

Ideas generales (no es asesoría financiera):

- Armar primero un fondo de emergencia.
- Después, invertir lo que genere el sitio en instrumentos diversificados y de bajo costo.
- Considerar el APV cuando tengan sueldo, por su beneficio tributario.
- La combinación sitio que genera ingresos + inversión constante es el camino realista hacia ese "hazme millonario".
