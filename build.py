#!/usr/bin/env python3
"""Genera la web de Fresas y Chocolate en _site/ a partir de content/*.yml y src/.

    python3 build.py            # genera _site/
    SITE_URL=https://... python3 build.py

Necesita jinja2, pyyaml y pillow (pip install -r requirements.txt). Si el contenido tiene algún
error (un precio que no es un número, una foto que no existe, una foto sin texto alternativo…)
se para con un mensaje y no genera nada, así nunca se publica una web rota.
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

register_heif_opener()  # fotos HEIC del iPhone

ROOT = Path(__file__).resolve().parent
CONTENT, SRC, OUT = ROOT / 'content', ROOT / 'src', ROOT / '_site'
STATIC = ['css', 'js', 'assets', 'presentacion']  # presentacion/: la presentación para el cliente, tal cual
SITE = os.environ.get('SITE_URL', 'https://fresasychocolate.com/').rstrip('/') + '/'
I18N = yaml.safe_load((SRC / 'i18n.yml').read_text(encoding='utf-8'))  # textos fijos de la web, por idioma
MAX_IMG = 1600  # ancho máximo de las fotos publicadas

# Orden y nombres de los alérgenos de la carta (el número es el de la carta impresa).
ALERGENOS = ['gluten', 'leche', 'huevo', 'sésamo', 'soja', 'pistachos', 'frutos de cáscara',
             'avellanas', 'mantequilla', 'coco']
ALERGENOS_EN = {'gluten': 'Gluten', 'leche': 'Milk', 'huevo': 'Egg', 'sésamo': 'Sesame', 'soja': 'Soy',
                'pistachos': 'Pistachios', 'frutos de cáscara': 'Tree nuts', 'avellanas': 'Hazelnuts',
                'mantequilla': 'Butter', 'coco': 'Coconut'}
# Campos de texto que llevan traducción en content/*.yml con el sufijo _en (para avisar de los que faltan).
TRADUCIBLES = {'referencia', 'dias', 'lema', 'seo_titulo', 'seo_descripcion', 'titulo_principal', 'descripcion_negocio',
               'antetitulo', 'titulo', 'intro', 'pedir_titulo', 'nota_alergenos', 'nombre', 'nota', 'foto_alt', 'video_alt',
               'alt', 'detalle', 'como_encargar', 'boton', 'texto', 'firma', 'pregunta', 'respuesta', 'ingredientes',
               'especiales_titulo', 'especiales_nota', 'contacto_texto', 'financiacion'}
# Se traducen si hay `_en`, pero no es un fallo que falte (p. ej. reseñas de clientes en su idioma original).
OPCIONALES = {'resena'}
IDIOMAS = ('es', 'en')
DIAS = {'lunes': 'Monday', 'martes': 'Tuesday', 'miercoles': 'Wednesday', 'jueves': 'Thursday',
        'viernes': 'Friday', 'sabado': 'Saturday', 'domingo': 'Sunday'}

# Campos sin los que la web no tiene sentido; el resto son opcionales.
OBLIGATORIOS = [
    'tienda.nombre', 'tienda.calle', 'tienda.codigo_postal', 'tienda.ciudad', 'tienda.latitud', 'tienda.longitud',
    'tienda.google_maps', 'tienda.instagram', 'tienda.horario',
    'portada.seo_titulo', 'portada.seo_descripcion', 'portada.titulo_principal', 'portada.descripcion_negocio', 'portada.lema',
    'carta.titulo', 'carta.vaso.nombre', 'carta.vaso.precio', 'carta.vaso.foto', 'carta.cremas.titulo',
    'carta.cremas.grupos', 'carta.cremas.video', 'carta.cremas.video_portada', 'carta.toppings.titulo', 'carta.toppings.foto',
    'carta.toppings.grupos', 'bebidas.titulo', 'bebidas.grupos', 'encargos.titulo', 'encargos.bandejas', 'encargos.como_encargar',
    'historia.fresas.titulo', 'historia.fresas.foto', 'historia.chocolate.titulo', 'historia.chocolate.video',
    'historia.nosotras.titulo', 'historia.nosotras.foto', 'instagram.fotos', 'preguntas.titulo',
]

errores = []


def error(msg):
    errores.append(msg)


# ---------- contenido ----------

def cargar():
    c = {}
    for f in sorted(CONTENT.glob('*.yml')):
        try:
            c[f.stem] = yaml.safe_load(f.read_text(encoding='utf-8')) or {}
        except yaml.YAMLError as e:
            error(f'{f.name}: no se puede leer ({e})')
    return c


def localizar(obj, lang, faltan, ruta=''):
    """Copia del contenido con cada campo X sustituido por X_en (inglés). Anota en `faltan` los textos sin traducir."""
    if lang == 'es':
        return obj
    if isinstance(obj, list):
        return [localizar(v, lang, faltan, f'{ruta}[{i}]') for i, v in enumerate(obj)]
    if not isinstance(obj, dict):
        return obj
    raiz = ruta.split('.')[0].split('[')[0]
    out = {}
    for k, v in obj.items():
        if k.endswith('_en'):
            continue
        en = obj.get(k + '_en')
        traducible = (k in TRADUCIBLES and (raiz != 'tienda' or k in ('referencia', 'dias', 'financiacion'))
                      and (raiz != 'resenas' or k in ('antetitulo', 'titulo')))
        if isinstance(v, str) and v.strip() and (traducible or k in OPCIONALES):
            if isinstance(en, str) and en.strip():
                out[k] = en
            else:
                out[k] = v
                if traducible:
                    faltan.append(f'{ruta}.{k}'.lstrip('.'))
        else:
            out[k] = localizar(v, lang, faltan, f'{ruta}.{k}'.lstrip('.'))
    return out


def numero(v):
    """3.5, "3,50", "3,50 €" o "12" → float; None si no es un número."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace('€', '').strip().replace(',', '.'))
    except ValueError:
        return None


