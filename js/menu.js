// Burger menu: a full-screen panel in the hero colour under the top bar. Closes on link, Escape or
// a second tap, and locks the page scroll while open.
(function () {
  const burger = document.getElementById('burger');
  const panel = document.getElementById('nav-panel');
  if (!burger || !panel) return;

  function set(open) {
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    panel.hidden = !open;
    document.documentElement.classList.toggle('nav-open', open);
    if (open) panel.querySelector('a').focus();
  }

  burger.addEventListener('click', () => set(burger.getAttribute('aria-expanded') !== 'true'));
  panel.addEventListener('click', (e) => { if (e.target.closest('a')) set(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !panel.hidden) { set(false); burger.focus(); }
  });
})();

// Desktop bar: mark the link of the section on screen (the band across the middle of the viewport).
(function () {
  const links = [...document.querySelectorAll('.topnav a[href^="#"]')];
  if (!links.length || !('IntersectionObserver' in window)) return;
  const byId = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      links.forEach((a) => a.removeAttribute('aria-current'));
      byId.get(e.target.id).setAttribute('aria-current', 'true');
    }
  }, { rootMargin: '-45% 0px -50% 0px' });
  byId.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
})();
