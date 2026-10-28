#!/usr/bin/env bash
# Convierte el vídeo del hero en la secuencia de fotogramas WebP que recorre el scroll.
# Uso:  scripts/extraer-frames.sh ruta/al/video.mp4 [ultimo-fotograma=todos] [calidad=70] [ancho=720]
# El último fotograma es donde se detiene la animación (p. ej. 156); 0 o vacío = el vídeo entero.
# Genera assets/hero/frames/0001.webp… y assets/hero/manifest.json (nº de fotogramas,
# tamaño y color de fondo muestreado de la esquina, que la web usa para fundir el hero).
set -euo pipefail

VIDEO="${1:?Uso: $0 video.mp4 [ultimo-fotograma] [calidad] [ancho]}"
LAST_FRAME="${2:-0}"
QUALITY="${3:-70}"
WIDTH="${4:-720}"
LIMIT=()
[ "$LAST_FRAME" -gt 0 ] && LIMIT=(-frames:v "$LAST_FRAME")
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/assets/hero"

command -v ffmpeg >/dev/null || { echo "Falta ffmpeg (brew install ffmpeg)"; exit 1; }

rm -rf "$OUT/frames"
mkdir -p "$OUT/frames"

ffmpeg -loglevel error -i "$VIDEO" -an ${LIMIT[@]+"${LIMIT[@]}"} -vf "scale=${WIDTH}:-2" \
  -c:v libwebp -quality "$QUALITY" -compression_level 4 "$OUT/frames/%04d.webp"

# Último fotograma como imagen estática (sin JS / prefers-reduced-motion).
LAST="$(ls "$OUT/frames" | sort | tail -1)"
cp "$OUT/frames/$LAST" "$OUT/poster.webp"

COUNT="$(ls "$OUT/frames" | wc -l | tr -d ' ')"
SIZE="$( (ffmpeg -hide_banner -i "$OUT/frames/0001.webp" 2>&1 || true) | grep -oE '[0-9]{2,5}x[0-9]{2,5}' | head -1)"
W="${SIZE%x*}"; H="${SIZE#*x}"
BG="#$(ffmpeg -loglevel error -i "$OUT/frames/0001.webp" -vf "crop=24:24:4:4,scale=1:1" \
  -f rawvideo -pix_fmt rgb24 - | xxd -p)"

# Franja vertical que ocupa el motivo (la fresa) en el último fotograma, en fracciones de la altura.
# La web la usa en móvil para subir la fresa lo justo al aparecer el lema, sin chocar con el logo.
# Se ignoran las filas estrechas (el chorro, gotas sueltas, salpicaduras): cuentan las de ≥ 10/90 px.
SUBJECT="$(ffmpeg -loglevel error -i "$OUT/poster.webp" -vf "scale=90:160" -f rawvideo -pix_fmt rgb24 - | python3 -c '
import sys
bg = bytes.fromhex(sys.argv[1].lstrip("#")); px = sys.stdin.buffer.read(); W, H = 90, 160
rows = [i for i in range(H) if sum(sum(abs(px[(i*W+x)*3+k] - bg[k]) for k in range(3)) > 90 for x in range(W)) >= 10]
print(f"[{rows[0]/H:.3f}, {(rows[-1]+1)/H:.3f}]" if rows else "[0, 1]")
' "$BG")"

# Se escribe como script (no JSON) para que la web funcione también abierta con doble clic (file://).
cat > "$OUT/manifest.js" <<JS
window.HERO_MANIFEST = {
  count: $COUNT,
  width: $W,
  height: $H,
  background: "$BG",
  subject: $SUBJECT,
  pattern: "assets/hero/frames/{n}.webp",
  pad: 4
};
JS

echo "Listo: $COUNT fotogramas ${W}x${H}, fondo $BG, $(du -sh "$OUT/frames" | cut -f1)"
echo "La web toma el fondo del manifest; para la versión sin JS, pon --hero-bg: $BG en css/styles.css."
