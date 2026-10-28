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
