// Burger menu: a full-screen panel in the hero colour under the top bar. Closes on link, Escape or
// a second tap, and locks the page scroll while open.
(function () {
  const burger = document.getElementById('burger');
  const panel = document.getElementById('nav-panel');
  if (!burger || !panel) return;
  const T = Object.assign({ abrir_menu: 'Abrir menú', cerrar_menu: 'Cerrar menú' }, window.UI);

  function set(open) {
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? T.cerrar_menu : T.abrir_menu);
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

// Desktop bar: "Carta" drops down the sections you can order from (hover with a mouse, click or tap
// otherwise; Escape or a click outside closes it).
(function () {
  const group = document.querySelector('.topnav-group');
  if (!group) return;
  const btn = group.querySelector('.topnav-parent');
  let timer = 0;
  function set(open) {
    clearTimeout(timer);
    group.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', String(open));
  }
  btn.addEventListener('click', () => set(!group.classList.contains('open')));
  const mouse = window.matchMedia('(hover: hover) and (pointer: fine)');
  group.addEventListener('mouseenter', () => { if (mouse.matches) set(true); });
  group.addEventListener('mouseleave', () => { if (mouse.matches) timer = setTimeout(() => set(false), 160); });
  group.addEventListener('focusout', (e) => { if (!group.contains(e.relatedTarget)) set(false); });
  group.addEventListener('click', (e) => { if (e.target.closest('.topnav-sub a')) set(false); });
  document.addEventListener('click', (e) => { if (!group.contains(e.target)) set(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && group.classList.contains('open')) { set(false); btn.focus(); } });
})();

// Desktop bar: mark the link of the section on screen (the band across the middle of the viewport).
// The "Carta" button is marked too while one of its sections is on screen.
(function () {
  const links = [...document.querySelectorAll('.topnav a[href^="#"]')];
  if (!links.length || !('IntersectionObserver' in window)) return;
  const byId = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
  const parent = document.querySelector('.topnav-parent');
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      links.forEach((a) => a.removeAttribute('aria-current'));
      parent && parent.removeAttribute('aria-current');
      const a = byId.get(e.target.id);
      a.setAttribute('aria-current', 'true');
      if (parent && a.closest('.topnav-sub')) parent.setAttribute('aria-current', 'true');
    }
  }, { rootMargin: '-45% 0px -50% 0px' });
  byId.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
})();
