# Fresas y Chocolate · web

Web estática (HTML + CSS + JS, sin npm ni build). Abre `index.html` con doble clic o publícala
tal cual en cualquier hosting estático (Netlify, Vercel, GitHub Pages, un servidor Apache…).

## Estructura

```
index.html                 página completa (los logos van incrustados como SVG)
css/styles.css             estilos, mobile first; paleta de marca en :root
js/hero.js                 animación del hero ligada al scroll
js/menu.js                 menú hamburguesa
js/vaso.js                 "Monta tu vaso": suma el precio y los alérgenos de lo elegido
js/videos.js               vídeos cortos de la tienda: cargan al acercarse y solo se reproducen en pantalla
js/faq.js                  preguntas frecuentes: abren y cierran con animación
assets/hero/frames/        el vídeo del hero convertido en fotogramas WebP (0030–0156)
assets/hero/poster.webp    último fotograma (sin JS / movimiento reducido)
assets/hero/manifest.js    nº de fotogramas, tamaño y color de fondo del vídeo
assets/img/insta/          fotos de Instagram optimizadas (1000 px de ancho)
assets/video/              clips de los reels (recortados, sin sonido) y su fotograma de portada
assets/img/                fachada y fotos antiguas de WhatsApp (algunas ya sin usar)
assets/logo/               logos SVG limpios (fill = currentColor) y el símbolo de la fresa
assets/icons/              favicon (SVG + PNG) e icono para la pantalla de inicio del iPhone
scripts/extraer-frames.sh  regenera los fotogramas a partir de un vídeo
```

## Secciones

Debajo del hero, la página imita la tienda: el verde petróleo de la pared y el dorado del
logo se alternan con el rosa del packaging y un fondo nata. Los titulares van en Italiana; el
texto, en Jost; los detalles caligráficos (antetítulos y lema del hero), en Petit Formal Script.

1. **Monta tu vaso**: la carta de 3 pasos en tres tarjetas, como la carta impresa de la tienda, cada
   una con su foto o vídeo y el número en la esquina. Las opciones se pueden seleccionar. Suma el precio y lista
   los alérgenos de la combinación. Sin JavaScript sigue funcionando como una lista de opciones.
2. **Para beber**: tira de fotos deslizable y los precios de batidos, matcha y café.
3. **Por encargo**: bandejas solo fresas y mixtas, caja personalizada y botón para encargar
   por mensaje de Instagram.
4. **De Salamanca** y **el chocolate**: el origen de las fresas (de proximidad, de Salamanca). La foto se funde
   en marrón chocolate y continúa en el bloque del chocolate belga Callebaut, con el vídeo de la fuente.
5. **Quiénes somos**: Rosi y Adri.
6. **Del día a día**: mosaico de fotos de Instagram.
7. **Visítanos**: dirección, horario, mapa e ilustración de la fachada.

## Cómo funciona el hero

El hero ocupa 300vh de scroll y se queda fijo (sticky) mientras tanto. Según lo que hayas
bajado se dibuja un fotograma u otro en un `<canvas>`, así que la animación avanza y retrocede
con el dedo o la rueda. No se usa `<video>` porque buscar fotogramas con `currentTime` da
tirones, sobre todo en iPhone.

En móvil y en escritorio, el vídeo va centrado por detrás del logo y el chocolate cae desde arriba.
El vídeo se amplía (sin mover su borde superior) para que la fresa y "Desliza" queden centrados
debajo del logo, y vuelve a su tamaño mientras aparece el lema.
Secuencia (constantes `ANIM_OVERRUN`, `CLOSE` y `BAR_AT` en `js/hero.js`, en alturas de pantalla):

1. El hero queda fijo durante 2 pantallas de scroll mientras el vídeo avanza.
2. Media pantalla antes de soltarse, aparecen el lema y los botones, y la fresa sube lo justo
   para no quedar tapada.
3. El hero se suelta poco antes de terminar la animación. Los últimos fotogramas se reproducen
   mientras sube con el logo (`ANIM_OVERRUN` = 0,3 pantallas).
4. Cuando el borde inferior del hero sube por encima del 60 % de la pantalla, la barra (logo
   horizontal + hamburguesa) entra desde arriba. Si vuelves a subir, se esconde.

- Los fotogramas se cargan de grueso a fino: primero uno de cada 16 y después los intermedios.
  Así, aunque se haga scroll rápido nada más entrar, ya se ve toda la secuencia.
- El fondo del hero usa el color plano del vídeo, de modo que el vídeo no muestra bordes.
- Con `prefers-reduced-motion` o sin JavaScript se muestra el último fotograma, sin recorrido.
- Para cambiar la longitud del recorrido, edita `--hero-run` en `css/styles.css`.

## Cambiar el vídeo

