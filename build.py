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
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from PIL import Image

ROOT = Path(__file__).resolve().parent
CONTENT, SRC, OUT = ROOT / 'content', ROOT / 'src', ROOT / '_site'
STATIC = ['css', 'js', 'assets']
SITE = os.environ.get('SITE_URL', 'https://fresasychocolate.com/').rstrip('/') + '/'
MAX_IMG = 1600  # ancho máximo de las fotos publicadas

# Orden y nombres de los alérgenos de la carta (el número es el de la carta impresa).
ALERGENOS = ['gluten', 'leche', 'huevo', 'sésamo', 'soja', 'pistachos', 'frutos de cáscara',
             'avellanas', 'mantequilla', 'coco']
DIAS = {'lunes': 'Monday', 'martes': 'Tuesday', 'miercoles': 'Wednesday', 'jueves': 'Thursday',
        'viernes': 'Friday', 'sabado': 'Saturday', 'domingo': 'Sunday'}

# Campos sin los que la web no tiene sentido; el resto son opcionales.
OBLIGATORIOS = [
    'tienda.nombre', 'tienda.calle', 'tienda.codigo_postal', 'tienda.ciudad', 'tienda.latitud', 'tienda.longitud',
    'tienda.google_maps', 'tienda.instagram', 'tienda.horario',
    'portada.seo_titulo', 'portada.seo_descripcion', 'portada.titulo_principal', 'portada.descripcion_negocio', 'portada.lema',
    'carta.titulo', 'carta.vaso.nombre', 'carta.vaso.precio', 'carta.vaso.foto', 'carta.cremas.titulo', 'carta.cremas.precio',
    'carta.cremas.opciones', 'carta.cremas.video', 'carta.cremas.video_portada', 'carta.toppings.titulo', 'carta.toppings.foto',
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


def precio(v, donde):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        error(f'{donde}: el precio debe ser un número (por ejemplo 3.5), no "{v}"')
        return 0
    return float(v)


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
    precio(carta['vaso'].get('precio'), 'Monta tu vaso › vaso')
    precio(carta['cremas'].get('precio'), 'Monta tu vaso › cremas')
    for op in carta['cremas'].get('opciones') or []:
        for a in op.get('alergenos') or []:
            if a not in ALERGENOS:
                error(f'Crema "{op.get("nombre")}": alérgeno desconocido "{a}"')
    for i, g in enumerate(carta['toppings'].get('grupos') or [], 1):
        precio(g.get('precio'), f'Monta tu vaso › toppings, grupo {i}')
        for op in g.get('opciones') or []:
            for a in op.get('alergenos') or []:
                if a not in ALERGENOS:
                    error(f'Topping "{op.get("nombre")}": alérgeno desconocido "{a}"')
    for g in c['bebidas'].get('grupos') or []:
        for p in g.get('productos') or []:
            precio(p.get('precio'), f'Bebidas › {g.get("titulo")} › {p.get("nombre")}')
    for b in c['encargos'].get('bandejas') or []:
        for t in b.get('tamanos') or []:
            precio(t.get('precio'), f'Encargos › {b.get("titulo")} › {t.get("nombre")}')
    for h in c['tienda'].get('horario') or []:
        for d in h.get('dias_semana') or []:
            if d not in DIAS:
                error(f'Horario "{h.get("dias")}": día desconocido "{d}"')
        for k in ('abre', 'cierra'):
            if not re.fullmatch(r'\d{2}:\d{2}', str(h.get(k, ''))):
                error(f'Horario "{h.get("dias")}": la hora "{h.get(k)}" debe ser como 14:00')


# ---------- utilidades para las plantillas ----------

def euros(v):
    return f'{float(v):,.2f}'.replace(',', ' ').replace('.', ',').replace(' ', '.') + ' €'


def euros_corto(v):
    v = float(v)
    return f'{int(v)} €' if v.is_integer() else euros(v)


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
    with Image.open(src) as im:
        w, h = im.size
        if src.suffix.lower() == '.webp' and w <= MAX_IMG:
            _imgs[p] = {'src': p, 'width': w, 'height': h}
        else:
            out = Path(p).with_suffix('.webp')
            if w > MAX_IMG:
                h, w = round(h * MAX_IMG / w), MAX_IMG
            dest = OUT / out
            dest.parent.mkdir(parents=True, exist_ok=True)
            im = im.convert('RGB')
            im.thumbnail((w, h))
            im.save(dest, 'WEBP', quality=80)
            _imgs[p] = {'src': str(out), 'width': w, 'height': h}
    return _imgs[p]


def svg(nombre, etiqueta=None):
    """SVG en línea. Decorativo por defecto; con `etiqueta`, se anuncia como imagen con ese nombre."""
    s = (SRC / 'svg' / f'{nombre}.svg').read_text(encoding='utf-8')
    if etiqueta:
        s = s.replace('aria-hidden="true" focusable="false"', f'role="img" aria-label="{html.escape(etiqueta)}"', 1)
    return Markup(s)


# ---------- datos derivados ----------

def preguntas_auto(c):
    t, carta, enc, beb = c['tienda'], c['carta'], c['encargos'], c['bebidas']
    vaso, crema = float(carta['vaso']['precio']), float(carta['cremas']['precio'])
    tops = [float(g['precio']) for g in carta['toppings']['grupos']]
    cremas = [o['nombre'] for o in carta['cremas']['opciones']]
    horario = '; '.join(f'{h["dias"].lower()}, de {h["abre"]} a {h["cierra"]}' for h in t['horario'])
    horario = horario[0].upper() + horario[1:] + '.'
    if len({d for h in t['horario'] for d in h['dias_semana']}) == 7:
        horario = 'Abrimos todos los días. ' + horario
    bandejas = []
    for b in enc['bandejas']:
        if b.get('tamanos'):
            bandejas.append(f'{b["titulo"].lower()} ({lista([euros_corto(x["precio"]) for x in b["tamanos"]])})')
        else:
            bandejas.append(b['titulo'].lower())
    minus = lambda x: x[0].lower() + x[1:]
    bebidas = '; '.join(f'{g["titulo"].lower()} ({lista([minus(p["nombre"]) for p in g["productos"]])})' for g in beb['grupos'])
    precio_vaso = (f'El {carta["vaso"]["nombre"].lower()} cuesta {euros(vaso)}. La crema suma {euros(crema)}, así que un vaso de fresas '
                   f'con chocolate sale por {euros(vaso + crema)}.')
    if tops:
        precio_vaso += f' Con topping, entre {euros(vaso + crema + min(tops))} y {euros(vaso + crema + max(tops))}.'
    precio_vaso += f' Cremas a elegir: {lista(cremas, "o")}.'
    return [
        {'pregunta': f'¿Dónde está {t["nombre"]} en {t["ciudad"]}?',
         'respuesta': f'En la {t["calle"][0].lower() + t["calle"][1:]} ({t["codigo_postal"]} {t["ciudad"]}), en el centro'
                      + (f', {t["referencia"]}' if t.get('referencia') else '') + f'. [Ver en Google Maps]({t["google_maps"]}).'},
        {'pregunta': '¿Qué horario tiene?', 'respuesta': horario},
        {'pregunta': '¿Cuánto cuesta un vaso de fresas con chocolate?', 'respuesta': precio_vaso},
        {'pregunta': '¿Se pueden encargar bandejas de fresas con chocolate?',
         'respuesta': f'Sí. Hay bandejas {lista(bandejas)}. {enc["como_encargar"]} [Escríbenos por Instagram](https://ig.me/m/{t["instagram"]}).'},
        {'pregunta': '¿Qué más se puede tomar?', 'respuesta': 'Además de los vasos de fresas: ' + bebidas + '.'},
    ]


def jsonld(c, faq):
    t, carta = c['tienda'], c['carta']
    ig = f'https://www.instagram.com/{t["instagram"]}/'

    def item(nombre, p, desc=None):
        d = {'@type': 'MenuItem', 'name': nombre, 'offers': {'@type': 'Offer', 'price': f'{float(p):.2f}', 'priceCurrency': 'EUR'}}
        if desc:
            d['description'] = desc
        return d
    sup = 'Suplemento sobre el vaso de fresas'
    secciones = [
        {'@type': 'MenuSection', 'name': carta['vaso']['nombre'], 'description': carta['vaso'].get('nota', ''),
         'hasMenuItem': [item(carta['vaso']['nombre'], carta['vaso']['precio'])]},
        {'@type': 'MenuSection', 'name': 'Cremas',
         'hasMenuItem': [item(o['nombre'], carta['cremas']['precio'], sup) for o in carta['cremas']['opciones']]},
        {'@type': 'MenuSection', 'name': 'Toppings',
         'hasMenuItem': [item(o['nombre'], g['precio'], sup) for g in carta['toppings']['grupos'] for o in g['opciones']]},
    ]
    for g in c['bebidas']['grupos']:
        secciones.append({'@type': 'MenuSection', 'name': g['titulo'],
                          'hasMenuItem': [item(p['nombre'], p['precio'], p.get('detalle')) for p in g['productos']]})
    secciones.append({'@type': 'MenuSection', 'name': 'Bandejas por encargo', 'description': c['encargos']['como_encargar'],
                      'hasMenuItem': [item(f'{b["titulo"]} {x["nombre"].lower()}', x['precio'], x.get('detalle') or b.get('nota'))
                                      for b in c['encargos']['bandejas'] for x in b.get('tamanos') or []]})
    tienda = {
        '@type': ['FoodEstablishment', 'CafeOrCoffeeShop'], '@id': SITE + '#tienda',
        'name': t['nombre'], 'alternateName': f'{t["nombre"]} {t["ciudad"]}',
        'description': c['portada']['descripcion_negocio'],
        'url': SITE, 'logo': SITE + 'assets/og/logo.png',
        'image': [SITE + 'assets/og/og.jpg', SITE + img(carta['vaso']['foto'])['src'], SITE + img(c['historia']['nosotras']['foto'])['src']],
        'address': {'@type': 'PostalAddress', 'streetAddress': t['calle'], 'postalCode': str(t['codigo_postal']),
                    'addressLocality': t['ciudad'], 'addressRegion': t['ciudad'], 'addressCountry': 'ES'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': t['latitud'], 'longitude': t['longitud']},
        'hasMap': f'https://www.google.com/maps?cid={t["google_maps_cid"]}' if t.get('google_maps_cid') else t['google_maps'],
        'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': [DIAS[d] for d in h['dias_semana']],
                                       'opens': h['abre'], 'closes': h['cierra']} for h in t['horario']],
        'priceRange': '€', 'currenciesAccepted': 'EUR',
        'servesCuisine': ['Fresas con chocolate', 'Postres', 'Batidos', 'Café'],
        'hasMenu': {'@id': SITE + '#carta'}, 'areaServed': {'@type': 'City', 'name': t['ciudad']},
        'foundingDate': str(t.get('abierta_desde', '')), 'sameAs': [ig],
        'potentialAction': {'@type': 'OrderAction', 'target': f'https://ig.me/m/{t["instagram"]}',
                            'description': 'Encargar bandejas de fresas con chocolate por mensaje de Instagram'},
    }
    if t.get('telefono'):
        tienda['telephone'] = t['telefono']
    if t.get('email'):
        tienda['email'] = t['email']
    grafo = [
        tienda,
        {'@type': 'Menu', '@id': SITE + '#carta', 'name': f'Carta de {t["nombre"]}', 'inLanguage': 'es', 'hasMenuSection': secciones},
        {'@type': 'WebSite', '@id': SITE + '#web', 'url': SITE, 'name': t['nombre'], 'inLanguage': 'es-ES', 'publisher': {'@id': SITE + '#tienda'}},
        {'@type': 'WebPage', '@id': SITE + '#pagina', 'url': SITE, 'name': c['portada']['seo_titulo'], 'isPartOf': {'@id': SITE + '#web'},
         'about': {'@id': SITE + '#tienda'}, 'inLanguage': 'es-ES', 'primaryImageOfPage': SITE + 'assets/og/og.jpg'},
        {'@type': 'FAQPage', '@id': SITE + '#preguntas', 'isPartOf': {'@id': SITE + '#web'}, 'inLanguage': 'es-ES',
         'mainEntity': [{'@type': 'Question', 'name': q['pregunta'],
                         'acceptedAnswer': {'@type': 'Answer', 'text': sin_enlaces(q['respuesta'])}} for q in faq]},
    ]
    s = json.dumps({'@context': 'https://schema.org', '@graph': grafo}, ensure_ascii=False, separators=(',', ':'))
    return Markup(s.replace('</', '<\\/'))


