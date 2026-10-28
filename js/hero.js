// Fresas y Chocolate · hero. The video is played back as a sequence of WebP frames drawn on a canvas;
// the scroll position through the hero picks the frame, so it scrubs both ways without the seeking
// jank of <video>.currentTime (worst on iOS Safari). Frames come from scripts/extraer-frames.sh.
// Timeline, in scroll distance from the top of the hero (vh = viewport height, run = pinned distance):
// - the hero stays pinned for `run`; the video ends ANIM_OVERRUN after that, so its last frames play
//   while the hero (logo included) is already scrolling away;
// - the closing line and buttons rise over CLOSE, just before the pin releases;
// - the top bar slides down once the hero's bottom edge is above BAR_AT of the viewport.
(function () {
  const ANIM_OVERRUN = 0.3, CLOSE = [-0.5, -0.1], BAR_AT = 0.6; // in vh
  const m = window.HERO_MANIFEST;
  const hero = document.getElementById('hero');
  const canvas = document.getElementById('hero-canvas');
  const hint = document.getElementById('hero-hint');
  const close = document.getElementById('hero-close');
  const topbar = document.getElementById('topbar');
  const pin = hero && hero.querySelector('.hero-pin');
  const logo = hero && hero.querySelector('.hero-brand .logo');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!m || !hero || !canvas || !topbar || !logo || reduce.matches) return;

  const ctx = canvas.getContext('2d');
  const frames = new Array(m.count);
  let shown = 0, dirty = true, raf = 0, cw = 0, ch = 0, lift = 0, fitHeight = false;
  const src = (i) => m.pattern.replace('{n}', String(i + (m.start || 1)).padStart(m.pad, '0'));
  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const smooth = (a, b, x) => { const t = clamp01((x - a) / (b - a)); return t * t * (3 - 2 * t); };

  document.documentElement.classList.add('hero-ready');
  document.documentElement.style.setProperty('--hero-bg', m.background);

  // Load coarse-to-fine (every 16th frame, then 8th, 4th…) so a fast scroll already shows the whole
  // pour in low temporal resolution while the in-between frames arrive.
  const order = [];
  const seen = new Uint8Array(m.count);
  for (let step = 16; step >= 1; step /= 2) {
    for (let i = 0; i < m.count; i += step) if (!seen[i]) { seen[i] = 1; order.push(i); }
  }
  if (!seen[m.count - 1]) order.push(m.count - 1);
  let next = 0;
  function loadNext() {
    if (next >= order.length) return;
    const i = order[next++];
    const img = new Image();
    img.decoding = 'async';
    img.onload = () => { frames[i] = img; if (Math.abs(i - Math.round(shown)) < 16) dirty = true; loadNext(); };
    img.onerror = loadNext;
    img.src = src(i);
  }
  for (let k = 0; k < 6; k++) loadNext();

  // Nearest frame that has already arrived.
  function nearest(i) {
    for (let d = 0; d < m.count; d++) {
      if (frames[i - d]) return frames[i - d];
      if (frames[i + d]) return frames[i + d];
    }
    return null;
  }

  function resize() {
    const r = canvas.parentElement.getBoundingClientRect(); // the stage: unlike the canvas, never lifted
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    cw = Math.round(r.width * dpr); ch = Math.round(r.height * dpr);
    if (canvas.width !== cw || canvas.height !== ch) { canvas.width = cw; canvas.height = ch; }
    fitHeight = getComputedStyle(canvas).getPropertyValue('--hero-fit').trim() === 'height';
    // Positions below are in pin coordinates so they hold wherever the page is scrolled.
    const pr = pin.getBoundingClientRect();
    const s = fitHeight ? r.height / m.height : Math.min(r.width / m.width, r.height / m.height);
    const top = r.top - pr.top + (r.height - m.height * s) / 2;
    // "Desliza" sits just under the strawberry of the first frame.
    if (m.subjectStart) {
      hint.style.top = `${Math.round(top + m.subjectStart[1] * m.height * s + 20)}px`;
      hint.style.bottom = 'auto';
    }
    lift = 0;
    // Mobile: the closing line overlays the bottom of the screen. Lift the strawberry (its extent in the
    // last frame comes from the manifest) just enough to clear it, but never into the logo.
    if (getComputedStyle(close).position === 'absolute' && m.subject) {
      const subjTop = top + m.subject[0] * m.height * s;
      const subjBottom = top + m.subject[1] * m.height * s;
      const closeTop = r.top - pr.top + r.height - close.offsetHeight + 24;
      const needed = subjBottom - closeTop;
      const room = subjTop - (logo.getBoundingClientRect().bottom - pr.top) - 12;
      lift = Math.max(0, Math.min(needed, room));
    }
    dirty = true;
  }

  function draw(i) {
    const img = nearest(i);
    if (!img || !cw || !ch) return;
    // Centred, either fitted to the height (sides may crop) or contained. The frame edges are the same
    // colour as the hero, so any letterbox is invisible.
    const s = fitHeight ? ch / m.height : Math.min(cw / m.width, ch / m.height);
    const w = m.width * s, h = m.height * s;
    ctx.clearRect(0, 0, cw, ch);
    ctx.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
  }

  // The drawn frame eases toward the scroll target, which smooths out coarse wheel steps.
  function tick() {
    raf = 0;
    const vh = window.innerHeight;
    const r = hero.getBoundingClientRect();
    const run = hero.offsetHeight - vh;
    const y = Math.max(0, -r.top);
    const target = clamp01(y / (run + ANIM_OVERRUN * vh)) * (m.count - 1);
    const delta = target - shown;
    shown = Math.abs(delta) < 0.5 ? target : shown + delta * 0.3;
    draw(Math.round(shown));
    dirty = false;
    hint.style.opacity = String(1 - smooth(0.02, 0.12, y / run));
    const c = smooth(run + CLOSE[0] * vh, run + CLOSE[1] * vh, y);
    close.style.opacity = String(c);
    close.style.transform = `translateY(${(1 - c) * 14}px)`;
    close.classList.toggle('on', c > 0.5);
    canvas.style.transform = lift ? `translateY(${-c * lift}px)` : '';
    topbar.classList.toggle('show', r.bottom < BAR_AT * vh);
    if (shown !== target) request();
  }
  function request() { if (!raf) raf = requestAnimationFrame(tick); }

  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', () => { resize(); request(); });
  // Redraw while frames near the current position are still arriving.
  (function watch() { if (dirty) request(); if (next < order.length || dirty) setTimeout(watch, 120); })();
  resize();
  shown = clamp01(Math.max(0, -hero.getBoundingClientRect().top) / (hero.offsetHeight - innerHeight * (1 - ANIM_OVERRUN))) * (m.count - 1);
  request();
})();