```
scripts/extraer-frames.sh ruta/al/video.mp4 30-156          # empieza en el 30 y se detiene en el 156
scripts/extraer-frames.sh ruta/al/video.mp4 156             # del 1 al 156
scripts/extraer-frames.sh ruta/al/video.mp4 0               # usar el vídeo entero
scripts/extraer-frames.sh ruta/al/video.mp4 30-156 75 1080  # más calidad / más resolución
```

El vídeo actual usa `30-156`. Los primeros fotogramas se descartaron porque el chocolate tardaba
en aparecer. Los archivos conservan su número original (0030.webp…) y el manifest guarda en
`start` el primero.

Necesita `ffmpeg`. El script sustituye los fotogramas, el póster y el manifest. El JS toma el
color de fondo del manifest. Para que la versión sin JS también coincida, copia en
`--hero-bg` (en `css/styles.css`) el color que imprime el script.

Para que el vídeo funcione bien en el hero:
- Fondo plano y uniforme durante todo el vídeo. Si el fondo se mueve o cambia de color, se
  notará el borde del vídeo sobre la página.
- Vertical (9:16) o 3:4. En escritorio se ve centrado bajo el logo y sus bordes laterales se difuminan
  con el fondo; con el móvil en horizontal ocupa la columna derecha.
- Unos 8–10 s a 24 fps, que son unos 200–240 fotogramas y 3–5 MB.

## SEO y GEO

La web está preparada para Google (SEO local) y para que los asistentes de IA (ChatGPT, Perplexity,
Gemini, el modo IA de Google…) encuentren la tienda y la citen con datos correctos (GEO).

- `<head>` de `index.html`: título, descripción, URL canónica (https://fresasychocolate.com/),
  tarjetas para compartir (imagen en `assets/og/og.jpg`) y coordenadas de la tienda.
- Datos estructurados (JSON-LD, en el `<head>`): la tienda con dirección, coordenadas, horario,
  Instagram y forma de encargar; la carta completa con precios; y las preguntas frecuentes.
- Sección **Preguntas frecuentes** (`#preguntas`): respuestas cortas y concretas, que es lo que más
  citan las IA. Sus textos también están en el JSON-LD.
- `llms.txt`: ficha de la tienda en texto plano para asistentes de IA.
- `robots.txt` (permite buscadores y bots de IA) y `sitemap.xml`.

**Si cambian precios, horario o carta**, hay que actualizarlo en cuatro sitios: la sección visible de
`index.html`, el JSON-LD del `<head>`, las preguntas frecuentes y `llms.txt`.

## Revisión de posicionamiento (pendiente, 28/10/2026)

Por orden de impacto. Nada de esto está hecho todavía.

**Fuera de la web**
- Ficha de Google Business: nombre, dirección y horario idénticos a la web; categorías (tienda de
  postres, cafetería); web enlazada; fotos y carta; responder reseñas.
- Bing Places (ChatGPT busca con Bing) y Apple Business Connect (Siri, Apple Maps).
- TripAdvisor y Yelp. Pedir reseñas a clientes.
- Menciones en blogs, guías y prensa local de Salamanca.
- Enlace a la web en la bio de Instagram.

**Legal (obligatorio)**
- Aviso legal (LSSI: titular, NIF, domicilio, email), política de privacidad y de cookies.
- Alojar las fuentes en la propia web y cargar el mapa de Google solo al pulsarlo (ahora ambos
  envían datos de cada visita a Google sin consentimiento).

**Técnico, al conectar el dominio**
- `CNAME` en el repo, HTTPS y redirección de www a sin www.
- Google Search Console y Bing Webmaster Tools, con el sitemap.
- Página 404 propia.
- Analítica sin cookies (Plausible o GoatCounter).

**Datos que faltan**
- Teléfono y email de la tienda (para la web y los datos estructurados).

**Oportunidades**
- Versión en inglés (turistas y Erasmus).
- Página de encargos (San Valentín, Día de la Madre…).
- Hero más ligero en móvil: cargar los fotogramas después del resto o menos con ahorro de datos.

## Pendiente / por confirmar

- Alérgenos de las cremas Chocolate Dubái y Chocolate Tokyo: aún no se conocen. Mientras tanto,
  "Monta tu vaso" pide preguntar en tienda (atributo `data-al-pending` en `index.html`). Cuando
  se sepan, cámbialo por `data-al="…"` con los números.
- Precios de las bandejas: se han tomado de la publicación de Instagram del 9 de mayo.
  Confirmar que siguen vigentes.
- Leyenda de alérgenos: en la carta, el nº 7 dice "frutos de cáscara" en español y "peanuts"
  en inglés. Conviene revisarlo con el local.
- Revisar precios y carta con el local antes de publicar.
- Las fotos del mosaico de Instagram son una selección fija. Para cambiarlas, sustituye los
  archivos en `assets/img/insta/` o edita la sección en `index.html`.
