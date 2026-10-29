// Fresas y Chocolate · hero. The video is played back as a sequence of WebP frames drawn on a canvas;
// the scroll position through the hero picks the frame, so it scrubs both ways without the seeking
// jank of <video>.currentTime (worst on iOS Safari). Frames come from scripts/extraer-frames.sh.
// Timeline, in scroll distance from the top of the hero (vh = viewport height, run = pinned distance):
// - the hero stays pinned for `run`; the video ends ANIM_OVERRUN after that, so its last frames play
//   while the hero (logo included) is already scrolling away;
// - the closing line and buttons rise over CLOSE, from halfway through the pin, while the chocolate still pours;
// - the top bar slides down once the hero's bottom edge is above BAR_AT of the viewport.
(function () {
  const ANIM_OVERRUN = 0.3, CLOSE = [-1.0, -0.6], BAR_AT = 0.6; // in vh
  const SUBJECT_W = 0.6; // share of the frame width the strawberry spans, leaves and drips included
  const STALK = 0.04; // share of the frame height the thin stalk rises above the detected strawberry
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
  let shown = 0, dirty = true, raf = 0, cw = 0, ch = 0, zoom = 1, lift = 0, fitHeight = false;
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
    const stageTop = r.top - pr.top, stageBottom = stageTop + r.height;
    const logoBottom = logo.getBoundingClientRect().bottom - pr.top;
    const mobile = getComputedStyle(close).position === 'absolute';
    zoom = 1; lift = 0;
    // Mobile: fitted to the height, the strawberry sits high and leaves the bottom of the screen empty.
    // Zoom in, keeping the top edge so the chocolate still pours from the top of the screen, until the
    // strawberry plus "Desliza" are centred below the logo, without cropping the strawberry's sides.
    if (fitHeight && mobile && m.subjectStart) {
      const s0 = r.height / m.height;
      const want = (stageBottom + logoBottom - 2 * stageTop - 20 - hint.offsetHeight) /
        ((m.subjectStart[0] - STALK + m.subjectStart[1]) * m.height);
      const widest = (0.96 * r.width) / (SUBJECT_W * m.width);
      zoom = Math.max(1, Math.min(want, widest) / s0);
    }
    const s = fitHeight ? r.height / m.height : Math.min(r.width / m.width, r.height / m.height);
    const top = fitHeight ? stageTop : stageTop + (r.height - m.height * s) / 2;
    // "Desliza" sits just under the strawberry of the first frame.
    if (m.subjectStart) {
      hint.style.top = `${Math.round(top + m.subjectStart[1] * m.height * s * zoom + 20)}px`;
      hint.style.bottom = 'auto';
    }
    // Mobile: the closing line overlays the bottom of the screen. The zoom eases back out as it comes
    // in; lift the strawberry (its extent in the last frame comes from the manifest) just enough to
    // clear it, but never into the logo.
    if (mobile && m.subject) {
      const subjTop = top + m.subject[0] * m.height * s;
      const subjBottom = top + m.subject[1] * m.height * s;
      const closeTop = stageBottom - close.offsetHeight + 24;
      const needed = subjBottom - closeTop;
      const room = subjTop - logoBottom - 12;
      lift = Math.max(0, Math.min(needed, room));
    }
    dirty = true;
  }

  function draw(i, zoom) {
    const img = nearest(i);
    if (!img || !cw || !ch) return;
    // Either fitted to the height (top edge kept, zoomed on mobile, sides may crop) or contained and
    // centred. The frame edges are the same colour as the hero, so any letterbox is invisible.
    const s = (fitHeight ? ch / m.height : Math.min(cw / m.width, ch / m.height)) * zoom;
    const w = m.width * s, h = m.height * s;
    ctx.clearRect(0, 0, cw, ch);
    ctx.drawImage(img, (cw - w) / 2, fitHeight ? 0 : (ch - h) / 2, w, h);
    // Narrower than the screen (desktop): the frame's edges are a shade darker than the background, so
    // fade them out instead of leaving a visible seam.
    if (w < cw) {
      const x = (cw - w) / 2, f = w * 0.12;
      const g = ctx.createLinearGradient(x, 0, x + w, 0);
      g.addColorStop(0, 'rgba(0,0,0,0)');
      g.addColorStop(f / w, '#000');
      g.addColorStop(1 - f / w, '#000');
      g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.globalCompositeOperation = 'destination-in';
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, cw, ch);
      ctx.globalCompositeOperation = 'source-over';
    }
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
    const c = smooth(run + CLOSE[0] * vh, run + CLOSE[1] * vh, y);
    draw(Math.round(shown), 1 + (zoom - 1) * (1 - c));
    dirty = false;
    hint.style.opacity = String(1 - smooth(0.02, 0.12, y / run));
    close.style.opacity = String(c);
    close.style.transform = `translateY(${(1 - c) * 14}px)`;
    close.classList.toggle('on', c > 0.5);
    canvas.style.transform = lift ? `translateY(${-c * lift}px)` : '';
    topbar.classList.toggle('show', r.bottom < BAR_AT * vh);
    if (shown !== target) request();
  }
  function request() { if (!raf) raf = requestAnimationFrame(tick); }

  window.addEventListener('scroll', request, { passive: true });
  // The logo in the top bar goes back to the end of the animation (closing line and buttons in view),
  // not to the top of the pour.
  topbar.querySelector('.topbar-logo').addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({ top: hero.offsetTop + hero.offsetHeight - window.innerHeight, behavior: 'smooth' });
  });
  window.addEventListener('resize', () => { resize(); request(); });
  // Redraw while frames near the current position are still arriving.
  (function watch() { if (dirty) request(); if (next < order.length || dirty) setTimeout(watch, 120); })();
  resize();
  shown = clamp01(Math.max(0, -hero.getBoundingClientRect().top) / (hero.offsetHeight - innerHeight * (1 - ANIM_OVERRUN))) * (m.count - 1);
  request();
})();
