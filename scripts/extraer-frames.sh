#!/usr/bin/env bash
# Convierte el vídeo del hero en la secuencia de fotogramas WebP que recorre el scroll.
# Uso:  scripts/extraer-frames.sh ruta/al/video.mp4 [fotogramas=todos] [calidad=70] [ancho=720]
# fotogramas: "156" = del 1 al 156; "30-156" = del 30 al 156 (donde empieza y se detiene la
# animación); 0 o vacío = el vídeo entero. Los archivos conservan su número de fotograma
# (0030.webp…) y assets/hero/manifest.js recoge el primero, el nº de fotogramas, el tamaño y el
# color de fondo muestreado de la esquina, que la web usa para fundir el hero.
set -euo pipefail

VIDEO="${1:?Uso: $0 video.mp4 [fotogramas] [calidad] [ancho]}"
RANGE="${2:-0}"
QUALITY="${3:-70}"
WIDTH="${4:-720}"
if [[ "$RANGE" == *-* ]]; then FIRST="${RANGE%-*}"; LAST_FRAME="${RANGE#*-}"; else FIRST=1; LAST_FRAME="$RANGE"; fi
LIMIT=()
[ "$LAST_FRAME" -gt 0 ] && LIMIT=(-frames:v "$((LAST_FRAME - FIRST + 1))")
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/assets/hero"

command -v ffmpeg >/dev/null || { echo "Falta ffmpeg (brew install ffmpeg)"; exit 1; }

rm -rf "$OUT/frames"
mkdir -p "$OUT/frames"

ffmpeg -loglevel error -i "$VIDEO" -an ${LIMIT[@]+"${LIMIT[@]}"} \
  -vf "select='gte(n\,$((FIRST - 1)))',scale=${WIDTH}:-2" -fps_mode passthrough \
  -c:v libwebp -quality "$QUALITY" -compression_level 4 -start_number "$FIRST" "$OUT/frames/%04d.webp"

# Último fotograma como imagen estática (sin JS / prefers-reduced-motion).
LAST="$(ls "$OUT/frames" | sort | tail -1)"
cp "$OUT/frames/$LAST" "$OUT/poster.webp"

COUNT="$(ls "$OUT/frames" | wc -l | tr -d ' ')"
FIRST_FILE="$OUT/frames/$(ls "$OUT/frames" | sort | head -1)"
SIZE="$( (ffmpeg -hide_banner -i "$FIRST_FILE" 2>&1 || true) | grep -oE '[0-9]{2,5}x[0-9]{2,5}' | head -1)"
W="${SIZE%x*}"; H="${SIZE#*x}"
BG="#$(ffmpeg -loglevel error -i "$FIRST_FILE" -vf "crop=24:24:4:4,scale=1:1" \
  -f rawvideo -pix_fmt rgb24 - | xxd -p)"

# Franja vertical que ocupa el motivo (la fresa) en un fotograma, en fracciones de la altura.
# La web usa la del último fotograma para subir la fresa lo justo al aparecer el lema, y la del
# primero para colocar "Desliza" justo debajo de la fresa.
# Se ignoran las filas estrechas (el chorro, gotas sueltas, salpicaduras): cuentan las de ≥ 10/90 px.
subject() {
  ffmpeg -loglevel error -i "$1" -vf "scale=90:160" -f rawvideo -pix_fmt rgb24 - | python3 -c '
import sys
bg = bytes.fromhex(sys.argv[1].lstrip("#")); px = sys.stdin.buffer.read(); W, H = 90, 160
rows = [i for i in range(H) if sum(sum(abs(px[(i*W+x)*3+k] - bg[k]) for k in range(3)) > 90 for x in range(W)) >= 10]
print(f"[{rows[0]/H:.3f}, {(rows[-1]+1)/H:.3f}]" if rows else "[0, 1]")
' "$BG"
}
SUBJECT="$(subject "$OUT/poster.webp")"
SUBJECT_START="$(subject "$FIRST_FILE")"

# Se escribe como script (no JSON) para que la web funcione también abierta con doble clic (file://).
cat > "$OUT/manifest.js" <<JS
window.HERO_MANIFEST = {
  count: $COUNT,
  start: $FIRST,
  width: $W,
  height: $H,
  background: "$BG",
  subject: $SUBJECT,
  subjectStart: $SUBJECT_START,
  pattern: "assets/hero/frames/{n}.webp",
  pad: 4
};
JS

echo "Listo: $COUNT fotogramas ${W}x${H}, fondo $BG, $(du -sh "$OUT/frames" | cut -f1)"
echo "La web toma el fondo del manifest; para la versión sin JS, pon --hero-bg: $BG en css/styles.css."
