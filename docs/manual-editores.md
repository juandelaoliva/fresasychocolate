# Manual para editar la web de Fresas y Chocolate

Este manual explica cómo cambiar el contenido de la web (precios, horario, textos, fotos, vídeos
y preguntas frecuentes) sin tocar nada técnico. Todo se hace desde el navegador, en el ordenador
o en el móvil.

## Índice

1. [Antes de empezar](#1-antes-de-empezar)
2. [Entrar en el editor](#2-entrar-en-el-editor)
3. [Cómo se guarda y se publica un cambio](#3-cómo-se-guarda-y-se-publica-un-cambio)
4. [Qué se puede cambiar en cada apartado](#4-qué-se-puede-cambiar-en-cada-apartado)
5. [Tareas habituales, paso a paso](#5-tareas-habituales-paso-a-paso)
6. [Fotos y vídeos](#6-fotos-y-vídeos)
7. [Si algo no funciona](#7-si-algo-no-funciona)
8. [Lo que no se cambia desde el editor](#8-lo-que-no-se-cambia-desde-el-editor)

## 1. Antes de empezar

- **Cuenta de GitHub.** El editor guarda los cambios en GitHub, así que necesitas una cuenta
  (es gratis, en https://github.com). Pide a quien mantiene la web que te añada al proyecto: te
  llegará una invitación por email que tienes que aceptar.
- **Lo que cambias se publica de verdad.** No hay una versión de pruebas: al guardar, el cambio
  sale en la web en uno o dos minutos. Revisa antes de guardar.
- **No se puede romper la web.** Si guardas algo mal (por ejemplo, un precio con letras), la web
  no se actualiza y sigue la versión anterior hasta que se corrija. Ver
  [Si algo no funciona](#7-si-algo-no-funciona).

## 2. Entrar en el editor

1. Abre https://app.pagescms.org.
2. Entra con tu cuenta de GitHub.
3. Elige el proyecto **fresasychocolate**. La primera vez puede pedirte que instales su app en
   GitHub: acepta.
4. Comprueba arriba que estás en la rama **main**. Es la que se publica.

A la izquierda verás los apartados de la web. En el móvil están en el menú de arriba a la izquierda.

## 3. Cómo se guarda y se publica un cambio

1. Entra en un apartado y haz los cambios.
2. Pulsa **Save** (arriba a la derecha).
3. Espera uno o dos minutos y recarga la web: https://fresasychocolate.com/ (mientras no esté el
   dominio, https://juandelaoliva.github.io/fresasychocolate/).

Si el cambio no aparece después de unos minutos, recarga forzando (en el ordenador,
Mayús + recargar) o abre la web en una ventana privada.

**Las listas salen plegadas.** Cremas, toppings, productos, fotos y preguntas aparecen cerradas y
muestran solo el nombre. Pulsa la flecha para abrir una, o **Expand all** para abrirlas todas.
Arrastra los puntitos de la izquierda (⠿) para cambiar el orden y pulsa la papelera para borrar.
**Add an item** añade un elemento nuevo al final.

**Required** al lado de un campo significa que es obligatorio.

## 4. Qué se puede cambiar en cada apartado

| Apartado del editor | Qué cambia en la web |
|---|---|
| **Tienda (dirección y horario)** | Dirección, teléfono, email, Instagram, enlace a Google Maps y horario. Salen en Visítanos, en el pie, en el menú y en las preguntas frecuentes. |
| **Portada y Google** | La frase que aparece al final de la animación inicial, y cómo sale la tienda en Google y en asistentes como ChatGPT. |
| **Monta tu vaso** | Precio del vaso, cremas, toppings, precios, alérgenos y fotos de las tres tarjetas. |
| **Para beber** | Galería de fotos y vídeos, y la carta de batidos, matcha y café. |
| **Por encargo** | Galería de fotos y vídeos, bandejas con sus tamaños y precios, y cómo se encarga. |
| **Fresas, chocolate y quiénes somos** | Textos, fotos y vídeo de esas tres secciones. |
| **Del día a día (Instagram)** | Las fotos del mosaico. |
| **Preguntas frecuentes** | Las preguntas que se escriben a mano. |

**Preguntas que se escriben solas.** Las de dirección, horario, precio del vaso, encargos y
bebidas se generan a partir de los datos de los otros apartados. Si cambias un precio o el
horario, esas respuestas se actualizan solas. No hace falta (ni se puede) escribirlas a mano.

## 5. Tareas habituales, paso a paso

### Cambiar un precio

1. Ve al apartado donde está el producto: **Monta tu vaso**, **Para beber** o **Por encargo**.
2. Despliega el grupo y el producto, y cambia **Precio (€)**.
3. Escríbelo como prefieras: `1,70`, `1.70`, `12` o `4,80 €` valen todos. En la web siempre sale
   bien escrito (1,70 €).
4. Guarda.

En **Monta tu vaso**, las cremas tienen un único precio para todas (en "Paso 2: cremas") y los
toppings van por **grupos de precio** (por ejemplo, +0,50 € y +1,00 €). Para cambiar el precio de
un topping, cámbialo de grupo: bórralo de uno y añádelo en el otro.

### Añadir o quitar una crema o un topping

1. **Monta tu vaso** › "Paso 2: cremas" › **Cremas**, o "Paso 3: toppings" › el grupo de precio ›
   **Toppings**.
2. **Add an item** para añadir uno, o la papelera para quitarlo.
3. Escribe el **Nombre** y marca sus **Alérgenos**.
4. Si aún no se saben los alérgenos, marca **Alérgenos sin confirmar**: la web pedirá al cliente
   que pregunte en la tienda.
5. Guarda.

La calculadora de "Monta tu vaso" y las preguntas frecuentes se actualizan solas.

### Cambiar el horario

1. **Tienda (dirección y horario)** › **Horario**.
2. Cada fila es un grupo de días con el mismo horario. Por ejemplo: "Lunes a jueves, de 14:00 a 22:00".
3. En cada fila:
   - **Días (como se ve en la web):** el texto que se lee, por ejemplo `Viernes y sábado`.
   - **Qué días son:** marca los mismos días en la lista. Es lo que lee Google, así que tienen
     que coincidir con el texto.
   - **Abre** y **Cierra:** con el formato `14:00`.
4. Guarda.

Para un día con horario especial, añade otra fila. Si un día se cierra, quítalo de su fila.

### Añadir una bebida o una bandeja

1. **Para beber** › **Grupos** › el grupo (Batidos, Matcha, Café) › **Productos** › **Add an
   item**. En **Por encargo**: **Bandejas** › la bandeja › **Tamaños** › **Add an item**.
2. Rellena el nombre, el precio y, si quieres, un **Detalle** (por ejemplo, "Fresas, leche y
   miel" o "6 fresas aprox.").
3. Guarda.

Para un grupo nuevo de bebidas (por ejemplo, "Zumos"), usa **Add an item** en **Grupos**.

### Cambiar textos

Casi todas las secciones tienen **Antetítulo** (la palabra en letra a mano, encima del título),
**Título** y **Texto**. Cámbialos y guarda.

En **Quiénes somos**:
- El **Texto** puede tener varios párrafos: deja una línea en blanco entre uno y otro.
- La **Despedida** sale al final con letra a mano (por ejemplo, "¡Te esperamos!"). Si la dejas
  vacía, no sale.

### Añadir o cambiar preguntas frecuentes

1. **Preguntas frecuentes** › **Preguntas** › **Add an item**.
2. Escribe la **Pregunta** como la haría un cliente ("¿Tenéis opciones sin gluten?") y una
   **Respuesta** corta y concreta. Google y los asistentes de IA citan mejor las respuestas
   directas.
3. Para poner un enlace en la respuesta: `[texto que se ve](https://dirección)`. Por ejemplo,
   `[escríbenos por Instagram](https://ig.me/m/fresasychocolate.salamanca)`.
4. Guarda.

### Cambiar cómo sale la tienda en Google

**Portada y Google**:
- **Título en Google:** lo que sale en azul en los resultados. Mejor menos de 60 caracteres.
- **Descripción en Google:** el texto gris bajo el título. Mejor entre 120 y 160 caracteres.
- **Descripción de la tienda:** la leen Google y los asistentes de IA (ChatGPT, Perplexity…). Que
  sea concreta: qué vendéis, dónde y qué os hace distintas.

Google tarda días o semanas en mostrar los cambios.

## 6. Fotos y vídeos

### Subir una foto o un vídeo a una galería

Las galerías de **Para beber** y **Por encargo** se deslizan de lado y admiten fotos y vídeos
mezclados.

1. Ve a **Fotos y vídeos** › **Add an item**.
2. Para una **foto**: pulsa en **Foto** y súbela o elígela de la biblioteca.
3. Para un **vídeo**: pulsa en **Vídeo** y súbelo. La **Foto** es opcional: es la imagen que se ve
   mientras carga. Si no pones ninguna, se saca del propio vídeo.
4. Escribe la **Descripción**. Es obligatoria (ver más abajo).
5. Arrastra el elemento a su sitio en la lista y guarda.

Los vídeos se ven sin sonido, en bucle y solo mientras están en pantalla.

### Cambiar una foto de otra sección

Igual que en las galerías: pulsa en el campo de la foto, sube o elige otra y cambia también su
**Descripción** si ya no corresponde.

### La descripción de las fotos

Cada foto y cada vídeo necesita una descripción de lo que se ve. La leen las personas ciegas (con
lectores de pantalla) y Google. Escribe lo que verías si no pudieras ver la foto:

- Bien: "Vaso de fresas con chocolate blanco y Lacasitos por encima".
- Mal: "foto1", "rico", "vaso".

### Consejos para que se vean bien

- **Formato:** en las galerías, las fotos y vídeos se recortan a vertical (3:4). Usa fotos
  verticales con lo importante en el centro. En el mosaico de Instagram se recortan cuadradas.
- **Mosaico de Instagram:** mejor 6 fotos (o 3), para que quede completo.
- **Vídeos:** mejor cortos, de menos de 15 segundos.
- **Desde el iPhone:** las fotos y vídeos se pueden subir tal cual, también en el formato del
  iPhone (HEIC y MOV). Al publicar se reducen y se convierten solos, así que no hace falta
  editarlos antes.

### Archivos de más de 3 MB

El editor no deja subir archivos de más de unos 3 MB. Sale el error **"413 failed to upload
file"**. Les pasa a casi todos los vídeos y a algunas fotos. Para subirlos:

1. Entra en https://github.com/juandelaoliva/fresasychocolate con tu cuenta.
2. Abre la carpeta `assets`, y dentro, `video` para vídeos o `img` para fotos.
3. Pulsa **Add file › Upload files**, arrastra el archivo (hasta 25 MB) y pulsa **Commit changes**.
4. Vuelve al editor y, en el campo del vídeo o la foto, elige ese archivo de la biblioteca en vez
   de subirlo.

Otra opción es enviarte antes el vídeo o la foto por WhatsApp, que lo reduce, y subir esa versión.

## 7. Si algo no funciona

**Pulso Save y no pasa nada.**
Algún campo tiene un error y está dentro de un elemento plegado, así que no se ve. Pulsa **Expand
all** en cada lista y busca el campo marcado en rojo. Suele ser un campo obligatorio vacío, como
la descripción de una foto.

**Sale "413 failed to upload file".**
El archivo pesa demasiado. Ver [Archivos de más de 3 MB](#archivos-de-más-de-3-mb).

**He guardado pero la web no cambia.**
1. Espera dos o tres minutos y recarga la web forzando (Mayús + recargar) o en una ventana privada.
2. Si sigue igual, puede que la publicación haya fallado por un dato mal escrito. Entra en
   https://github.com/juandelaoliva/fresasychocolate/actions:
   - Si la última fila tiene un círculo rojo, ha fallado. Ábrela, entra en **generar** y busca el
     paso **python build.py**: dice en español qué hay que corregir (por ejemplo, "el precio debe
     ser un número"). Corrígelo en el editor y guarda otra vez.
   - Si pone **cancelled**, no pasa nada: se guardó otro cambio justo después y se publicó todo junto.

**Me he equivocado y quiero volver atrás.**
El icono del reloj, al lado de **Save**, muestra el historial de cambios de ese apartado y lo que
había antes. Si no sabes deshacerlo, avisa a quien mantiene la web: todos los cambios quedan
guardados y se pueden recuperar.

**Sale un error raro en el editor.**
Recarga la página del editor y vuelve a intentarlo. Si sigue, haz una captura y envíasela a quien
mantiene la web.

## 8. Lo que no se cambia desde el editor

Estas cosas las cambia quien mantiene la web:

- El diseño, los colores y las letras.
- La animación inicial de la fresa.
- Añadir secciones nuevas a la web.
- El dominio y los avisos legales.

**Con cuidado:** el vídeo de la tarjeta de cremas en "Monta tu vaso" y el de la sección del
chocolate sí se pueden cambiar desde el editor, pero tienen un encuadre pensado para su hueco.
Si los cambias, revisa después cómo quedan en el móvil y en el ordenador.
