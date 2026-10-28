// Preguntas frecuentes: <details> that open and close with a height animation instead of jumping.
// Without JS (or with reduced motion) they still work as plain <details>.
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const EASE = 'cubic-bezier(.2, .7, .2, 1)';

  document.querySelectorAll('.faq-item').forEach((item) => {
    const summary = item.querySelector('summary');
    let anim = null;

    function run(from, to, done) {
      if (anim) anim.cancel();
      item.style.overflow = 'hidden';
      anim = item.animate({ height: [`${from}px`, `${to}px`] }, { duration: 320, easing: EASE });
      anim.onfinish = () => { anim = null; item.style.overflow = ''; done && done(); };
      anim.oncancel = () => { anim = null; };
    }

    summary.addEventListener('click', (e) => {
      e.preventDefault();
      const from = item.offsetHeight;
      if (item.open && !item.classList.contains('is-closing')) {
        item.classList.add('is-closing');
        run(from, summary.offsetHeight, () => { item.open = false; item.classList.remove('is-closing'); });
      } else {
        item.classList.remove('is-closing');
        item.open = true;
        run(from, item.offsetHeight);
      }
    });
  });
})();
