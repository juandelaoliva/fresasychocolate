# Fresas y Chocolate · web

Web estática (HTML + CSS + JS, sin npm ni build). Abre `index.html` con doble clic o publícala
tal cual en cualquier hosting estático (Netlify, Vercel, GitHub Pages, un servidor Apache…).

## Estructura

```
index.html                 página completa (los logos van incrustados como SVG)
css/styles.css             estilos, mobile first; paleta de marca en :root
js/hero.js                 animación del hero ligada al scroll
assets/hero/frames/        el vídeo del hero convertido en 240 fotogramas WebP
assets/hero/poster.webp    último fotograma (sin JS / movimiento reducido)
assets/hero/manifest.js    nº de fotogramas, tamaño y color de fondo del vídeo
assets/img/                fotos de producto optimizadas
assets/logo/               logos SVG limpios (fill = currentColor)
scripts/extraer-frames.sh  regenera los fotogramas a partir de un vídeo
```

## Cómo funciona el hero

El hero ocupa 300vh de scroll y se queda fijo (sticky) mientras tanto. Según lo que hayas
bajado se dibuja un fotograma u otro en un `<canvas>`, así que la animación avanza y retrocede
con el dedo o la rueda. No se usa `<video>` porque buscar fotogramas con `currentTime` da
tirones, sobre todo en iPhone.

En móvil, el vídeo ocupa toda la pantalla por detrás del logo y el chocolate cae desde arriba.
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
- Vertical (9:16) o 3:4. En escritorio ocupa la columna derecha.
- Unos 8–10 s a 24 fps, que son unos 200–240 fotogramas y 3–5 MB.

## Pendiente / por confirmar

- Horario de apertura: no aparece en ningún material, así que no se ha puesto.
- Textos de las secciones "para regalar" y "visítanos": son una propuesta. Hay que confirmar
  si se aceptan encargos y por qué canal.
- Leyenda de alérgenos: en la carta, el nº 7 dice "frutos de cáscara" en español y "peanuts"
  en inglés. Conviene revisarlo con el local.
- Revisar precios y carta con el local antes de publicar.
- Fotos: de momento son las de WhatsApp. Si hay originales en mejor calidad, sustitúyelas en
  `assets/img/` con el mismo nombre.
