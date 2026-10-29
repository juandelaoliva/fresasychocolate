// Galerías deslizables (.carrusel): on touch screens they are swiped; with a mouse, prev/next arrows
// appear under the strip while there is more to see. Each click moves by one photo or clip.
(function () {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

  document.querySelectorAll('.carrusel').forEach((c) => {
    const strip = c.querySelector('.strip');
    const nav = c.querySelector('.carrusel-nav');
    const [prev, next] = nav.querySelectorAll('.carrusel-btn');

    function update() {
      const max = strip.scrollWidth - strip.clientWidth;
      nav.hidden = max < 4;
      prev.disabled = strip.scrollLeft < 4;
      next.disabled = strip.scrollLeft > max - 4;
    }

    nav.addEventListener('click', (e) => {
      const btn = e.target.closest('.carrusel-btn');
      if (!btn) return;
      const item = strip.firstElementChild;
      const step = item ? item.getBoundingClientRect().width + parseFloat(getComputedStyle(strip).columnGap || 0) : strip.clientWidth;
      strip.scrollBy({ left: Number(btn.dataset.dir) * step, behavior: 'smooth' });
    });
    strip.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });
})();