def precio(d, k, donde):
    """Valida el precio d[k] y lo deja como número para las plantillas."""
    v = numero(d.get(k))
    if v is None or v < 0:
        error(f'{donde}: el precio debe ser un número (por ejemplo 1,70), no "{d.get(k)}"')
        v = 0.0
    d[k] = v


def validar(c):
    for k in ['tienda', 'portada', 'carta', 'bebidas', 'encargos', 'historia', 'instagram', 'preguntas']:
        if k not in c:
            error(f'Falta el archivo content/{k}.yml')
    if errores:
        return
    for ruta_campo in OBLIGATORIOS:
        archivo, *claves = ruta_campo.split('.')
        v = c[archivo]
        for k in claves:
            v = v.get(k) if isinstance(v, dict) else None
        if v in (None, '', []):
            error(f'content/{archivo}.yml: falta "{".".join(claves)}"')
    if errores:
        return
    carta = c['carta']
    precio(carta['vaso'], 'precio', 'Monta tu vaso › vaso')
    for i, g in enumerate(carta['cremas'].get('grupos') or [], 1):
        precio(g, 'precio', f'Monta tu vaso › cremas, grupo {i}')
        for op in g.get('opciones') or []:
            for a in op.get('alergenos') or []:
                if a not in ALERGENOS:
                    error(f'Crema "{op.get("nombre")}": alérgeno desconocido "{a}"')
    for i, g in enumerate(carta['toppings'].get('grupos') or [], 1):
        precio(g, 'precio', f'Monta tu vaso › toppings, grupo {i}')
        for op in g.get('opciones') or []:
            for a in op.get('alergenos') or []:
                if a not in ALERGENOS:
                    error(f'Topping "{op.get("nombre")}": alérgeno desconocido "{a}"')
    for i, e in enumerate(carta.get('especiales') or [], 1):
        donde = f'Monta tu vaso › especiales › {e.get("nombre") or i}'
        for k in ('nombre', 'ingredientes'):
            if not str(e.get(k) or '').strip():
                error(f'{donde}: falta "{k}"')
        precio(e, 'precio', donde)
        for a in e.get('alergenos') or []:
            if a not in ALERGENOS:
                error(f'{donde}: alérgeno desconocido "{a}"')
        if e.get('foto') and not str(e.get('foto_alt') or '').strip():
            error(f'{donde}: falta la descripción de la foto')
        if not e.get('foto'):
            print(f'Aviso: el especial "{e.get("nombre")}" aún no tiene foto; se muestra un marcador.')
    for g in c['bebidas'].get('grupos') or []:
        for p in g.get('productos') or []:
            precio(p, 'precio', f'Bebidas › {g.get("titulo")} › {p.get("nombre")}')
    for b in c['encargos'].get('bandejas') or []:
        for t in b.get('tamanos') or []:
            precio(t, 'precio', f'Encargos › {b.get("titulo")} › {t.get("nombre")}')
    for sec in ('bebidas', 'encargos'):
        for i, f in enumerate(c[sec].get('fotos') or [], 1):
            if not f.get('foto') and not f.get('video'):
                error(f'{sec.capitalize()} › fotos y vídeos, elemento {i}: falta la foto o el vídeo')
            if not str(f.get('alt') or '').strip():
                error(f'{sec.capitalize()} › fotos y vídeos, elemento {i}: falta la descripción')
    r = c.get('resenas') or {}
    if r.get('valoracion') not in (None, ''):
        v = numero(r['valoracion'])
        if v is None or not 1 <= v <= 5:
            error(f'Reseñas: la valoración debe ser un número entre 1 y 5, no "{r["valoracion"]}"')
        r['valoracion_num'] = v
    if r.get('total') not in (None, ''):
        v = numero(r['total'])
        if v is None or v < 1 or v != int(v):
            error(f'Reseñas: el número de reseñas debe ser un entero, no "{r["total"]}"')
        r['total_num'] = int(v) if v else None
        if r['total_num']:
            # Se enseña «Más de N» redondeado hacia abajo: sigue siendo verdad aunque lleguen reseñas nuevas.
            paso = 50 if r['total_num'] > 100 else 25 if r['total_num'] > 50 else 10
            r['total_redondeado'] = (r['total_num'] - 1) // paso * paso
    for i, it in enumerate(r.get('lista') or [], 1):
        e = numero(it.get('estrellas'))
        if e is None or e not in (1, 2, 3, 4, 5):
            error(f'Reseñas, reseña {i}: las estrellas deben ser de 1 a 5, no "{it.get("estrellas")}"')
        it['estrellas'] = int(e) if e else 5
        for k in ('nombre', 'resena'):
            if not str(it.get(k) or '').strip():
                error(f'Reseñas, reseña {i}: falta "{k}"')
    for k in ('latitud', 'longitud'):
        v = numero(c['tienda'].get(k))
        if v is None:
            error(f'Tienda: la {k} debe ser un número, no "{c["tienda"].get(k)}"')
        c['tienda'][k] = v
    for h in c['tienda'].get('horario') or []:
        # Sin comillas, YAML lee 14:00 como un número en base 60 (840): se vuelve a escribir como hora.
        for k in ('abre', 'cierra'):
            if isinstance(h.get(k), int) and not isinstance(h.get(k), bool):
                h[k] = f'{h[k] // 60:02d}:{h[k] % 60:02d}'
        for d in h.get('dias_semana') or []:
            if d not in DIAS:
                error(f'Horario "{h.get("dias")}": día desconocido "{d}"')
        for k in ('abre', 'cierra'):
            if not re.fullmatch(r'\d{2}:\d{2}', str(h.get(k, ''))):
                error(f'Horario "{h.get("dias")}": la hora "{h.get(k)}" debe ser como 14:00')