# ---------- generación ----------

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

    faq = preguntas_auto(c) + list(c['preguntas'].get('preguntas') or [])
    env = Environment(loader=FileSystemLoader(SRC), autoescape=True,
                      trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    env.filters.update(euros=euros, euros_corto=euros_corto, enlaces=enlaces, sin_enlaces=sin_enlaces, ruta=ruta)
    env.globals.update(img=img, svg=svg, site=SITE, alergenos=ALERGENOS, year=dt.date.today().year,
                       hoy=dt.date.today().isoformat(), faq=faq, **c)
    # El JSON-LD usa img(), que también registra errores de fotos.
    env.globals['jsonld'] = jsonld(c, faq)

    for nombre, autoescape in [('index.html', True), ('llms.txt', False), ('sitemap.xml', True), ('robots.txt', False)]:
        env.autoescape = autoescape
        (OUT / nombre).write_text(env.get_template(nombre + '.j2').render(), encoding='utf-8')
    if errores:
        shutil.rmtree(OUT)
        sys.exit('No se ha generado la web:\n  - ' + '\n  - '.join(errores))
    (OUT / '.nojekyll').write_text('')
    print(f'Web generada en {OUT.relative_to(ROOT)}/ ({SITE})')


if __name__ == '__main__':
    main()
