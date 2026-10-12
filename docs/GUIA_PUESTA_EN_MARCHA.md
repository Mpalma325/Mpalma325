# Guía de puesta en marcha

Sigan estos pasos en orden. Tiempo total: entre 2 y 4 horas, más la espera de aprobaciones (dominio, Google). Los pasos marcados con 💰 son los que generan ingresos.

---

## Paso 0: Mover el código a su propio repositorio

Sigan las instrucciones del [README](../README.md#mover-a-un-repositorio-propio). El repositorio puede ser **privado** si publican en Cloudflare (recomendado).

## Paso 1: Probar el sitio en su computador

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest                   # todas las pruebas deberían pasar
python -m lucas construir --demo   # datos ficticios
python -m lucas servir             # http://localhost:8000
```

Revisen las páginas y los textos. Si algo no les gusta, las plantillas están en `plantillas/` y los estilos en `estaticos/css/estilos.css`.

## Paso 2: Personalizar `config.yaml`

- `sitio.url`: la URL final (por ejemplo, `https://sacalacuenta.cl`).
- `sitio.correo_contacto`: un correo para el sitio. Creen uno nuevo, por ejemplo `contacto.sacalacuenta@gmail.com`. Google AdSense valora que exista un contacto.
- `sitio.autores`: cómo quieren presentarse en "Quiénes somos" (o déjenlo vacío).
- `sitio.equipo`: **muy recomendado.** En los sitios de finanzas, Google y AdSense valoran saber quién está detrás. Completen sus datos reales:

  ```yaml
    equipo:
      - nombre: Nombre Apellido
        rol: Cofundadora · datos y fórmulas
        descripcion: Estudiante de ingeniería. Revisa las fórmulas y los parámetros legales.
        enlace: https://www.linkedin.com/in/su-perfil/     # opcional: LinkedIn o GitHub
      - nombre: Nombre Apellido
        rol: Cofundador · negocio
        descripcion: Estudiante de ingeniería. Se encarga de métricas, AdSense y alianzas.
        enlace: https://github.com/su-usuario
    redes: []          # perfiles públicos del sitio (no personales), con https://
    repositorio: ""    # solo si publican el código
  ```

  Aparecen como tarjetas en `/acerca/` y en los datos estructurados de la organización. Corran `python -m pytest`: una prueba revisa que cada persona tenga nombre y que los enlaces empiecen con `https://`.
- Si quieren otro nombre para el sitio, cámbienlo aquí y regeneren las imágenes con `python herramientas/generar_imagenes.py`.

## Paso 3: Comprar el dominio

1. **Ojo: `sacalacuenta.cl` ya está en uso** por otro sitio chileno de calculadoras, así que antes de lanzar hay que elegir otro nombre. Revisen en [nic.cl](https://www.nic.cl) que el dominio nuevo esté libre, cámbienlo en `config.yaml` (`sitio.nombre` y `sitio.url`), regeneren las imágenes con `python herramientas/generar_imagenes.py` (toma el nombre de `config.yaml`) y busquen el nombre antiguo en el repositorio (`grep -rn "sacalacuenta" .`).
2. Regístrenlo en NIC Chile (necesitan RUT; cuesta unos $10.000 al año). Activen la renovación automática para no perderlo.

## Paso 4 (recomendado): Clave gratuita de la API de la CMF (5 minutos)

El sitio se alimenta solo, sin claves:

- **SII** (oficial): UF, UTM e IPC.
- **findic.cl** (servicio gratuito no oficial): dólar del día, euro y otros indicadores. El SII publica el dólar con unos 10 días de atraso y no publica el euro.

Como findic.cl no es oficial, conviene agregar el respaldo oficial de la Comisión para el Mercado Financiero (CMF):

1. Pidan una clave en [api.cmfchile.cl](https://api.cmfchile.cl) (formulario con su correo).
2. Guárdenla en GitHub como secreto `CMF_API_KEY` (*Settings → Secrets and variables → Actions → New repository secret*).
3. Para comprobar que funciona, corran el workflow **Pruebas** y revisen el paso *Diagnosticar fuentes de datos*: deben aparecer líneas `OK api.cmfchile.cl`.

## Paso 5: Publicar en Cloudflare (gratis, permite uso comercial)

> ¿Por qué no GitHub Pages? Sus términos dicen que no está pensado para "un negocio en línea". Para un sitio con publicidad, Cloudflare es la opción segura y también es gratis.

1. **Crear la cuenta:** regístrense en [cloudflare.com](https://dash.cloudflare.com/sign-up) (plan Free).
2. **Agregar el dominio:** *Add a domain* → escriban `sacalacuenta.cl` → plan **Free**. Cloudflare les mostrará **dos servidores de nombres** (nameservers).
3. **Apuntar el dominio a Cloudflare:** en NIC Chile, en la administración del dominio, reemplacen los servidores DNS por los dos de Cloudflare. Puede tardar desde minutos hasta unas horas en activarse.
4. **Crear un token de API:** en Cloudflare, *My Profile → API Tokens → Create Token* → plantilla **Edit Cloudflare Workers** → elijan su cuenta y su zona → *Create Token*. Copien el token (se muestra una sola vez).
5. **Copiar el Account ID:** aparece en la página de inicio de *Workers & Pages* (columna derecha).
6. **Configurar GitHub:** en su repositorio, *Settings → Secrets and variables → Actions*:
   - Pestaña **Secrets** → *New repository secret*:
     - `CLOUDFLARE_API_TOKEN` = el token del punto 4
     - `CLOUDFLARE_ACCOUNT_ID` = el Account ID
   - Pestaña **Variables** → *New repository variable*:
     - `DESTINO` = `cloudflare`
7. **Publicar por primera vez:** pestaña *Actions* → **Actualizar y publicar** → *Run workflow*. La primera vez descarga datos desde 2018 y demora un par de minutos. Debe terminar en verde ✅. Se crea el Worker `saca-la-cuenta` con una dirección `saca-la-cuenta.<algo>.workers.dev`.
8. **Conectar el dominio:** Cloudflare → *Workers & Pages* → `saca-la-cuenta` → *Settings* → *Domains & Routes* → *Add* → *Custom domain* → `sacalacuenta.cl`. **No agreguen `www` como dominio del Worker**: servirían el mismo sitio dos veces. Para `www`, sigan el complemento B más abajo.
9. **Analítica gratis y sin cookies:** Cloudflare → *Web Analytics* → agreguen el sitio. Si les entrega un token, cópienlo en `config.yaml` (`analitica.cloudflare_web_analytics_token`). Prefieran esta opción a Google Analytics: las calculadoras guardan los montos en la parte `#` de la dirección para poder compartirlos, y si algún día activan Google Analytics 4 deben desactivar en su "medición mejorada" los cambios de página basados en el historial del navegador, para no enviar esos montos a Google.
10. **Avisar a Bing y Yandex automáticamente:** Cloudflare → *Caching → Configuration* → activen **Crawler Hints** (usa IndexNow).

<details>
<summary>Alternativa: GitHub Pages (para pruebas, requiere repositorio público o GitHub Pro)</summary>

1. *Settings → Pages → Build and deployment → Source:* **GitHub Actions**.
2. Variable `DESTINO` = `github-pages`.
3. En `config.yaml`, `url: https://mpalma325.github.io/saca-la-cuenta` (o su dominio si lo configuran en *Settings → Pages → Custom domain*).
4. *Actions → Actualizar y publicar → Run workflow*.

Con el GitHub Student Developer Pack tienen GitHub Pro gratis, que permite Pages en repositorios privados.
</details>

Desde ahora el sitio se actualiza solo dos veces al día. 🎉

### Complemento A: correo de contacto gratis con Cloudflare Email Routing

Con el dominio ya en Cloudflare pueden tener `contacto@sacalacuenta.cl` sin pagar: Cloudflare recibe los correos y los reenvía a su correo personal. **AdSense espera que el sitio tenga un contacto.**

1. En Cloudflare, entren a **Email Routing** dentro del dominio (según el panel aparece como *Email Service → Email Routing* o *Email → Email Routing*).
2. **Destination addresses → Add:** escriban su correo personal y confírmenlo con el mensaje de verificación que les llega. Sin confirmar, la regla queda desactivada.
3. Activen Email Routing para `sacalacuenta.cl`. Cloudflare agrega solo los registros MX y el TXT de SPF. Si el dominio tenía otro correo, hay que quitar esos MX: no pueden convivir.
4. **Routing rules → Create address:** en la dirección escriban `contacto`; en la acción elijan **Send to an email** y su correo verificado.
5. Prueben escribiendo desde otra cuenta (revisen también la carpeta de spam).
6. En `config.yaml`, pongan `correo_contacto: "contacto@sacalacuenta.cl"` y hagan commit y push. El correo aparece en Contacto, Privacidad, Quiénes somos y en los datos estructurados.

> Email Routing solo recibe y reenvía: sus respuestas saldrán desde su correo personal.

### Complemento B: que `www` lleve al dominio sin `www`

1. En **DNS → Records**, creen un registro para `www` con la nube naranja (*Proxied*), por ejemplo un `CNAME` `www` → `sacalacuenta.cl`.
2. En **Rules → Redirect Rules → Create rule**, elijan la plantilla **Redirect from WWW to root** (o configúrenla a mano: *Request URL* `https://www.*`, *Target URL* `https://${1}`, código **301**, *Preserve query string* activado).
3. Activen **SSL/TLS → Edge Certificates → Always Use HTTPS**.
4. Prueben que `https://www.sacalacuenta.cl/uf/?x=1` lleve a `https://sacalacuenta.cl/uf/?x=1`.

### Complemento C: apaguen `workers.dev` cuando el dominio funcione

Cuando `https://sacalacuenta.cl` ya muestre el sitio, apaguen la dirección `saca-la-cuenta.<cuenta>.workers.dev` y las URL de vista previa, para que no queden copias del sitio que Google pueda indexar. En `wrangler.jsonc`, agreguen:

```jsonc
  "workers_dev": false,
  "preview_urls": false,
```

Hagan commit y push: el siguiente despliegue las apaga. **Háganlo solo después de conectar el dominio**; si no, el sitio queda sin dirección pública.

## Paso 6: Registrar el sitio en Google y Bing

1. **Google Search Console** ([search.google.com/search-console](https://search.google.com/search-console)): *Agregar propiedad* → tipo **Dominio** → `sacalacuenta.cl`. Google les pedirá un registro TXT: agréguenlo en Cloudflare → *DNS → Records* → *Add record* (tipo TXT).
2. En Search Console → *Sitemaps* → envíen `https://sacalacuenta.cl/sitemap.xml`.
3. Usen *Inspección de URLs* para pedir la indexación de las páginas más importantes: inicio, `/uf/`, `/calculadoras/sueldo-liquido/`, `/feriados/`, `/uf/proyeccion/`.
4. **Bing Webmaster Tools** ([bing.com/webmasters](https://www.bing.com/webmasters)): *Importar desde Google Search Console*.

## Paso 7: Conseguir las primeras visitas y enlaces

Google confía más en un sitio nuevo cuando otros sitios lo enlazan. El plan detallado de las primeras 8 semanas, con borradores de mensajes y un calendario de temporadas, está en [LANZAMIENTO.md](LANZAMIENTO.md). Lo esencial, sin spam:

- Ofrezcan el **widget gratuito** (`/widget/`) y la **API de indicadores** (`/api/`) a blogs, medios y centros de alumnos: cada sitio que los use los enlaza.

- Compártanlo con amigos, familia y compañeros, y en sus perfiles de LinkedIn y GitHub (¡el README del perfil de Marcelo es un buen lugar!).
- Respondan preguntas reales en comunidades (por ejemplo, foros o subreddits chilenos de finanzas personales) enlazando la calculadora cuando de verdad sirva.
- Ofrezcan las calculadoras a centros de alumnos, oficinas de práctica o asociaciones que publiquen guías para trabajadores o estudiantes.

## Paso 8: Google AdSense 💰

Postulen cuando el sitio lleve algunas semanas en línea y ya tenga páginas indexadas (lo ven en Search Console).

1. Requisitos: ser mayor de 18 años, tener contenido original (✅ calculadoras y 15 guías), política de privacidad (✅ `/privacidad/`) y página de contacto (✅ `/contacto/`, **con el correo del complemento A**). Antes de postular, completen también `sitio.equipo` (paso 2): "Quiénes somos" con personas reales ayuda mucho en un sitio de finanzas.
   - Detalles verificados de AdSense en Chile (umbral de pago, PIN, formulario W-8BEN, formas de pago) en [MONETIZACION.md](MONETIZACION.md#3-publicidad).
2. Entren a [adsense.google.com](https://adsense.google.com), creen la cuenta y agreguen el sitio.
3. Copien su ID de editor (`ca-pub-XXXXXXXXXXXXXXXX`) y en `config.yaml` pongan:

   ```yaml
   monetizacion:
     adsense:
       activo: true
       publisher_id: "ca-pub-XXXXXXXXXXXXXXXX"
   ```

   Hagan commit y push: el sitio incluirá el código de AdSense y el archivo `ads.txt` automáticamente.
4. En AdSense, pidan la revisión del sitio. Puede tardar desde días hasta 2–4 semanas.
5. Cuando lo aprueben:
   - Activen los **anuncios automáticos** (Auto ads).
   - En *Privacidad y mensajes*, activen el mensaje de consentimiento para visitantes de Europa, Reino Unido y Suiza (lo exige Google).
6. Pagos: AdSense paga cuando se acumulan CLP 60.000 (cuenta en pesos) o US$100. Completen sus datos tributarios y de pago en la cuenta.

> Si los rechazan por "contenido de poco valor", esperen a tener más páginas indexadas y tráfico, y vuelvan a postular. Es muy común con sitios nuevos.

## Paso 9: Referidos 💰

1. Revisen [MONETIZACION.md](MONETIZACION.md): tiene los programas verificados (Fintual, Racional, Global66 Afiliados, ComparaOnline vía Awin...), los descartados y por qué (por ejemplo, Buda.com prohíbe publicar el enlace en sitios web) y **fragmentos listos para pegar** en `config.yaml`.
2. **Pidan por escrito la confirmación** de que pueden publicar el enlace en un sitio web cuando las bases no lo digan (Fintual, Racional). Guarden esa respuesta.
3. Agreguen los programas en `config.yaml`, en `monetizacion.afiliados`, con las secciones donde mostrarlos (en las guías, la sección es la categoría de la guía). El sitio siempre muestra el aviso de que son enlaces de referidos.
4. Antes de recibir el primer pago, ordenen los impuestos con un contador (ver la sección tributaria de MONETIZACION.md).

## Lista final

- [ ] Secreto `CMF_API_KEY` configurado (respaldo oficial del dólar y el euro).
- [ ] El workflow **Actualizar y publicar** termina en verde.
- [ ] `https://sacalacuenta.cl` muestra el sitio, con el candado HTTPS.
- [ ] `https://sacalacuenta.cl/sitemap.xml` y `/robots.txt` responden.
- [ ] Sitemap enviado a Search Console y a Bing.
- [ ] Correo de contacto funcionando (`contacto@sacalacuenta.cl`) y puesto en `correo_contacto`.
- [ ] `sitio.equipo` completo ("Quiénes somos" con personas reales).
- [ ] `www` redirige al dominio sin `www`; `workers_dev` y `preview_urls` en `false`.
- [ ] AdSense postulado (cuando corresponda).
- [ ] Referidos configurados (cuando corresponda).
- [ ] Leyeron [MANTENCION.md](MANTENCION.md) y saben qué hacer cuando llegue un correo de GitHub con un workflow en rojo.