# ---------- utilidades para las plantillas ----------

def euros(v, lang='es'):
    if lang == 'en':
        return '€' + f'{float(v):,.2f}'
    return f'{float(v):,.2f}'.replace(',', ' ').replace('.', ',').replace(' ', '.') + ' €'


def euros_corto(v, lang='es'):
    v = float(v)
    if v.is_integer():
        return f'€{int(v)}' if lang == 'en' else f'{int(v)} €'
    return euros(v, lang)


def fecha(d, lang='es'):
    if lang == 'en':
        meses = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                 'October', 'November', 'December']
        return f'{meses[d.month - 1]} {d.day}, {d.year}'
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre',
             'octubre', 'noviembre', 'diciembre']
    return f'{d.day} de {meses[d.month - 1]} de {d.year}'


def lista(items, y='y'):
    items = [i for i in items if i]
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + f' {y} ' + items[-1] if items else ''


def enlaces(texto):
    """Texto plano con enlaces [texto](url) → HTML seguro."""
    def a(m):
        t, u = m.group(1), m.group(2)
        ext = u.startswith('http')
        return f'<a href="{u}"' + (' target="_blank" rel="noopener"' if ext else '') + f'>{t}</a>'
    return Markup(re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', a, html.escape(str(texto), quote=False)))


def sin_enlaces(texto):
    return re.sub(r'\[([^\]]+)\]\([^)\s]+\)', r'\1', str(texto))


def ruta(p):
    return str(p or '').lstrip('/')


_imgs = {}


def img(path, alt=None, donde=''):
    """Devuelve src/width/height de una foto; si es grande o no es WebP, publica una versión WebP."""
    p = ruta(path)
    if alt is not None and not str(alt).strip():
        error(f'{donde or p}: falta el texto alternativo de la foto')
    if p in _imgs:
        return _imgs[p]
    src = ROOT / p
    if not src.is_file():
        error(f'{donde or p}: no existe la foto "{p}"')
        _imgs[p] = {'src': p, 'width': 1, 'height': 1}
        return _imgs[p]
    try:
        im = Image.open(src)
    except (UnidentifiedImageError, OSError):
        error(f'{donde or p}: "{p}" no es una foto que se pueda abrir (JPG, PNG, WebP o HEIC)')
        _imgs[p] = {'src': p, 'width': 1, 'height': 1}
        return _imgs[p]
    with im:
        w, h = im.size
        if src.suffix.lower() == '.webp' and w <= MAX_IMG:
            _imgs[p] = {'src': p, 'width': w, 'height': h}
        else:
            out = Path(p).with_suffix('.webp')
            (OUT / p).unlink(missing_ok=True)  # el original pesado no se publica
            if w > MAX_IMG:
                h, w = round(h * MAX_IMG / w), MAX_IMG
            dest = OUT / out
            dest.parent.mkdir(parents=True, exist_ok=True)
            im = im.convert('RGB')
            im.thumbnail((w, h))
            im.save(dest, 'WEBP', quality=80)
            _imgs[p] = {'src': str(out), 'width': w, 'height': h}
    return _imgs[p]


MAX_VIDEO = 12 * 1024 * 1024  # los MP4 más pesados (o en otro formato) se recomprimen
_videos = {}


def video(path, portada=None, donde=''):
    """Publica un vídeo para la web: MP4 sin sonido, como mucho 720 px de ancho, y su imagen fija.

    Si el vídeo ya es un MP4 ligero se publica tal cual. Si no hay `portada`, se saca un fotograma
    del propio vídeo. Hace falta ffmpeg solo cuando hay que convertir algo."""
    p = ruta(path)
    if p in _videos:
        return _videos[p]
    src = ROOT / p
    res = {'src': p, 'poster': img(portada, donde=donde)['src'] if portada else ''}
    _videos[p] = res
    if not src.is_file():
        error(f'{donde or p}: no existe el vídeo "{p}"')
        return res
    ligero = src.suffix.lower() == '.mp4' and src.stat().st_size <= MAX_VIDEO
    if ligero and portada:
        return res
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        error(f'{donde or p}: hace falta ffmpeg para preparar el vídeo')
        return res
    run = lambda *a: subprocess.run([ffmpeg, '-nostdin', '-loglevel', 'error', '-y', *a], check=True)
    try:
        if not ligero:
            out = Path(p).with_suffix('.mp4')
            (OUT / p).unlink(missing_ok=True)  # el original pesado no se publica
            (OUT / out).parent.mkdir(parents=True, exist_ok=True)
            run('-i', str(src), '-an', '-vf', "scale='min(720,iw)':-2,fps=30,format=yuv420p",
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '27', '-movflags', '+faststart', str(OUT / out))
            res['src'] = str(out)
        if not portada:
            out = Path(p).with_name(Path(p).stem + '-portada.webp')
            (OUT / out).parent.mkdir(parents=True, exist_ok=True)
            run('-ss', '1', '-i', str(src), '-frames:v', '1', '-vf', "scale='min(720,iw)':-2",
                '-c:v', 'libwebp', '-quality', '75', str(OUT / out))
            res['poster'] = str(out)
    except subprocess.CalledProcessError:
        error(f'{donde or p}: no se ha podido convertir el vídeo')
    return res


def svg(nombre, etiqueta=None):
    """SVG en línea. Decorativo por defecto; con `etiqueta`, se anuncia como imagen con ese nombre."""
    s = (SRC / 'svg' / f'{nombre}.svg').read_text(encoding='utf-8')
    if etiqueta:
        s = s.replace('aria-hidden="true" focusable="false"', f'role="img" aria-label="{html.escape(etiqueta)}"', 1)
    return Markup(s)


# ---------- datos derivados ----------

def preguntas_auto(c, lang='es'):
    """Preguntas automáticas; si hay especiales de la casa, añade una sobre ellos tras la del precio."""
    preguntas = _preguntas_base(c, lang)
    esp = c['carta'].get('especiales') or []
    if esp:
        en = lang == 'en'
        eur = lambda v: euros(v, lang)
        minus = lambda x: x[0].lower() + x[1:]
        nombres = lista([e['nombre'] for e in esp], 'and' if en else 'y')
        detalle = ' '.join(f'{e["nombre"]}: {minus(e["ingredientes"])} ({eur(e["precio"])}).' for e in esp)
        nota = c['carta'].get('especiales_nota') or ''
        if en:
            q = {'pregunta': f'Do you have {esp[0]["nombre"]} chocolate strawberries?',
                 'respuesta': f'Yes. Our house specials are {nombres}. {detalle} {nota}'.strip()}
        else:
            q = {'pregunta': f'¿Tenéis fresas con chocolate {esp[0]["nombre"]}?',
                 'respuesta': f'Sí. Nuestros especiales de la casa son {nombres}. {detalle} {nota}'.strip()}
        preguntas.insert(3, q)
    return preguntas


def _preguntas_base(c, lang='es'):
    en = lang == 'en'
    t, carta, enc, beb = c['tienda'], c['carta'], c['encargos'], c['bebidas']
    eur, eurc = (lambda v: euros(v, lang)), (lambda v: euros_corto(v, lang))
    y, o = ('and', 'or') if en else ('y', 'o')
    vaso = float(carta['vaso']['precio'])
    cr = [float(g['precio']) for g in carta['cremas']['grupos']]
    tops = [float(g['precio']) for g in carta['toppings']['grupos']]
    cremas = [o_['nombre'] for g in carta['cremas']['grupos'] for o_ in g['opciones']]
    cap = lambda x: x[0].upper() + x[1:]
    minus = lambda x: x[0].lower() + x[1:]
    if en:  # los días ya vienen con mayúscula
        horario = cap('; '.join(f'{h["dias"]}, {h["abre"]} to {h["cierra"]}' for h in t['horario'])) + '.'
    else:
        horario = cap('; '.join(f'{h["dias"].lower()}, de {h["abre"]} a {h["cierra"]}' for h in t['horario'])) + '.'
    if len({d for h in t['horario'] for d in h['dias_semana']}) == 7:
        horario = ('We are open every day. ' if en else 'Abrimos todos los días. ') + horario
    bandejas = []
    for b in enc['bandejas']:
        if b.get('tamanos'):
            bandejas.append(f'{b["titulo"].lower()} ({lista([eurc(x["precio"]) for x in b["tamanos"]], y)})')
        else:
            bandejas.append(b['titulo'].lower())
    bebidas = '; '.join(f'{g["titulo"].lower()} ({lista([minus(p["nombre"]) for p in g["productos"]], y)})' for g in beb['grupos'])
    calle = minus(t['calle'])
    ref = f', {t["referencia"]}' if t.get('referencia') else ''
    if en:
        precio_vaso = f'The {carta["vaso"]["nombre"].lower()} costs {eur(vaso)}. '
        if min(cr) == max(cr):
            precio_vaso += f'The chocolate or cream adds {eur(min(cr))}, so a cup of strawberries with chocolate comes to {eur(vaso + min(cr))}.'
        else:
            precio_vaso += (f'The chocolate or cream adds between {eur(min(cr))} and {eur(max(cr))} depending on which you choose, '
                            f'so a cup of strawberries with chocolate starts at {eur(vaso + min(cr))}.')
        if tops:
            precio_vaso += f' With a topping, between {eur(vaso + min(cr) + min(tops))} and {eur(vaso + max(cr) + max(tops))}.'
        precio_vaso += f' Chocolates and creams to choose from: {lista(cremas, o)}.'
        return [
            {'pregunta': f'Where is {t["nombre"]} in {t["ciudad"]}?',
             'respuesta': f'At {t["calle"]} ({t["codigo_postal"]} {t["ciudad"]}), in the city centre{ref}. [See it on Google Maps]({t["google_maps"]}).'},
            {'pregunta': 'What are the opening hours?', 'respuesta': horario},
            {'pregunta': 'How much is a cup of chocolate-covered strawberries?', 'respuesta': precio_vaso},
            {'pregunta': 'Can I order trays of chocolate-covered strawberries?',
             'respuesta': f'Yes. There are trays: {lista(bandejas, y)}. {enc["como_encargar"]} [Message us on Instagram](https://ig.me/m/{t["instagram"]}).'},
            {'pregunta': 'What else can I have?', 'respuesta': 'Besides the cups of strawberries: ' + bebidas + '.'},
        ]
    precio_vaso = f'El {carta["vaso"]["nombre"].lower()} cuesta {eur(vaso)}. '
    if min(cr) == max(cr):
        precio_vaso += f'La crema suma {eur(min(cr))}, así que un vaso de fresas con chocolate sale por {eur(vaso + min(cr))}.'
    else:
        precio_vaso += (f'La crema suma entre {eur(min(cr))} y {eur(max(cr))} según la que elijas, '
                        f'así que un vaso de fresas con chocolate sale desde {eur(vaso + min(cr))}.')
    if tops:
        precio_vaso += f' Con topping, entre {eur(vaso + min(cr) + min(tops))} y {eur(vaso + max(cr) + max(tops))}.'
    precio_vaso += f' Cremas a elegir: {lista(cremas, o)}.'
    return [
        {'pregunta': f'¿Dónde está {t["nombre"]} en {t["ciudad"]}?',
         'respuesta': f'En la {calle} ({t["codigo_postal"]} {t["ciudad"]}), en el centro{ref}. [Ver en Google Maps]({t["google_maps"]}).'},
        {'pregunta': '¿Qué horario tiene?', 'respuesta': horario},
        {'pregunta': '¿Cuánto cuesta un vaso de fresas con chocolate?', 'respuesta': precio_vaso},
        {'pregunta': '¿Se pueden encargar bandejas de fresas con chocolate?',
         'respuesta': f'Sí. Hay bandejas {lista(bandejas, y)}. {enc["como_encargar"]} [Escríbenos por Instagram](https://ig.me/m/{t["instagram"]}).'},
        {'pregunta': '¿Qué más se puede tomar?', 'respuesta': 'Además de los vasos de fresas: ' + bebidas + '.'},
    ]


def jsonld(c, faq, lang, home):
    en = lang == 'en'
    u = I18N[lang]['ld']
    il = 'en' if en else 'es-ES'
    t, carta = c['tienda'], c['carta']
    ig = f'https://www.instagram.com/{t["instagram"]}/'

    def item(nombre, p, desc=None):
        d = {'@type': 'MenuItem', 'name': nombre, 'offers': {'@type': 'Offer', 'price': f'{float(p):.2f}', 'priceCurrency': 'EUR'}}
        if desc:
            d['description'] = desc
        return d
    sup = u['suplemento']
    secciones = [
        {'@type': 'MenuSection', 'name': carta['vaso']['nombre'], 'description': carta['vaso'].get('nota', ''),
         'hasMenuItem': [item(carta['vaso']['nombre'], carta['vaso']['precio'])]},
        {'@type': 'MenuSection', 'name': u['cremas'],
         'hasMenuItem': [item(o['nombre'], g['precio'], sup) for g in carta['cremas']['grupos'] for o in g['opciones']]},
        {'@type': 'MenuSection', 'name': u['toppings'],
         'hasMenuItem': [item(o['nombre'], g['precio'], sup) for g in carta['toppings']['grupos'] for o in g['opciones']]},
    ]
    if carta.get('especiales'):
        secciones.insert(1, {'@type': 'MenuSection', 'name': carta.get('especiales_titulo') or u['especiales'],
                             'hasMenuItem': [item(e['nombre'], e['precio'], e['ingredientes']) for e in carta['especiales']]})
    for g in c['bebidas']['grupos']:
        secciones.append({'@type': 'MenuSection', 'name': g['titulo'],
                          'hasMenuItem': [item(p['nombre'], p['precio'], p.get('detalle')) for p in g['productos']]})
    secciones.append({'@type': 'MenuSection', 'name': u['bandejas'], 'description': c['encargos']['como_encargar'],
                      'hasMenuItem': [item(f'{b["titulo"]} {x["nombre"].lower()}', x['precio'], x.get('detalle') or b.get('nota'))
                                      for b in c['encargos']['bandejas'] for x in b.get('tamanos') or []]})
    tienda = {
        '@type': ['FoodEstablishment', 'CafeOrCoffeeShop'], '@id': home + '#tienda',
        'name': t['nombre'], 'alternateName': f'{t["nombre"]} {t["ciudad"]}',
        'description': c['portada']['descripcion_negocio'],
        'url': home, 'logo': SITE + 'assets/og/logo.png',
        'image': [SITE + 'assets/og/og-pronto.jpg', SITE + img(carta['vaso']['foto'])['src'], SITE + img(c['historia']['nosotras']['foto'])['src']],
        'address': {'@type': 'PostalAddress', 'streetAddress': t['calle'], 'postalCode': str(t['codigo_postal']),
                    'addressLocality': t['ciudad'], 'addressRegion': t['ciudad'], 'addressCountry': 'ES'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': t['latitud'], 'longitude': t['longitud']},
        'hasMap': f'https://www.google.com/maps?cid={t["google_maps_cid"]}' if t.get('google_maps_cid') else t['google_maps'],
        'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': [DIAS[d] for d in h['dias_semana']],
                                       'opens': h['abre'], 'closes': h['cierra']} for h in t['horario']],
        'priceRange': '€', 'currenciesAccepted': 'EUR',
        'servesCuisine': u['cocina'],
        'hasMenu': {'@id': home + '#carta'}, 'areaServed': {'@type': 'City', 'name': t['ciudad']},
        'foundingDate': str(t.get('abierta_desde', '')), 'sameAs': [ig],
        'potentialAction': {'@type': 'OrderAction', 'target': f'https://ig.me/m/{t["instagram"]}', 'description': u['encargar']},
    }
    real = lambda v: bool(v) and not str(v).strip().startswith('[')  # sin marcadores provisionales
    if real(t.get('telefono')):
        tienda['telephone'] = t['telefono']
    if real(t.get('email')):
        tienda['email'] = t['email']
    grafo = [
        tienda,
        {'@type': 'Menu', '@id': home + '#carta', 'name': u['carta_de'].format(nombre=t['nombre']), 'inLanguage': u['inlanguage'], 'hasMenuSection': secciones},
        {'@type': 'WebSite', '@id': home + '#web', 'url': home, 'name': t['nombre'], 'inLanguage': il, 'publisher': {'@id': home + '#tienda'}},
        {'@type': 'WebPage', '@id': home + '#pagina', 'url': home, 'name': c['portada']['seo_titulo'], 'isPartOf': {'@id': home + '#web'},
         'about': {'@id': home + '#tienda'}, 'inLanguage': il, 'primaryImageOfPage': SITE + 'assets/og/og-pronto.jpg'},
        {'@type': 'FAQPage', '@id': home + '#preguntas', 'isPartOf': {'@id': home + '#web'}, 'inLanguage': il,
         'mainEntity': [{'@type': 'Question', 'name': q['pregunta'],
                         'acceptedAnswer': {'@type': 'Answer', 'text': sin_enlaces(q['respuesta'])}} for q in faq]},
    ]
    s = json.dumps({'@context': 'https://schema.org', '@graph': grafo}, ensure_ascii=False, separators=(',', ':'))
    return Markup(s.replace('</', '<\\/'))


