# Plan de lanzamiento: visitas y enlaces en las primeras 8 semanas

Del lunes 12 de octubre al domingo 6 de diciembre de 2026. El objetivo es que personas reales conozcan Lucas Claras, lo usen y lo citen, sin hacer nada que Google considere spam. Para un sitio nuevo, los enlaces desde otros sitios son lo más difícil de conseguir: toma meses y no hay atajos que valgan el riesgo.

Las herramientas para esto ya están construidas:

- **Widget** (`/widget/`): otros sitios muestran la UF, el dólar y la UTM del día pegando dos líneas de código.
- **API abierta** (`/api/`): la UF, el dólar, el euro, la UTM, el IPC y los feriados en JSON, sin registro y con CORS.
- **Calculadoras y calendario de feriados**: lo que la gente comparte cuando le sirve.

---

## 1. Qué esperar

- En 8 semanas lo normal es tener decenas o pocos cientos de visitas desde comunidades y contactos, unos pocos sitios que enlacen o usen el widget y las primeras impresiones en Search Console. El tráfico orgánico importante tarda de 3 a 12 meses (ver [PLAN_DE_NEGOCIO.md](PLAN_DE_NEGOCIO.md)).
- Un enlace desde un sitio relevante (un blog de finanzas, una universidad, un medio) vale más que cien enlaces de directorios o comentarios.
- Lo que acelera de verdad: herramientas útiles, estar presentes cuando la gente busca (las temporadas de la sección 7) y responder bien cuando alguien pregunta.
- Presupuesten unas 3 a 4 horas a la semana entre los dos. Es más importante la constancia que un gran día de lanzamiento.

## 2. Las reglas de Google que seguimos

