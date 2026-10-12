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

- `sitio.url`: la URL final (por ejemplo, `https://lucasclaras.cl`).
- `sitio.correo_contacto`: un correo para el sitio. Creen uno nuevo, por ejemplo `contacto.lucasclaras@gmail.com`. Google AdSense valora que exista un contacto.
- `sitio.autores`: cómo quieren presentarse en "Quiénes somos" (o déjenlo vacío).
- Si quieren otro nombre para el sitio, cámbienlo aquí y regeneren las imágenes con `python herramientas/generar_imagenes.py`.

## Paso 3: Comprar el dominio

1. Elijan un nombre corto y fácil de recordar. Ideas: `lucasclaras.cl`, `cuentasclaras.cl`, `calculalucas.cl`, `indicadoreshoy.cl`. Revisen la disponibilidad en [nic.cl](https://www.nic.cl).
2. Regístrenlo en NIC Chile (necesitan RUT; cuesta unos $10.000 al año). Activen la renovación automática para no perderlo.

## Paso 4: Publicar en Cloudflare (gratis, permite uso comercial)

> ¿Por qué no GitHub Pages? Sus términos dicen que no está pensado para "un negocio en línea". Para un sitio con publicidad, Cloudflare es la opción segura y también es gratis.

1. **Crear la cuenta:** regístrense en [cloudflare.com](https://dash.cloudflare.com/sign-up) (plan Free).
2. **Agregar el dominio:** *Add a domain* → escriban `lucasclaras.cl` → plan **Free**. Cloudflare les mostrará **dos servidores de nombres** (nameservers).
3. **Apuntar el dominio a Cloudflare:** en NIC Chile, en la administración del dominio, reemplacen los servidores DNS por los dos de Cloudflare. Puede tardar desde minutos hasta unas horas en activarse.
4. **Crear un token de API:** en Cloudflare, *My Profile → API Tokens → Create Token* → plantilla **Edit Cloudflare Workers** → elijan su cuenta y su zona → *Create Token*. Copien el token (se muestra una sola vez).
5. **Copiar el Account ID:** aparece en la página de inicio de *Workers & Pages* (columna derecha).
6. **Configurar GitHub:** en su repositorio, *Settings → Secrets and variables → Actions*:
   - Pestaña **Secrets** → *New repository secret*:
     - `CLOUDFLARE_API_TOKEN` = el token del punto 4
     - `CLOUDFLARE_ACCOUNT_ID` = el Account ID
   - Pestaña **Variables** → *New repository variable*:
     - `DESTINO` = `cloudflare`
7. **Publicar por primera vez:** pestaña *Actions* → **Actualizar y publicar** → *Run workflow*. La primera vez descarga datos desde 2018 y demora unos minutos. Debe terminar en verde ✅. Se crea el Worker `lucas-claras` con una dirección `lucas-claras.<algo>.workers.dev`.
8. **Conectar el dominio:** Cloudflare → *Workers & Pages* → `lucas-claras` → *Settings* → *Domains & Routes* → *Add* → *Custom domain* → `lucasclaras.cl`. Repitan con `www.lucasclaras.cl` si quieren que también funcione.
9. **Analítica gratis y sin cookies:** Cloudflare → *Web Analytics* → agreguen el sitio. Si les entrega un token, cópienlo en `config.yaml` (`analitica.cloudflare_web_analytics_token`).
10. **Avisar a Bing y Yandex automáticamente:** Cloudflare → *Caching → Configuration* → activen **Crawler Hints** (usa IndexNow).

<details>
<summary>Alternativa: GitHub Pages (para pruebas, requiere repositorio público o GitHub Pro)</summary>

1. *Settings → Pages → Build and deployment → Source:* **GitHub Actions**.
2. Variable `DESTINO` = `github-pages`.
3. En `config.yaml`, `url: https://mpalma325.github.io/lucas-claras` (o su dominio si lo configuran en *Settings → Pages → Custom domain*).
4. *Actions → Actualizar y publicar → Run workflow*.

Con el GitHub Student Developer Pack tienen GitHub Pro gratis, que permite Pages en repositorios privados.
</details>

Desde ahora el sitio se actualiza solo dos veces al día. 🎉

## Paso 5: Registrar el sitio en Google y Bing

1. **Google Search Console** ([search.google.com/search-console](https://search.google.com/search-console)): *Agregar propiedad* → tipo **Dominio** → `lucasclaras.cl`. Google les pedirá un registro TXT: agréguenlo en Cloudflare → *DNS → Records* → *Add record* (tipo TXT).
2. En Search Console → *Sitemaps* → envíen `https://lucasclaras.cl/sitemap.xml`.
3. Usen *Inspección de URLs* para pedir la indexación de las páginas más importantes: inicio, `/uf/`, `/calculadoras/sueldo-liquido/`, `/feriados/`, `/uf/proyeccion/`.
4. **Bing Webmaster Tools** ([bing.com/webmasters](https://www.bing.com/webmasters)): *Importar desde Google Search Console*.

## Paso 6: Conseguir las primeras visitas y enlaces

Google confía más en un sitio nuevo cuando otros sitios lo enlazan. Sin spam:

- Compártanlo con amigos, familia y compañeros, y en sus perfiles de LinkedIn y GitHub (¡el README del perfil de Marcelo es un buen lugar!).
- Respondan preguntas reales en comunidades (por ejemplo, foros o subreddits chilenos de finanzas personales) enlazando la calculadora cuando de verdad sirva.
- Ofrezcan las calculadoras a centros de alumnos, oficinas de práctica o asociaciones que publiquen guías para trabajadores o estudiantes.

## Paso 7: Google AdSense 💰

Postulen cuando el sitio lleve algunas semanas en línea y ya tenga páginas indexadas (lo ven en Search Console).

1. Requisitos: ser mayor de 18 años, tener contenido original, política de privacidad (✅ ya está en `/privacidad/`) y página de contacto (✅ `/contacto/`, con el correo del paso 2).
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

## Paso 8: Referidos 💰

1. Inscríbanse en los programas que les parezcan confiables y útiles para sus lectores. Ideas: Fintual (referidos), Racional, Global66 (programa de afiliados), Mercado Libre Afiliados.
2. **Lean las bases:** algunos programas solo permiten invitar a conocidos y no publicar el enlace en un sitio web.
3. Agréguenlos en `config.yaml`, en `monetizacion.afiliados`, indicando en qué secciones mostrarlos. Hay un ejemplo comentado en el archivo. El sitio siempre muestra el aviso de que son enlaces de referidos.

## Paso 9 (opcional): Fuente de datos de respaldo

Si mindicador.cl deja de responder, el sitio puede usar la API oficial de la CMF:

1. Pidan una clave gratuita en [api.cmfchile.cl](https://api.cmfchile.cl).
2. Guárdenla como secreto `CMF_API_KEY` en GitHub (*Settings → Secrets and variables → Actions*).

## Lista final

- [ ] El workflow **Actualizar y publicar** termina en verde.
- [ ] `https://lucasclaras.cl` muestra el sitio, con el candado HTTPS.
- [ ] `https://lucasclaras.cl/sitemap.xml` y `/robots.txt` responden.
- [ ] Sitemap enviado a Search Console y a Bing.
- [ ] Correo de contacto configurado.
- [ ] AdSense postulado (cuando corresponda).
- [ ] Referidos configurados (cuando corresponda).
- [ ] Leyeron [MANTENCION.md](MANTENCION.md) y saben qué hacer cuando llegue un correo de GitHub con un workflow en rojo.
