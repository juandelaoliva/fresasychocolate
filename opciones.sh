#!/usr/bin/env bash
# TEMPORAL: publica, además de la web, tres copias de prueba para elegir cómo se muestran las ayudas
# (content/financiacion.yml › modo), en /opciones/a/, /opciones/b/ y /opciones/c/. No se indexan ni cuentan visitas.
# Cuando se elija una, se pone ese modo en content/financiacion.yml, se borra este archivo y en
# .github/workflows/publicar.yml se vuelve a `python build.py`.
set -euo pipefail
PY=$(command -v python || command -v python3)
tmp=$(mktemp -d)
for par in "a:visible:Opción A · visible" "b:pagina:Opción B · enlace a página" "c:ventana:Opción C · ventana"; do
  IFS=: read -r letra modo nombre <<< "$par"
  FIN_MODO=$modo PREVIA="$nombre" "$PY" build.py
  mv _site "$tmp/$letra"
done
"$PY" build.py
mkdir -p _site/opciones
mv "$tmp"/a "$tmp"/b "$tmp"/c _site/opciones/
cat > _site/opciones/index.html <<'HTML'
<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Ayudas públicas · 3 opciones · Fresas y Chocolate</title>
<link rel="stylesheet" href="../css/fonts.css">
<style>
body{margin:0;padding:32px 20px;background:#fbf5ec;color:#613613;font:17px/1.5 Jost,system-ui,sans-serif}
main{max-width:640px;margin:0 auto} h1{font:400 34px/1.1 Italiana,serif;margin:0 0 8px} p{margin:0 0 20px;color:#6f4f38}
a.op{display:block;background:#fff;border-radius:16px;padding:18px 20px;margin:14px 0;text-decoration:none;color:inherit;box-shadow:0 2px 10px rgba(0,0,0,.07)}
a.op b{display:block;font-size:19px;margin-bottom:4px;color:#b5485c} small{font-size:14px}
</style></head><body><main>
<h1>Ayudas públicas · 3 opciones</h1>
<p>Cada opción abre la web completa. La diferencia está al final de la página, justo encima del pie.</p>
<a class="op" href="a/#fin-t"><b>Opción A · Visible directamente</b>Los dos carteles, en pequeño y con fondo blanco, encima del pie.</a>
<a class="op" href="b/#fin-t"><b>Opción B · Enlace a otra página</b>Logos, una frase de resumen y un botón que lleva a una página con los dos carteles.</a>
<a class="op" href="c/#fin-t"><b>Opción C · Enlace que abre una ventana</b>Logos, una frase de resumen y un botón con icono que abre los dos carteles encima de la página.</a>
<p><small>En inglés: añade <code>en/</code> a la dirección de cada opción.</small></p>
</main></body></html>
HTML
rm -rf "$tmp"
echo "Opciones de prueba en _site/opciones/"