# ---------- generación ----------

def nombre_pagina(clave_pagina, lang, clave):
    """Nombre del archivo de cada página en cada idioma (la web completa se llama <clave>.html en modo «próximamente»)."""
    nombres = {'inicio': ('index.html', 'index.html'), 'completa': (f'{clave}.html', f'{clave}.html'),
               'aviso': ('aviso-legal.html', 'legal-notice.html'), 'privacidad': ('privacidad.html', 'privacy.html')}
    return nombres[clave_pagina][IDIOMAS.index(lang)]


def url_pagina(nombre, lang):
    return SITE + ('en/' if lang == 'en' else '') + ('' if nombre == 'index.html' else nombre)


def render_idioma(lang, cl, faltan_en, pronto, clave, legal):
    """Genera todas las páginas de un idioma: en la raíz (es) o en /en/ (en)."""
    es = lang == 'es'
    ui = I18N[lang]
    destino = OUT if es else OUT / 'en'
    destino.mkdir(exist_ok=True)
    home = url_pagina('index.html', lang)
    env = Environment(loader=FileSystemLoader(SRC), autoescape=True,
                      trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    env.filters.update(euros=lambda v: euros(v, lang), euros_corto=lambda v: euros_corto(v, lang),
                       un_decimal=lambda v: f'{float(v):.1f}'.replace('.', ',' if es else '.'),
                       enlaces=enlaces, sin_enlaces=sin_enlaces, ruta=ruta)
    faq = preguntas_auto(cl, lang) + list(cl['preguntas'].get('preguntas') or [])
    orden = ALERGENOS if es else [ALERGENOS_EN[a] for a in ALERGENOS]
    al_nombres = lambda lista_: [orden[i] for i, a in enumerate(ALERGENOS) if a in (lista_ or [])]
    env.globals.update(img=img, video=video, svg=svg, site=SITE, home=home, lang=lang, ui=ui, base='' if es else '../',
                       alergenos_orden=orden, al_nombres=al_nombres, year=dt.date.today().year,
                       hoy=dt.date.today().isoformat(), hoy_texto=fecha(dt.date.today(), lang), faq=faq,
                       noindex=False, legal=legal, ui_js=Markup(json.dumps(ui['js'], ensure_ascii=False).replace('</', '<\\/')),
                       **cl)
    # El JSON-LD usa img(), que también registra errores de fotos.
    env.globals['jsonld'] = jsonld(cl, faq, lang, home)

    def pag(id_pagina):
        """Datos de cada página para la plantilla: canónica, hreflang y enlace al otro idioma."""
        n_es, n_en = nombre_pagina(id_pagina, 'es', clave), nombre_pagina(id_pagina, 'en', clave)
        raiz = lambda n: '' if n == 'index.html' else n
        otro = ('en/' + raiz(n_en)) if es else ('../' + raiz(n_es))
        return {'es': url_pagina(n_es, 'es'), 'en': url_pagina(n_en, 'en'), 'canonica': url_pagina(n_es if es else n_en, lang),
                'otro': otro or './', 'otro_lang': 'en' if es else 'es'}

    paginas = []  # (archivo, plantilla, autoescape, id de página)
    sufijo = '' if es else '.en'
    if pronto:
        if es:
            paginas += [('index.html', 'pronto.html.j2', True, None), ('robots.txt', 'robots-cerrado.txt.j2', False, None)]
        env.globals['noindex'] = True
        n = nombre_pagina('completa', lang, clave)
        env.autoescape = True
        env.globals['pag'] = pag('completa')
        (destino / n).write_text(env.get_template('index.html.j2').render(), encoding='utf-8')
        env.globals['noindex'] = False
    else:
        paginas.append(('index.html', 'index.html.j2', True, 'completa_inicio'))
        if es:
            paginas += [('robots.txt', 'robots.txt.j2', False, None), ('sitemap.xml', 'sitemap.xml.j2', True, None)]
        paginas.append(('llms.txt', f'llms{sufijo}.txt.j2', False, None))
    if legal:
        paginas += [(nombre_pagina('aviso', lang, clave), f'aviso-legal{sufijo}.html.j2', True, 'aviso'),
                    (nombre_pagina('privacidad', lang, clave), f'privacidad{sufijo}.html.j2', True, 'privacidad')]
    for nombre, plantilla, autoescape, id_pagina in paginas:
        env.autoescape = autoescape
        if id_pagina:
            env.globals['pag'] = pag('inicio' if id_pagina == 'completa_inicio' else id_pagina)
        (destino / nombre).write_text(env.get_template(plantilla).render(), encoding='utf-8')


def main():
    c = cargar()
    validar(c)
    if errores:
        sys.exit('No se ha generado la web:\n  - ' + '\n  - '.join(errores))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for d in STATIC:
        shutil.copytree(ROOT / d, OUT / d)

    t = c['tienda']
    # Páginas legales: solo si están los datos del titular, para no publicar un aviso legal a medias.
    legal = all(str(t.get(k) or '').strip() for k in ('titular', 'nif', 'email'))
    provisionales = [k for k in ('titular', 'nif', 'email', 'telefono')
                     if str(t.get(k) or '').strip().startswith('[')]
    if provisionales:
        print(f'Aviso: datos provisionales en content/tienda.yml ({", ".join(provisionales)}); sustitúyelos antes de anunciar la web.')
    if not legal:
        print('Aviso: faltan titular, NIF o email en content/tienda.yml; no se publican las páginas legales.')

    # Modo «próximamente»: la portada pública es solo la pantalla de espera y la web completa queda en
    # una dirección secreta, sin indexar. Sin sitemap ni llms.txt, y robots.txt cierra el paso.
    p = c.get('pronto') or {}
    pronto = bool(p.get('activo'))
    clave = None
    if pronto:
        clave = re.sub(r'[^a-z0-9-]', '', str(p.get('clave') or '').lower())
        if len(clave) < 8:
            error('content/pronto.yml: "clave" debe tener al menos 8 letras, números o guiones')
        else:
            print(f'Modo próximamente ACTIVO. Web completa en {SITE}{clave}.html (inglés: {SITE}en/{clave}.html)')

    faltan = []
    en = localizar(c, 'en', faltan)
    if faltan:
        print(f'Aviso: {len(faltan)} textos sin traducción al inglés (se usa el español). Por ejemplo: ' + ', '.join(faltan[:6]))
    if not errores:
        render_idioma('es', c, faltan, pronto, clave, legal)
        render_idioma('en', en, faltan, pronto, clave, legal)
    if errores:
        shutil.rmtree(OUT)
        sys.exit('No se ha generado la web:\n  - ' + '\n  - '.join(errores))
    # La presentación es HTML suelto (no plantilla): solo se le añaden las estadísticas.
    pres = OUT / 'presentacion' / 'index.html'
    if pres.exists():
        env = Environment(loader=FileSystemLoader(SRC), autoescape=True, trim_blocks=True, lstrip_blocks=True)
        env.globals.update(portada=c['portada'])
        snippet = env.get_template('analitica.html.j2').render()
        doc = pres.read_text(encoding='utf-8').replace('</body>', snippet + '</body>', 1)
        if pronto and clave:  # con «Muy pronto» activo, el móvil de la presentación enseña la web completa
            doc = doc.replace('id="site" src="../"', f'id="site" src="../{clave}.html"', 1)
        pres.write_text(doc, encoding='utf-8')
    (OUT / '.nojekyll').write_text('')
    print(f'Web generada en {OUT.relative_to(ROOT)}/ ({SITE})')


if __name__ == '__main__':
    main()