Las [políticas de spam de Google](https://developers.google.com/search/docs/essentials/spam-policies) definen el spam de enlaces como crear enlaces hacia o desde un sitio principalmente para manipular el posicionamiento. Entre sus ejemplos están:

- comprar o vender enlaces para posicionar, los intercambios excesivos de enlaces y los programas automáticos para crearlos;
- los enlaces con palabras clave, ocultos o de baja calidad **dentro de widgets que se distribuyen en varios sitios**;
- los enlaces distribuidos masivamente en pies de página o plantillas de otros sitios;
- **exigir un enlace** en unos términos de uso, un contrato o algo similar **sin permitir que el dueño del sitio lo califique** (por ejemplo, con `rel="nofollow"`).

Sobre los widgets en particular, Google publicó en septiembre de 2016 [«A reminder about widget links»](https://developers.google.com/search/blog/2016/09/a-reminder-about-widget-links): los enlaces que vienen dentro de un widget no los puso el dueño del sitio por decisión editorial, y deben llevar `rel="nofollow"` o eliminarse. Desde su anuncio de septiembre de 2019 sobre `nofollow` (vigente para el rastreo desde marzo de 2020), Google lo trata como una sugerencia y no como una orden.

### Decisión: el enlace del widget lleva `rel="nofollow"`

El código para insertar es:

```html
<div class="lucas-claras-widget" data-indicadores="uf,dolar,utm" data-tema="auto"><a href="https://lucasclaras.cl/" rel="nofollow">Indicadores de Lucas Claras</a></div>
<script async src="https://lucasclaras.cl/widget.js"></script>
```

- El enlace está en el HTML del sitio que inserta el widget, a la vista de quien copia el código, con la marca como texto, sin palabras clave y hacia la portada. No hay enlaces ocultos ni se agregan enlaces con JavaScript.
- Lleva `rel="nofollow"` desde el código, como pide Google. Las condiciones de uso piden mantener visible el enlace, pero permiten marcarlo con `nofollow`; nunca pedimos quitarlo.
- Lo que perdemos: ese enlace no traspasa relevancia para el posicionamiento. Lo que ganamos: ningún riesgo de una acción manual por enlaces artificiales (que hundiría todo el dominio), visitas de quienes hacen clic, reconocimiento de marca y la posibilidad de que quien ve el widget escriba sobre el sitio con un enlace editorial, que sí cuenta.
- Para la API pedimos un enlace visible de atribución y quien la usa decide si lo marca con `nofollow`. Eso cumple la regla de los términos de uso.

Los enlaces que se publican en LinkedIn, Reddit o GitHub tampoco traspasan relevancia, en general. Su valor está en las visitas y en que la gente conozca el sitio.

## 3. Antes de empezar (semana 0)

- [ ] El sitio está publicado en el dominio final, verificado en Search Console y Bing Webmaster Tools, con el sitemap enviado ([GUIA_PUESTA_EN_MARCHA.md](GUIA_PUESTA_EN_MARCHA.md), paso 6).
- [ ] `sitio.correo_contacto` está completo en `config.yaml`: sin un correo, nadie puede responder a una propuesta.
- [ ] `sitio.autores` está completo: un "Quiénes somos" con personas reales da confianza a lectores, periodistas y buscadores.
- [ ] La API responde con sus cabeceras: `curl -sI https://lucasclaras.cl/api/v1/indicadores.json` debe mostrar `access-control-allow-origin: *` y `cache-control: public, max-age=1800`.
- [ ] El widget funciona en una página HTML propia (un archivo en el escritorio con el código de `/widget/` basta).
- [ ] Si activan protecciones contra bots en Cloudflare, prueben de nuevo con `curl` y con el widget: la API y `/widget.js` deben seguir respondiendo a otros sitios y a programas.
- [ ] Tienen capturas de pantalla para publicar: el widget claro y oscuro, la calculadora de sueldo líquido y los feriados 2027.
- [ ] Tienen una planilla de seguimiento: fecha, dónde se publicó, enlace, respuesta y resultado.

## 4. Dónde compartir

Reglas generales: una comunidad a la vez; leer sus reglas antes de publicar; decir siempre que el proyecto es de ustedes; participar antes y después (no solo dejar el enlace); no pedir votos ni "me gusta"; no repetir el mismo texto en muchos lugares.

### Reddit

| Comunidad | Miembros (aprox.) | Qué compartir |
|---|---|---|
| r/chileIT | 34 mil | La historia técnica: sitio estático con Python, actualización automática con GitHub Actions, API JSON abierta y pruebas contra los valores oficiales. Es la comunidad con más afinidad. |
| r/chile | 915 mil | Solo si sus reglas lo permiten y con algo útil para cualquiera: los fines de semana largos de 2027 o una calculadora concreta. Mejor aún: responder hilos donde alguien pregunta justo eso. |
| r/RepublicadeChile | 124 mil | Igual que r/chile. |

- Los tamaños son estimaciones de un sitio de estadísticas de terceros ([GummySearch](https://gummysearch.com/r/chile/)) y pueden estar desactualizados.
- **Las reglas vigentes de cada comunidad no se pudieron revisar al preparar este plan.** Antes de publicar, lean la sección de reglas (*About* o *Acerca de*), busquen si hay un hilo semanal para promociones, usen la etiqueta (*flair*) que corresponda y, si dudan, escríbanles a los moderadores. Las publicaciones de cuentas nuevas sin historial suelen quedar filtradas.
- No se encontró un subreddit chileno de finanzas personales que se pudiera verificar. Búsquenlo en Reddit ("finanzas Chile") y revisen su actividad y reglas antes de usarlo. No creen comunidades ni cuentas para promocionar el sitio.

### LinkedIn

Usen los perfiles personales de Laura y Marcelo: al principio llegan a más gente que una página de empresa nueva. Un post de lanzamiento (semana 1) y uno con algo aprendido o un dato útil (semana 6). No etiqueten a personas o empresas que no tengan relación con el proyecto.

### GitHub

- El README del perfil de cada uno (texto en la sección 5.4).
- Si el repositorio es público: descripción con el enlace al sitio y temas (*topics*) como `chile`, `uf`, `indicadores-economicos` y `api`.
- Listas de APIs públicas, como el repositorio `public-apis/public-apis`: solo si la API cumple sus requisitos. Lean su guía de contribución antes de proponerla (no se revisó al preparar este plan).

### Universidades

- Empiecen por su propia facultad: centro de estudiantes, ramas estudiantiles, ayudantes y profesores de cursos de programación, ciencia de datos, economía o finanzas.
- Qué ofrecer: la API para proyectos de curso (datos reales, sin clave), el widget para el sitio del centro de estudiantes, y las calculadoras de sueldo líquido y de boleta de honorarios para quienes hacen la práctica o una ayudantía con boleta.
- Ofrézcanse para una charla corta ("cómo leer tu liquidación de sueldo" o "cómo hicimos una API con archivos estáticos"). Aporta valor real y genera menciones naturales.

### Blogs, newsletters y medios

- Blogs y newsletters chilenos de finanzas personales o tecnología que publiquen indicadores o guías laborales. Un ejemplo encontrado al preparar este plan es *Invirtiendo desde Chile* (Substack). Revisen que sigan activos y que el tema calce antes de escribir.
- Sitios que hoy copian a mano la UF o el dólar: el widget les ahorra trabajo.
- Medios (economía, tecnología, regionales): solo con una historia concreta, por ejemplo "estudiantes publican una API gratuita de indicadores", "los fines de semana largos de 2027" o "ya se conoce la UF de diciembre" (cerca del día 8 de cada mes, cuando el INE publica el IPC). Las proyecciones siempre como proyecciones.
- Comunidades de desarrolladores de Chile (grupos de Python, JavaScript o datos en Meetup o Discord): búsquenlas y revisen sus reglas igual que en Reddit.

## 5. Borradores de mensajes

Adáptenlos: un mensaje personal funciona mejor que uno genérico. Los textos entre corchetes son para completar.

### 5.1 Post de LinkedIn

> Con [Marcelo/Laura] lanzamos **Lucas Claras** (https://lucasclaras.cl), un sitio gratuito con los indicadores económicos de Chile y calculadoras para el día a día: sueldo líquido, finiquito, vacaciones proporcionales, boletas de honorarios, reajuste de arriendo por IPC y crédito hipotecario.
>
> [Una o dos frases sobre por qué lo hicieron, en sus palabras.]
>
> Algunas decisiones de las que estamos contentos:
> - La UF se calcula con la fórmula oficial del Banco Central apenas el INE publica el IPC, y las pruebas automáticas la comparan con los valores publicados.
> - Los feriados se calculan con las reglas de la ley (traslados, Semana Santa, solsticio), no con una lista copiada.
> - Todo se actualiza solo, dos veces al día.
>
> Además liberamos gratis una API en JSON con la UF, el dólar, el euro, la UTM, el IPC y los feriados (https://lucasclaras.cl/api/) y un widget para mostrar la UF y el dólar en cualquier sitio (https://lucasclaras.cl/widget/).
>
> Si encuentras un error o se te ocurre una calculadora que te serviría, cuéntanos.
>
> #Chile #FinanzasPersonales #Python #DatosAbiertos

### 5.2 Post para comunidades (por ejemplo, r/chileIT)

**Título:** Hicimos una API gratuita (JSON estático) con la UF, el dólar, la UTM y los feriados de Chile

> Hola. Somos dos estudiantes de ingeniería y armamos Lucas Claras, un sitio de indicadores y calculadoras financieras para Chile. Lo comparto por si a alguien le sirven los datos en un proyecto. Aviso: el sitio es nuestro [y se financia con publicidad].
>
> Cómo funciona:
> - Python genera un sitio estático (unas 350 páginas) y archivos JSON; GitHub Actions lo actualiza dos veces al día y Cloudflare lo publica.
> - La UF de cada período se calcula con la fórmula del Banco Central apenas sale el IPC, y las pruebas la comparan con los valores oficiales.
> - Los feriados salen de las reglas de la ley (traslados, Semana Santa, solsticio para el Día de los Pueblos Indígenas).
>
> La API no pide clave y tiene CORS abierto (https://lucasclaras.cl/api/):
> - `/api/v1/indicadores.json`: UF de hoy y de mañana, dólar, euro, UTM e IPC
> - `/api/v1/uf.json`, `/api/v1/dolar.json` y `/api/v1/feriados/2027.json`
>
> Se agradece cualquier comentario, en especial si ven un error en un cálculo o algo incómodo en el formato.

Quédense a responder los comentarios durante el día. Si alguien encuentra un error, corríjanlo y avísenle en el mismo hilo.

### 5.3 Correo a blogs, medios y centros de alumnos

**Asunto:** Widget y API gratis con la UF y el dólar para [nombre del sitio]

> Hola, [nombre]:
>
> Soy [Laura/Marcelo], estudiante de [carrera] en [universidad]. Leo [nombre del sitio, newsletter o centro] y vi que [publican la UF / ayudan a estudiantes con su primer trabajo / ...].
>
> Con [compañero/a] creamos Lucas Claras (https://lucasclaras.cl), un sitio gratuito de indicadores y calculadoras para Chile. Te escribo porque quizás te sirvan dos cosas que liberamos sin costo:
>
> 1. Un **widget** que muestra la UF, el dólar y la UTM del día, se actualiza solo y se pega con dos líneas de código: https://lucasclaras.cl/widget/
> 2. Una **API en JSON**, sin registro, con la UF, el dólar, el euro, la UTM, el IPC y los feriados: https://lucasclaras.cl/api/
>
> No hay que pagar nada; solo pedimos mantener el enlace de atribución que trae el código. [Para medios: si preparan una nota sobre la UF o el IPC, con gusto les explicamos cómo se calcula.]
>
> Si no te interesa, no te vuelvo a escribir.
>
> Saludos,
> [Nombre] · [correo de contacto] · https://lucasclaras.cl

Variante para un **centro de alumnos**: reemplacen los puntos 1 y 2 por "la calculadora de sueldo líquido y la de boleta de honorarios, para quienes hacen la práctica o una ayudantía; el calendario de feriados para planificar el semestre; y la API, por si algún curso necesita datos reales para un proyecto".

Envíen cada correo uno a uno, con el nombre de la persona. Como máximo, un recordatorio una semana después.

### 5.4 Texto para el README del perfil de GitHub

```markdown
### Lucas Claras

Sitio gratuito de indicadores económicos y calculadoras financieras para Chile, hecho con [Laura/Marcelo]:
**[lucasclaras.cl](https://lucasclaras.cl)**

- Python y Jinja2 generan un sitio estático que GitHub Actions actualiza dos veces al día y Cloudflare publica.
- La UF se calcula con la fórmula oficial del Banco Central y se valida contra los valores publicados.
- [API JSON gratuita](https://lucasclaras.cl/api/) (UF, dólar, euro, UTM, IPC y feriados) y
  [widget](https://lucasclaras.cl/widget/) para mostrar los indicadores en cualquier sitio.
```

## 6. Plan semana a semana

| Semana | Foco | Acciones | Páginas a empujar |
|---|---|---|---|
| 1 (12–18 oct) | Base y círculo cercano | Lista de la semana 0. Post de LinkedIn. README de GitHub. Contarles a amigos, familia y compañeros, y pedirles que reporten errores. | Inicio, `/feriados/2027/` |
| 2 (19–25 oct) | Comunidad técnica | Post en r/chileIT (si sus reglas lo permiten) y responder comentarios. Corregir lo que reporten. | `/api/`, `/widget/` |
| 3 (26 oct–1 nov) | Universidades | 3 a 5 correos personalizados a su centro de estudiantes, ayudantes y profesores. Ofrecer una charla. | `/calculadoras/sueldo-liquido/`, `/calculadoras/boleta-honorarios/`, `/feriados/2027/` |
| 4 (2–8 nov) | Dato del mes | El IPC de octubre se publica cerca del 8 de noviembre y deja fija la UF hasta el 9 de diciembre: post corto con ese dato. Primera revisión en Search Console. | `/uf/`, `/uf/proyeccion/`, `/calculadoras/reajuste-arriendo-ipc/` |
| 5 (9–15 nov) | Blogs y newsletters | 5 correos personalizados; recordatorio a quienes no respondieron en la semana 3. | `/widget/`, `/api/` |
| 6 (16–22 nov) | Medios y segundo post | Proponer una historia concreta a 2 o 3 medios. Segundo post de LinkedIn con algo aprendido (sin inflar cifras). | `/feriados/2027/`, `/dolar/` |
| 7 (23–29 nov) | Fin de año laboral | Compartir las calculadoras de finiquito y vacaciones donde alguien las necesite (contratos que terminan en diciembre, vacaciones de verano). | `/calculadoras/finiquito/`, `/calculadoras/vacaciones-proporcionales/` |
| 8 (30 nov–6 dic) | Balance | Revisar métricas y la planilla: qué canal trajo visitas y enlaces. Planificar las 8 semanas siguientes (sueldo mínimo de enero, fines de semana largos de Navidad y Año Nuevo, Operación Renta). | `/feriados/` |

En este período no hay fines de semana largos (el 31 de octubre cae sábado y el 1 de noviembre, domingo). Los próximos son del 25 al 27 de diciembre y del 1 al 3 de enero de 2027.

> **`/feriados/2027/` es una dirección permanente:** sigue existiendo después del 1 de enero de 2027 (desde ese día indica a Google que la página principal del año en curso es `/feriados/`). Pueden usarla sin miedo en enlaces que deben durar.

## 7. Calendario de temporadas

Publiquen o compartan cada contenido una o dos semanas antes de que suba la búsqueda. Las fechas de los fines de semana largos salen del mismo cálculo de feriados del sitio (`lucas/feriados.py`). Las marcadas "por confirmar" no se pudieron verificar al preparar este plan: revísenlas en la fuente oficial cada año.

| Cuándo | Qué pasa | Páginas a empujar |
|---|---|---|
| Cada mes, cerca del día 8 | El INE publica el IPC y queda fija la UF hasta el día 9 del mes siguiente | `/uf/`, `/uf/proyeccion/`, archivo mensual de la UF, `/ipc/`, `/calculadoras/reajuste-arriendo-ipc/` |
| Octubre | Se buscan los feriados del año siguiente | `/feriados/2027/` (dirección permanente; desde enero, `/feriados/` muestra el año en curso) |
| Noviembre (por confirmar) | Black Friday: compras en tiendas extranjeras | `/dolar/` y las páginas de montos ("100 dólares en pesos") |
| Diciembre y enero | Términos de contrato y vacaciones; fines de semana largos del 25 al 27 de diciembre y del 1 al 3 de enero | `/calculadoras/finiquito/`, `/calculadoras/vacaciones-proporcionales/`, `/feriados/` |
| 1 de enero de 2027 | Reajuste del sueldo mínimo (Ley 21.830). En años anteriores también hubo reajustes en mayo | `/sueldo-minimo/`, `/calculadoras/sueldo-liquido/`, páginas de sueldo líquido por monto. Actualicen `parametros/chile.yaml` apenas se publique el monto |
| Abril | Operación Renta del SII | `/calculadoras/boleta-honorarios/`, `/impuesto-unico/`, `/utm/` (UTA). Buen momento para escribir a centros de estudiantes: ayudantes y practicantes con boletas de honorarios |
| Liquidaciones de todo el año; abril y mayo (por confirmar) | Gratificación legal: muchas empresas la pagan mes a mes con tope anual de 4,75 ingresos mínimos; la anual se calcula con las utilidades del año, que se conocen después de la Operación Renta | `/calculadoras/sueldo-liquido/` (opción de gratificación), `/sueldo-minimo/` (tope de gratificación) |
| Fines de semana largos de 2027 | 26–28 de marzo (Semana Santa), 21–23 de mayo, 19–21 de junio, 26–28 de junio, 16–18 de julio, 17–19 de septiembre, 9–11 de octubre y 30 de octubre–1 de noviembre | `/feriados/`, `/calculadoras/dias-habiles/` |
| Junio (por confirmar) | CyberDay, organizado por la Cámara de Comercio de Santiago | `/dolar/` y páginas de montos, `/euro/` |
| Agosto de 2027 | Sube el aporte del empleador por la reforma de pensiones (ya cargado en el sitio) | `/calculadoras/sueldo-liquido/` (costo para el empleador): pymes y contadores |
| Septiembre | Fiestas Patrias: en 2027, del viernes 17 al domingo 19 (el 17 es feriado por la Ley 20.983). Aguinaldos de Fiestas Patrias | `/feriados/`, `/calculadoras/sueldo-liquido/`, `/dolar/` (viajes) |
| Varias fechas (por confirmar) | Pago de bonos del Estado: Aporte Familiar Permanente (ex Bono Marzo), Bono de Invierno y aguinaldos de Fiestas Patrias y Navidad para pensionados | No hay páginas propias. Si las crean, que sean guías con montos y fechas verificados en ChileAtiende cada año, enlazadas a las calculadoras |

## 8. Cómo medir

### En Search Console

- **Rendimiento → Resultados de búsqueda.** Comparen los últimos 28 días con los 28 anteriores. Filtros útiles:
  - *Página* que contiene `/widget/` o `/api/`: impresiones y consultas que llegan a esas páginas.
  - *Consulta* que contiene `lucas claras`: búsquedas de la marca, la mejor señal de que la gente ya conoce el sitio.
  - Cada página de temporada (por ejemplo, `/feriados/2027/`) antes y después de compartirla.
- **Enlaces.** El informe de enlaces externos muestra qué sitios enlazan, qué páginas reciben más enlaces y con qué texto. Tarda semanas en actualizarse y no muestra todos los enlaces.
- **Indexación → Páginas** e **Inspección de URL**: confirmen que `/widget/` y `/api/` estén indexadas y pidan la indexación al publicarlas.
- **Seguridad y acciones manuales**: debe indicar que no hay problemas. Si alguna vez aparece una acción por enlaces artificiales, detengan todo lo que estén haciendo y revisen esta guía.

Bing Webmaster Tools también tiene un informe de enlaces entrantes; revísenlo una vez al mes.

### Fuera de Search Console

- **Cloudflare Web Analytics**, en las fuentes de referencia (*referrers*): de qué sitios llegan visitas, incluidos los clics en el enlace del widget.
- **La planilla de seguimiento**: cada publicación, correo y respuesta. Anoten los sitios que usan el widget o la API (los verán en los referrers, en Search Console o porque les escriben).
- **Alertas de Google** (google.com/alerts) con "Lucas Claras" y "lucasclaras.cl", para enterarse de menciones.

### Metas orientativas para la semana 8

No son promesas, sirven para saber si van bien:

| Indicador | Meta |
|---|---|
| `/widget/` y `/api/` indexadas | Sí |
| Sitios reales que usan el widget o la API | 3 o más |
| Dominios distintos que enlazan (con o sin `nofollow`) | 5 o más |
| Búsquedas de la marca en Search Console | Las primeras apariciones |
| Errores reportados y corregidos | Todos los que lleguen, en menos de una semana |

## 9. Lo que no vamos a hacer

- Comprar, vender o intercambiar enlaces ("te enlazo si me enlazas"), ni pagar artículos o notas con enlaces sin `rel="sponsored"`.
- Pedir que quiten el `nofollow` del widget o que usen textos de enlace con palabras clave ("valor UF hoy").
- Ocultar enlaces en el widget o agregarle enlaces desde el script.
- Dejar comentarios en blogs o foros solo para poner el enlace, o firmas con enlaces.
- Usar directorios de baja calidad, granjas o redes de blogs, ni servicios que venden "backlinks".
- Crear cuentas falsas, pedir votos, publicar el mismo mensaje en muchas comunidades o enviar correos masivos.
- Generar páginas en masa solo para posicionar.

Si alguien les ofrece enlaces a cambio de dinero o de otro enlace, respondan que no.

## 10. Fuentes y pendientes

- [Políticas de spam para la Búsqueda web de Google](https://developers.google.com/search/docs/essentials/spam-policies) (sección de spam de enlaces).
- [«A reminder about widget links»](https://developers.google.com/search/blog/2016/09/a-reminder-about-widget-links), Google Search Central, septiembre de 2016.
- Anuncio de Google sobre `nofollow` como sugerencia, septiembre de 2019 (vigente para el rastreo desde el 1 de marzo de 2020).
- [Cabeceras de los archivos estáticos en Cloudflare Workers](https://developers.cloudflare.com/workers/static-assets/headers/): todas las reglas de `_headers` que calzan con una ruta se aplican juntas.
- Tamaño de los subreddits: [GummySearch](https://gummysearch.com/r/chile/) (sitio de terceros).
- Fines de semana largos: `lucas/feriados.py`. Sueldo mínimo: `parametros/chile.yaml` (Ley 21.830).

Pendiente de verificar antes de usar (no se pudo al preparar este plan): las reglas vigentes de cada comunidad, las fechas de CyberDay y Black Friday de cada año, el calendario de pago de bonos (ChileAtiende), el momento de pago de la gratificación anual (Dirección del Trabajo) y los requisitos de `public-apis/public-apis`.
