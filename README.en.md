# Fresas y Chocolate · website

[Español](README.md) · **English**

Website for [Fresas y Chocolate](https://fresasychocolate.com/), a chocolate-covered strawberry
shop at Calle Espoz y Mina, 38, in Salamanca (Spain). It is a static, single-page site generated
from content files. The content (prices, opening hours, text, photos, videos, FAQ) is edited in
**Pages CMS**, and GitHub publishes the site automatically within a couple of minutes.

```
Pages CMS → content/*.yml on GitHub → GitHub Actions runs build.py → GitHub Pages
```

- **If you edit content**, read the [editors' manual](docs/manual-editores.md) (in Spanish). You
  don't need anything below.
- **If you maintain the site** (code, design, publishing), this README is for you.

The site and its content are in Spanish. Field names in `content/` and `.pages.yml` are in
Spanish too; the main ones are explained below.

## Contents

- [Working locally](#working-locally)
- [Repository layout](#repository-layout)
- [How the site is built (build.py)](#how-the-site-is-built-buildpy)
- [Publishing](#publishing)
- [Pages CMS](#pages-cms)
- [Design and sections](#design-and-sections)
- [The hero](#the-hero)
- [Changing the hero video](#changing-the-hero-video)
- [SEO and GEO](#seo-and-geo)
- [Client presentation](#client-presentation)
- [Known issues and fixes](#known-issues-and-fixes)
- [To do](#to-do)

## Working locally

You need Python 3.9 or later and, only if there are videos to convert, `ffmpeg`.

```
pip install -r requirements.txt
python3 build.py          # generates _site/
open _site/index.html     # on macOS; elsewhere, open the file in a browser
```

After any change in `content/`, `src/`, `css/` or `js/`, run `build.py` again and reload the page.
`_site/` is not committed.

`SITE_URL=https://another-domain/ python3 build.py` changes the domain used for the canonical
URL, the sitemap, `llms.txt` and the data for Google. The default is https://fresasychocolate.com/.

Run `git pull` before `git push`: whatever is saved in Pages CMS lands on `main` as commits, so
there are often new changes.

## Repository layout

```
content/*.yml              the content: what Pages CMS edits (one file per section)
src/index.html.j2          page template (Jinja2)
src/llms.txt.j2            shop summary for AI assistants
src/sitemap.xml.j2         sitemap
src/robots.txt.j2          robots.txt
src/legal.html.j2          base for the legal pages: aviso-legal.html.j2 and privacidad.html.j2
src/pie.html.j2            footer shared by every page
src/analitica.html.j2      Cloudflare Web Analytics (only with a token)
src/svg/                   logos, strawberry symbol, seal, arrow and wave (inlined in the page)
build.py                   generates _site/ from content/ and src/
requirements.txt           Python dependencies
.pages.yml                 Pages CMS forms
.github/workflows/         automatic publishing to GitHub Pages
css/styles.css             styles, mobile first; brand palette in :root
css/fonts.css              self-hosted fonts (Italiana, Jost, Petit Formal Script)
js/hero.js                 scroll-driven hero animation
js/menu.js                 menu: burger on phones; on desktop, marks the section in view
js/vaso.js                 "Monta tu vaso": adds up the price and allergens of the chosen options
js/videos.js               shop videos: load when near the screen, play only while visible
js/carrusel.js             swipeable galleries: arrows for mouse users
js/faq.js                  FAQ: animated open and close
js/mapa.js                 the Google map only loads after tapping "Ver el mapa aquí"
assets/hero/               the hero video as WebP frames, poster and manifest
assets/img/                photos (uploads from the CMS land here too)
assets/video/              shop videos and their still images
assets/logo/               clean SVG logos (fill = currentColor), strawberry symbol and seal
assets/icons/              favicon and iPhone home-screen icon
assets/og/                 social sharing image and square logo for Google
assets/fonts/              font files (woff2, latin and latin-ext)
scripts/extraer-frames.sh  regenerates the hero frames from a video
docs/                      editors' manual
presentacion/index.html    client presentation of the site concept, at /presentacion/ (not indexed)
```

The files in `content/`:

| File | Contents |
|---|---|
| `tienda.yml` (shop) | Name, address, coordinates, Google Maps, Instagram, phone, email, opening hours and the owner's details (legal notice) |
| `portada.yml` (front page) | Hero tagline, Google title and description, shop description for AI and the Cloudflare Web Analytics token |
| `carta.yml` (menu) | "Monta tu vaso": cup, creams, topping groups, prices and allergens |
| `bebidas.yml` (drinks) | Gallery and drinks menu |
| `encargos.yml` (orders) | Gallery, trays and how to order |
| `historia.yml` (story) | The strawberries, the chocolate and "about us" |
| `instagram.yml` | Photos in the "Del día a día" mosaic |
| `preguntas.yml` (FAQ) | Hand-written FAQ entries |

## How the site is built (build.py)

`build.py` reads `content/*.yml`, validates it, fills in the templates in `src/` and writes the
result to `_site/` along with `css/`, `js/` and `assets/`.

**Validation.** If something is wrong, it stops with a message in Spanish and generates nothing,
so a broken site is never published. Among other things, it checks:
- that the essential fields are present (the `OBLIGATORIOS` list);
- that prices are numbers; `1,70`, `1.70`, `12` and `4,80 €` are all accepted;
- that allergens come from the menu's list (`ALERGENOS`) and weekdays are valid;
- that times look like `14:00`;
- that every photo and video exists and has a description (alt text).

**Photos.** WebP files up to 1600 px wide are published as they are. Everything else (JPG, PNG,
HEIC from iPhones…) is converted to WebP at most 1600 px wide, and the original is not published.

**Videos.** MP4 files up to 12 MB are published as they are. Everything else (iPhone MOV, heavy
MP4…) is converted with `ffmpeg` to a silent MP4 at most 720 px wide. If a video has no still
image, one is taken from the video itself.

**Automatic FAQ.** The questions about the address, opening hours, cup price, orders and drinks
are written from `tienda.yml`, `carta.yml`, `encargos.yml` and `bebidas.yml`, so they never
contradict the menu. The rest come from `preguntas.yml`. Answers can contain links written as
`[text](https://…)`.

**Data for Google and AI.** From the same data it generates the JSON-LD (shop, menu with prices,
website and FAQ), `llms.txt`, `sitemap.xml` and `robots.txt`. A price is changed in one place and
updated everywhere.

## Publishing

`.github/workflows/publicar.yml` runs on every push to `main` (including the ones Pages CMS makes)
and can be started by hand from **Actions › Publicar web › Run workflow**:

1. Installs Python, the dependencies and `ffmpeg`.
2. Runs `build.py`. If it fails, publishing stops and the previous version stays live.
3. Publishes `_site/` to GitHub Pages.

It takes one or two minutes. If two changes arrive in a row, GitHub cancels the earlier run and
keeps the last one, which already includes both. You will see "cancelled" runs; that is expected.

**Required GitHub setting:** Settings › Pages › Build and deployment › Source: **GitHub Actions**.
If it is left on "Deploy from a branch", GitHub also publishes the branch as is, and since the
repository has no `index.html`, the site shows the README.

## Pages CMS

[Pages CMS](https://pagescms.org) is a web editor that saves straight into the files in
`content/`. There is no database. We use the hosted version at https://app.pagescms.org.

- **Access:** each editor needs a GitHub account and must be a collaborator on the repository
  (Settings › Collaborators). The first time, Pages CMS asks to install its GitHub app on the repo.
- **Forms:** defined in `.pages.yml`, one per file in `content/`, with Spanish labels and hints.
- **Media libraries:** `fotos` (in `assets/img`) and `videos` (in `assets/video`).

When changing `.pages.yml`, keep this in mind:
- **Prices and coordinates** are text fields (`type: string`), not number fields. The browser's
  number fields only accept whole numbers, so with 1.7 the form couldn't be saved and showed no
  error. `build.py` converts them to numbers.
- **If you change a field's type**, also convert the existing data in `content/`. Otherwise Pages
  CMS shows errors such as "Expected string, received number".
- **Descriptions (`description`)** go on fields, not on lists. On a list, Pages CMS repeats the
  description under every item.
- **After pushing changes**, reload Pages CMS so it reads the new configuration.

## Design and sections

Below the hero, the page echoes the shop: the teal of the wall and the gold of the logo alternate
with the pink of the packaging and a cream background. Headings use Italiana; body text and
numbers use Jost (Italiana's figures don't read well; see the `.num` class); script details use
Petit Formal Script.

1. **Monta tu vaso** (`#carta`, "build your cup"): the menu as three cards, like the printed
   menu, each with a photo or video and the step number in a coloured corner. Options can be
   selected; the price and allergens add up at the bottom. Without JavaScript it is still a
   readable list. Below it, the call to visit the shop: "Pídelo así en la tienda" (order it like
   this in the shop), today's hours worked out from the visitor's clock ("Abierto ahora, hasta las
   22:00"), the Google Maps button and, secondary, Instagram.
2. **Para beber** (`#bebidas`, drinks): a swipeable gallery of photos and videos, and the menu for
   milkshakes, matcha and coffee.
3. **Por encargo** (`#encargos`, orders): same structure as drinks, with the gallery, the trays
   and a button to order by Instagram message.
4. **The strawberries** and **the chocolate** (`#origen`, `#chocolate`): local strawberries and
   Belgian Callebaut chocolate, with the chocolate fountain video. A gradient leads from chocolate
   brown into the teal of the wall.
5. **About us** (`#nosotras`): the photo in the shop with the brand's oval seal stamped in gold,
   the text in paragraphs and a handwritten sign-off.
6. **Del día a día** (`#instagram`, day to day): photo mosaic that opens the Instagram profile.
7. **FAQ** (`#preguntas`): animated accordions.
8. **Visit us** (`#visita`): address, opening hours, Google Maps button, map (loads on tap) and an
   illustration of the shopfront.
9. **Footer**: address, Instagram, small links to the legal notice and privacy policy, and credit.

**Top bar:** appears once the hero ends. On phones, logo and burger (full-screen panel). From 1100 px
wide, the sections inline with an underline marking the one in view, and "Visítanos" as a button.

**Galleries** (drinks and orders, the `galeria()` macro in the template): each item is a photo or
a video, cropped to 3:4. On phones they are swiped; with a mouse, arrows appear below
(`js/carrusel.js`).

**Videos** (`js/videos.js`): muted and looping. They download only when close to the screen and
play only while visible. With "reduce motion" on, the still image is shown.

## The hero

The hero takes `--hero-run` (300vh) of scrolling and stays pinned (sticky) meanwhile. Depending on
how far you have scrolled, a different frame is drawn on a `<canvas>`, so the animation moves
forwards and backwards with your finger or wheel. A `<video>` isn't used because seeking with
`currentTime` stutters, especially on iPhone.

The video sits centred behind the logo and the chocolate pours from the top. The video is zoomed
in (keeping its top edge) so the strawberry and "Desliza" sit centred below the logo, and it
zooms back out while the tagline appears.

Sequence (constants at the top of `js/hero.js`; distances are in screen heights):

1. The hero stays pinned for 2 screens of scrolling while the video plays.
2. About halfway through (from 1 to 0.6 screens before it releases, `CLOSE`), the tagline and
   buttons appear while the chocolate is still pouring; the video zooms out and the strawberry
   moves up just enough not to be covered.
3. The hero releases shortly before the animation ends. The last frames play while it scrolls up
   with the logo (`ANIM_OVERRUN`, 0.3 screens).
4. Once the bottom of the hero rises above 60% of the screen (`BAR_AT`), the bar (symbol,
   horizontal logo and burger) slides in from the top. It hides again if you scroll back up.

Other details:
- Frames load coarse to fine: every 16th first, then the ones in between. Even a fast scroll
  right after the page opens shows the whole sequence.
- The hero background uses the video's flat colour, so the video has no visible edges. On wide
  screens, the sides of the frame fade out.
- With `prefers-reduced-motion` or without JavaScript, the last frame is shown with no scrolling.

## Changing the hero video

```
scripts/extraer-frames.sh path/to/video.mp4 30-156          # frames 30 to 156
scripts/extraer-frames.sh path/to/video.mp4 156             # frames 1 to 156
scripts/extraer-frames.sh path/to/video.mp4 0               # the whole video
scripts/extraer-frames.sh path/to/video.mp4 30-156 75 1080  # higher quality and resolution
```

The current video uses `30-156`; the first frames were dropped because the chocolate took too long
to appear. Files keep their original number (0030.webp…) and the manifest stores the first one in
`start`.

It needs `ffmpeg`. The script replaces the frames, the poster and the manifest. The JS reads the
background colour from the manifest; for the no-JS version to match too, copy the colour the
script prints into `--hero-bg` (in `css/styles.css`).

For a video to work well in the hero:
- A flat, even background throughout. If the background moves or changes colour, the edge of the
  video will show against the page.
- Portrait (9:16) or 3:4.
- About 8–10 s at 24 fps, which is about 200–240 frames and 3–5 MB.

## SEO and GEO

The site is set up for Google (local SEO) and for AI assistants (ChatGPT, Perplexity, Gemini,
Google's AI Mode…) to find the shop and quote it accurately (GEO, generative engine optimisation).

- **`<head>`:** title, description, canonical URL, sharing cards (`assets/og/og.jpg`) and the
  shop's coordinates.
- **Structured data (JSON-LD):** the shop (`FoodEstablishment`) with address, coordinates, opening
  hours, Instagram and how to order; the full menu with prices (`Menu`); the website; and the FAQ
  (`FAQPage`).
- **FAQ:** short, concrete answers, which is what AI assistants quote most.
- **`llms.txt`:** a plain-text summary of the shop for AI assistants.
- **`robots.txt` and `sitemap.xml`:** the first lets search engines and AI crawlers in.

## Legal and privacy

- **Legal notice** (`aviso-legal.html`) and **privacy and cookies** (`privacidad.html`) are
  generated from the owner's details in `content/tienda.yml` (`titular`, `nif` and `email`);
  the shop's address is used as the address, which the LSSI accepts as a permanent establishment.
  **Until the three are filled in, they are not published**
  and their footer links don't appear; `build.py` warns about it. They are filled in under Pages
  CMS › Tienda.
- **No cookies or tracking:** the site uses no cookies, and fonts, photos and videos are served from
  the site itself, so no cookie banner is needed.
- **Visit statistics:** Cloudflare Web Analytics (free, no cookies, doesn't identify anyone, so no
  banner either). It is switched on by adding the token in Pages CMS › Portada y Google; the
  privacy policy adds the paragraph explaining it. To get the token: free account at
  https://dash.cloudflare.com › Analytics & Logs › Web Analytics › Add a site › the site's current
  domain › copy the `token` value from the snippet. The Google map only loads if
  the visitor taps "Ver el mapa aquí" (`js/mapa.js`).
- **If anything third-party is added** (analytics, a YouTube video, an Instagram widget…), review
  the privacy policy and, if it sets cookies, add a consent notice.
- The legal pages are `noindex`, so they stay out of Google.
- The texts are a reasonable starting point, but should be reviewed by an accountant or lawyer.

## Client presentation

`presentacion/index.html` is the presentation of the site concept, at /presentacion/. It is a scroll
story: on the right, a phone shows the real site (the site's own home page in an iframe) and moves with
each chapter. Keys: ↓ or space to advance, N for speaker notes, P to use the site inside the phone (or
tap the phone) and F for full screen.

- It is a static file: `build.py` copies it as is and does not read `content/`. Prices and texts are those
  of 29/10/2026; if they change a lot, edit them by hand in the file.
- It has `noindex`, is not in the sitemap and the site does not link to it. It is still public: anyone
  with the link can see it, speaker notes included (they are in the source).
- It drives the iframe through the site's ids and classes (`#carta`, `.paso.p2`, `#bebidas .strip`,
  `.faq-item`, `#visita`…). If they change in the template, check the presentation.

## Known issues and fixes

| Symptom | Cause and fix |
|---|---|
| The site shows the README | Pages is set to "Deploy from a branch". Switch it to **GitHub Actions** (see [Publishing](#publishing)). |
| "413 failed to upload file" in Pages CMS | The hosted version rejects files over about 3 MB (it runs on Vercel, which limits requests to 4.5 MB, and uploads are base64-encoded). Upload the file through GitHub (*Add file › Upload files*, up to 25 MB) into `assets/video` or `assets/img`, then pick it in the CMS. |
| Pressing save in Pages CMS does nothing | A field inside a collapsed item has an error. Use *Expand all* to find it in red. |
| "Expected string, received number" | A stored value doesn't match the field type (see [Pages CMS](#pages-cms)). |
| Publishing fails | In **Actions**, open the failed run: the `python build.py` step says in Spanish which value is wrong. |
| A run shows as "cancelled" | Another change arrived right after. The next run includes everything. |

## To do

**Content to confirm with the shop**
- Allergens for the Chocolate Dubái and Chocolate Tokyo creams. Until then, "Monta tu vaso" asks
  customers to check in the shop. Once known: Pages CMS › Monta tu vaso › cremas, untick
  "Alérgenos sin confirmar" and pick them.
- Tray prices: taken from the Instagram post of 9 May.
- Allergen no. 7: the printed menu says "frutos de cáscara" (tree nuts) in Spanish and "peanuts"
  in English.
- "About us" text: confirm the phrase "cada vaso montado al momento, a tu gusto".
- Review prices and menu before announcing the site.

**Search ranking and good practice** (review of 28/10/2026, by impact)

*Off the site*
- Google Business profile: name, address and hours identical to the site; categories (dessert
  shop, café); website linked; photos and menu; reply to reviews.
- Bing Places (ChatGPT searches with Bing) and Apple Business Connect (Siri, Apple Maps).
- TripAdvisor and Yelp. Ask customers for reviews.
- Mentions in Salamanca blogs, guides and local press.
- Link to the site in the Instagram bio.

*Legal*
- Replace the `[…]` placeholders for owner and tax ID in Pages CMS › Tienda
  (the legal pages are published with them for now; `build.py` warns while they remain). Have
  the texts reviewed.

*Technical, when the domain is connected*
- `CNAME` in the repository, HTTPS and a www to non-www redirect.
- Google Search Console and Bing Webmaster Tools, with the sitemap.
- A custom 404 page.
- Cloudflare Web Analytics: add the new domain and update the token if needed.

*Missing data*
- The shop's phone and email. Pages CMS › Tienda has fields for them; once filled in, they appear
  in "Visit us" and in the data for Google.

*Opportunities*
- An English version of the site (tourists and Erasmus students).
- An orders page (Valentine's Day, Mother's Day…).
- A lighter hero on mobile: load the frames after the rest of the page, or fewer of them when
  data saving is on.
- Pin `runs-on: ubuntu-24.04` in the workflow. GitHub is moving `ubuntu-latest` to Ubuntu 26 and
  warns about it on every run.
- Old unused photos in `assets/img/` (`batido-matcha`, `brocheta`, `cajas`, `tarta-cajas`): reuse
  or delete them.
