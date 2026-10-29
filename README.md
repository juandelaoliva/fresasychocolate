# Fresas y Chocolate · web

**Español** · [English](README.en.md)

Web de [Fresas y Chocolate](https://fresasychocolate.com/), tienda de fresas con chocolate en la
calle Espoz y Mina, 38 (Salamanca). Es una web estática de una sola página que se genera a partir
de archivos de contenido. El contenido (precios, horario, textos, fotos, vídeos, preguntas) se
edita desde **Pages CMS** y GitHub publica la web sola en un par de minutos.

```
Pages CMS → content/*.yml en GitHub → GitHub Actions ejecuta build.py → GitHub Pages
```

- **Si editas contenido**, lee el [manual para editores](docs/manual-editores.md). No hace falta
  nada de lo que sigue.
- **Si mantienes la web** (código, diseño, publicación), este README es para ti.

## Índice

- [Trabajar en local](#trabajar-en-local)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Cómo se genera la web (build.py)](#cómo-se-genera-la-web-buildpy)
- [Publicación](#publicación)
- [Pages CMS](#pages-cms)
- [Diseño y secciones](#diseño-y-secciones)
- [El hero](#el-hero)
- [Cambiar el vídeo del hero](#cambiar-el-vídeo-del-hero)
- [SEO y GEO](#seo-y-geo)
- [Problemas conocidos y soluciones](#problemas-conocidos-y-soluciones)
- [Pendiente](#pendiente)

## Trabajar en local

Necesitas Python 3.9 o superior y, solo si hay vídeos que convertir, `ffmpeg`.

```
pip install -r requirements.txt
python3 build.py          # genera _site/
open _site/index.html     # en macOS; en otros sistemas, abre el archivo con el navegador
```

Cada cambio en `content/`, `src/`, `css/` o `js/` necesita volver a ejecutar `build.py` y recargar
la página. `_site/` no se guarda en el repositorio.

`SITE_URL=https://otro-dominio/ python3 build.py` cambia el dominio que se usa en la URL canónica,
el sitemap, `llms.txt` y los datos para Google. Por defecto es https://fresasychocolate.com/.

Antes de hacer `git push`, haz `git pull`: lo que se guarda desde Pages CMS llega a `main` como
commits y es fácil que haya cambios nuevos.

## Estructura del repositorio

```
content/*.yml              el contenido: lo que se edita desde Pages CMS (un archivo por sección)
src/index.html.j2          plantilla de la página (Jinja2)
src/llms.txt.j2            ficha de la tienda para asistentes de IA
src/sitemap.xml.j2         sitemap
src/robots.txt.j2          robots.txt
src/svg/                   logos, símbolo, sello, flecha y ola (van en línea en la página)
build.py                   genera _site/ a partir de content/ y src/
requirements.txt           dependencias de Python
.pages.yml                 formularios de Pages CMS
.github/workflows/         publicación automática en GitHub Pages
css/styles.css             estilos, mobile first; paleta de marca en :root
js/hero.js                 animación del hero ligada al scroll
js/menu.js                 menú hamburguesa
js/vaso.js                 "Monta tu vaso": suma el precio y los alérgenos de lo elegido
js/videos.js               vídeos de la tienda: cargan al acercarse y solo se reproducen en pantalla
js/carrusel.js             galerías deslizables: flechas para pasar fotos con ratón
js/faq.js                  preguntas frecuentes: abren y cierran con animación
assets/hero/               el vídeo del hero en fotogramas WebP, póster y manifest
assets/img/                fotos (las que se suben desde el CMS también van aquí)
assets/video/              vídeos de la tienda y su imagen fija
assets/logo/               logos SVG limpios (fill = currentColor), símbolo de la fresa y sello
assets/icons/              favicon e icono para la pantalla de inicio del iPhone
assets/og/                 imagen para compartir y logo cuadrado para Google
scripts/extraer-frames.sh  regenera los fotogramas del hero a partir de un vídeo
docs/                      manual para editores
```

`content/` tiene estos archivos:

| Archivo | Qué contiene |
|---|---|
| `tienda.yml` | Nombre, dirección, coordenadas, Google Maps, Instagram, teléfono, email y horario |
| `portada.yml` | Lema del hero, título y descripción para Google, descripción de la tienda para IA |
| `carta.yml` | Monta tu vaso: vaso, cremas, grupos de toppings, precios y alérgenos |
| `bebidas.yml` | Galería y carta de bebidas |
| `encargos.yml` | Galería, bandejas y cómo encargar |
| `historia.yml` | Las fresas, el chocolate y quiénes somos |
| `instagram.yml` | Fotos del mosaico "Del día a día" |
| `preguntas.yml` | Preguntas frecuentes escritas a mano |

## Cómo se genera la web (build.py)

`build.py` lee `content/*.yml`, comprueba los datos, rellena las plantillas de `src/` y escribe
el resultado en `_site/` junto con `css/`, `js/` y `assets/`.

**Comprobaciones.** Si algo no cuadra, se para con un mensaje en español y no genera nada, así
nunca se publica una web rota. Comprueba, entre otras cosas:
- que estén los campos imprescindibles (lista `OBLIGATORIOS`);
- que los precios sean números; se aceptan `1,70`, `1.70`, `12` o `4,80 €`;
- que los alérgenos sean de la lista de la carta (`ALERGENOS`) y los días de la semana sean válidos;
- que las horas tengan el formato `14:00`;
- que todas las fotos y vídeos existan y tengan descripción (texto alternativo).

**Fotos.** Las WebP de hasta 1600 px se publican tal cual. El resto (JPG, PNG, HEIC del iPhone…)
se convierte a WebP de 1600 px de ancho como máximo, y el original no se publica.

**Vídeos.** Los MP4 de hasta 12 MB se publican tal cual. El resto (MOV del iPhone, MP4 pesados…)
se convierte con `ffmpeg` a un MP4 sin sonido de 720 px de ancho como máximo. Si un vídeo no
tiene imagen fija, se saca un fotograma del propio vídeo.

**Preguntas automáticas.** Las preguntas de dirección, horario, precio del vaso, encargos y bebidas
se escriben solas a partir de `tienda.yml`, `carta.yml`, `encargos.yml` y `bebidas.yml`, así
nunca contradicen la carta. Las demás vienen de `preguntas.yml`. En las respuestas se pueden
poner enlaces con el formato `[texto](https://…)`.

**Datos para Google y para IA.** Con los mismos datos genera el JSON-LD (tienda, carta con
precios, web y preguntas frecuentes), `llms.txt`, `sitemap.xml` y `robots.txt`. Un precio se
cambia en un sitio y se actualiza en todas partes.

## Publicación

`.github/workflows/publicar.yml` se ejecuta en cada push a `main` (también en los que hace Pages
CMS) y se puede lanzar a mano desde **Actions › Publicar web › Run workflow**:

1. Instala Python, las dependencias y `ffmpeg`.
2. Ejecuta `build.py`. Si falla, la publicación se para y sigue la versión anterior.
3. Publica `_site/` en GitHub Pages.

Tarda uno o dos minutos. Si llegan dos cambios seguidos, GitHub cancela la publicación anterior
y se queda con la última, que ya incluye los dos. Verás publicaciones "cancelled": es normal.

**Configuración necesaria en GitHub:** Settings › Pages › Build and deployment › Source:
**GitHub Actions**. Si se deja en "Deploy from a branch", GitHub publica también la rama tal
cual y, como el repositorio no tiene `index.html`, la web enseña el README.

## Pages CMS

[Pages CMS](https://pagescms.org) es un editor web que guarda directamente en los archivos de
`content/` del repositorio. No tiene base de datos. Se usa la versión alojada,
https://app.pagescms.org.

- **Acceso:** cada editor necesita una cuenta de GitHub y ser colaborador del repositorio
  (Settings › Collaborators). La primera vez, Pages CMS pide instalar su app de GitHub en el
  repositorio.
- **Formularios:** se definen en `.pages.yml`, uno por archivo de `content/`, con etiquetas y
  ayudas en español.
- **Bibliotecas de archivos:** `fotos` (en `assets/img`) y `videos` (en `assets/video`).

Al cambiar `.pages.yml`, ten en cuenta lo siguiente:
- **Precios y coordenadas** son campos de texto (`type: string`), no numéricos. Los campos
  numéricos del navegador solo admiten enteros, y con 1.7 el formulario no se podía guardar ni
  enseñaba el error. `build.py` los convierte a número.
- **Si cambias el tipo de un campo**, convierte también los datos que ya hay en `content/`. Si no,
  Pages CMS da errores como "Expected string, received number".
- **Las descripciones (`description`)** van en los campos, no en las listas. En una lista, Pages
  CMS repite la descripción debajo de cada elemento.
- **Después de subir cambios**, recarga Pages CMS para que lea la configuración nueva.

## Diseño y secciones

Debajo del hero, la página imita la tienda: el verde petróleo de la pared y el dorado del logo se
alternan con el rosa del packaging y un fondo nata. Los titulares van en Italiana; el texto y
los números, en Jost (los números de Italiana no se leen bien, ver la clase `.num`); los detalles
caligráficos, en Petit Formal Script.

1. **Monta tu vaso** (`#carta`): la carta en tres tarjetas, como la carta impresa, cada una con
   su foto o vídeo y el número del paso en una esquina de color. Las opciones se pueden marcar:
   abajo se van sumando el precio y los alérgenos. Sin JavaScript sigue siendo una lista legible.
   Debajo, la llamada a ir a la tienda: "Pídelo así en la tienda", el horario de hoy calculado con
   la hora del visitante ("Abierto ahora, hasta las 22:00"), el botón de Google Maps y, como
   secundario, Instagram.
2. **Para beber** (`#bebidas`): galería deslizable de fotos y vídeos y carta de batidos, matcha y café.
3. **Por encargo** (`#encargos`): la misma estructura que bebidas, con la galería, las bandejas
   y el botón para encargar por mensaje de Instagram.
4. **Las fresas** y **el chocolate** (`#origen`, `#chocolate`): fresas de proximidad y chocolate
   belga Callebaut, con el vídeo de la fuente. Un degradado lleva del marrón chocolate al verde
   de la pared.
5. **Quiénes somos** (`#nosotras`): la foto en la tienda con el sello ovalado de la marca
   estampado en dorado, el texto en párrafos y una despedida con letra a mano.
6. **Del día a día** (`#instagram`): mosaico de fotos que abre el perfil de Instagram.
7. **Preguntas frecuentes** (`#preguntas`): desplegables con animación.
8. **Visítanos** (`#visita`): dirección, horario, botón a Google Maps, mapa e ilustración de la fachada.

**Galerías** (Para beber y Por encargo, macro `galeria()` en la plantilla): cada elemento es una
foto o un vídeo, recortado a 3:4. En el móvil se desliza con el dedo; con ratón salen flechas
debajo (`js/carrusel.js`).

**Vídeos** (`js/videos.js`): sin sonido y en bucle. Solo se descargan al acercarse a la pantalla y
solo se reproducen mientras se ven. Con "reducir movimiento" activado se ve la imagen fija.

## El hero

El hero ocupa `--hero-run` (300vh) de scroll y se queda fijo (sticky) mientras tanto. Según lo que
hayas bajado se dibuja un fotograma u otro en un `<canvas>`, así que la animación avanza y
retrocede con el dedo o la rueda. No se usa `<video>` porque buscar fotogramas con `currentTime`
da tirones, sobre todo en iPhone.

El vídeo va centrado por detrás del logo y el chocolate cae desde arriba. El vídeo se amplía (sin
mover su borde superior) para que la fresa y "Desliza" queden centrados debajo del logo, y vuelve
a su tamaño mientras aparece el lema.

Secuencia (constantes al principio de `js/hero.js`; las distancias van en alturas de pantalla):

1. El hero queda fijo durante 2 pantallas de scroll mientras el vídeo avanza.
2. Hacia la mitad del recorrido (de 1 a 0,6 pantallas antes de soltarse, `CLOSE`) aparecen el lema
   y los botones mientras el chocolate sigue cayendo, y el vídeo se aleja (zoom out) y la fresa
   sube lo justo para no quedar tapada.
3. El hero se suelta poco antes de terminar la animación. Los últimos fotogramas se reproducen
   mientras sube con el logo (`ANIM_OVERRUN`, 0,3 pantallas).
4. Cuando el borde inferior del hero sube por encima del 60 % de la pantalla (`BAR_AT`), la barra
   (símbolo, logo horizontal y hamburguesa) entra desde arriba. Si vuelves a subir, se esconde.

Otros detalles:
- Los fotogramas se cargan de grueso a fino: primero uno de cada 16 y después los intermedios.
  Así, aunque se haga scroll rápido nada más entrar, ya se ve toda la secuencia.
- El fondo del hero usa el color plano del vídeo, de modo que el vídeo no muestra bordes. En
  pantallas anchas los bordes laterales del fotograma se difuminan.
- Con `prefers-reduced-motion` o sin JavaScript se muestra el último fotograma, sin recorrido.

## Cambiar el vídeo del hero

```
scripts/extraer-frames.sh ruta/al/video.mp4 30-156          # del fotograma 30 al 156
scripts/extraer-frames.sh ruta/al/video.mp4 156             # del 1 al 156
scripts/extraer-frames.sh ruta/al/video.mp4 0               # el vídeo entero
scripts/extraer-frames.sh ruta/al/video.mp4 30-156 75 1080  # más calidad y más resolución
```

El vídeo actual usa `30-156`; los primeros fotogramas se descartaron porque el chocolate tardaba
en aparecer. Los archivos conservan su número original (0030.webp…) y el manifest guarda en
`start` el primero.

Necesita `ffmpeg`. El script sustituye los fotogramas, el póster y el manifest. El JS toma el
color de fondo del manifest; para que la versión sin JS también coincida, copia en `--hero-bg`
(en `css/styles.css`) el color que imprime el script.

Para que el vídeo funcione bien en el hero:
- Fondo plano y uniforme durante todo el vídeo. Si el fondo se mueve o cambia de color, se notará
  el borde del vídeo sobre la página.
- Vertical (9:16) o 3:4.
- Unos 8–10 s a 24 fps, que son unos 200–240 fotogramas y 3–5 MB.

## SEO y GEO

La web está preparada para Google (SEO local) y para que los asistentes de IA (ChatGPT,
Perplexity, Gemini, el modo IA de Google…) encuentren la tienda y la citen con datos correctos (GEO).

- **`<head>`:** título, descripción, URL canónica, tarjetas para compartir (`assets/og/og.jpg`)
  y coordenadas de la tienda.
- **Datos estructurados (JSON-LD):** la tienda (`FoodEstablishment`) con dirección, coordenadas,
  horario, Instagram y forma de encargar; la carta completa con precios (`Menu`); la web; y las
  preguntas frecuentes (`FAQPage`).
- **Preguntas frecuentes:** respuestas cortas y concretas, que es lo que más citan las IA.
- **`llms.txt`:** ficha de la tienda en texto plano para asistentes de IA.
- **`robots.txt` y `sitemap.xml`:** el primero deja entrar a buscadores y bots de IA.

## Problemas conocidos y soluciones

| Síntoma | Causa y solución |
|---|---|
| La web enseña el README | Pages está en "Deploy from a branch". Cámbialo a **GitHub Actions** (ver [Publicación](#publicación)). |
| "413 failed to upload file" en Pages CMS | La versión alojada no acepta archivos de más de unos 3 MB (funciona sobre Vercel, con un límite de 4,5 MB, y codifica los archivos en base64). Sube el archivo por GitHub (*Add file › Upload files*, hasta 25 MB) en `assets/video` o `assets/img` y elígelo después en el CMS. |
| Pulsar guardar en Pages CMS no hace nada | Hay un campo con un error dentro de un elemento plegado. Usa *Expand all* para encontrarlo en rojo. |
| "Expected string, received number" | Un dato guardado no es del tipo del campo (ver [Pages CMS](#pages-cms)). |
| La publicación falla | En **Actions**, abre la ejecución fallida: el paso `python build.py` dice en español qué dato está mal. |
| Una publicación sale "cancelled" | Llegó otro cambio justo detrás. La siguiente publicación lo incluye todo. |

## Pendiente

**Contenido por confirmar con la tienda**
- Alérgenos de las cremas Chocolate Dubái y Chocolate Tokyo. Mientras tanto, "Monta tu vaso" pide
  preguntar en tienda. Cuando se sepan: Pages CMS › Monta tu vaso › cremas, desmarcar "Alérgenos
  sin confirmar" y elegirlos.
- Precios de las bandejas: se tomaron de la publicación de Instagram del 9 de mayo.
- Alérgeno nº 7: en la carta dice "frutos de cáscara" en español y "peanuts" en inglés.
- Texto de "Quiénes somos": confirmar la frase "cada vaso montado al momento, a tu gusto".
- Repasar precios y carta antes de anunciar la web.

**Posicionamiento y buenas prácticas** (revisión del 28/10/2026, por orden de impacto)

*Fuera de la web*
- Ficha de Google Business: nombre, dirección y horario idénticos a la web; categorías (tienda de
  postres, cafetería); web enlazada; fotos y carta; responder reseñas.
- Bing Places (ChatGPT busca con Bing) y Apple Business Connect (Siri, Apple Maps).
- TripAdvisor y Yelp. Pedir reseñas a los clientes.
- Menciones en blogs, guías y prensa local de Salamanca.
- Enlace a la web en la bio de Instagram.

*Legal (obligatorio)*
- Aviso legal (LSSI: titular, NIF, domicilio, email), política de privacidad y de cookies.
- Alojar las fuentes en la propia web y cargar el mapa de Google solo al pulsarlo. Ahora los dos
  envían datos de cada visita a Google sin consentimiento.

*Técnico, al conectar el dominio*
- `CNAME` en el repositorio, HTTPS y redirección de www a sin www.
- Google Search Console y Bing Webmaster Tools, con el sitemap.
- Página 404 propia.
- Analítica sin cookies (Plausible o GoatCounter).

*Datos que faltan*
- Teléfono y email de la tienda. Hay campos para ellos en Pages CMS › Tienda; al rellenarlos salen
  en Visítanos y en los datos para Google.

*Oportunidades*
- Versión en inglés de la web (turistas y Erasmus).
- Página de encargos (San Valentín, Día de la Madre…).
- Hero más ligero en móvil: cargar los fotogramas después del resto, o menos con ahorro de datos.
- Fijar `runs-on: ubuntu-24.04` en la publicación. GitHub pasará `ubuntu-latest` a Ubuntu 26 y
  avisa de ello en cada ejecución.
- Fotos antiguas sin usar en `assets/img/` (`batido-matcha`, `brocheta`, `cajas`, `tarta-cajas`):
  reutilizarlas o borrarlas.
