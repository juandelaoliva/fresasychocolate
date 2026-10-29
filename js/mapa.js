// Visítanos: the embedded Google map loads only when the visitor taps "Ver el mapa aquí", so Google
// receives nothing (no IP, no cookies) until then. Without JS the address and the Maps button stay.
(function () {
  const box = document.getElementById('mapa');
  if (!box) return;
  const btn = box.querySelector('.mapa-btn');
  btn.hidden = false;
  btn.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = box.dataset.src;
    f.title = box.dataset.title;
    f.allowFullscreen = true;
    f.referrerPolicy = 'no-referrer-when-downgrade';
    box.replaceChildren(f);
    box.classList.add('cargado');
    f.focus();
  });
})();
