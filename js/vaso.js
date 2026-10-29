// "Monta tu vaso": the menu's three steps as radio chips. Adds up the price and lists the allergens
// of the chosen cream and topping (data-al on each option, by name). The base price and the menu's
// allergen order come from the form (data-base, data-alergenos), both written from content/carta.yml.
// Options whose allergens aren't known yet carry data-al-pending and send the customer to ask in the shop.
(function () {
  const form = document.getElementById('builder');
  if (!form) return;
  const BASE = Number(form.dataset.base);
  const ORDER = (form.dataset.alergenos || '').split(',');
  const desc = document.getElementById('total-desc');
  const price = document.getElementById('total-price');
  const al = document.getElementById('total-al');
  const base = desc.textContent;
  const euros = (n) => n.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';

  function update() {
    const picked = ['crema', 'topping'].map((n) => form.querySelector(`input[name="${n}"]:checked`)).filter((i) => i && i.value);
    const total = picked.reduce((sum, i) => sum + Number(i.dataset.price), BASE);
    const names = new Set(picked.flatMap((i) => (i.dataset.al ? i.dataset.al.split(',') : [])));
    const list = ORDER.filter((n) => names.has(n));
    desc.textContent = [base, ...picked.map((i) => i.value)].join(' + ');
    price.textContent = euros(total);
    const pending = picked.filter((i) => 'alPending' in i.dataset).map((i) => i.value);
    const parts = [];
    if (list.length) parts.push('Alérgenos: ' + list.join(', '));
    if (pending.length) parts.push('Pregunta en tienda los alérgenos de: ' + pending.join(', '));
    al.textContent = parts.length ? parts.join(' · ') : 'Sin alérgenos de la carta';
  }

  form.addEventListener('change', update);
  form.addEventListener('submit', (e) => e.preventDefault());
  update();
})();

// Under "Monta tu vaso": today's opening hours in plain words, from the shop's hours (data-* on
// #pedir-hoy, written from content/tienda.yml). Uses the visitor's clock. Without JS the address stays.
(function () {
  const el = document.getElementById('pedir-hoy');
  if (!el) return;
  const DIAS = ['domingo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'];
  let dias, abre, cierra;
  try {
    [dias, abre, cierra] = ['horario', 'abre', 'cierra'].map((k) => JSON.parse(el.dataset[k]));
  } catch (e) { return; }
  const horasDe = (d) => {
    const i = dias.findIndex((lista) => lista.includes(DIAS[d]));
    return i < 0 ? null : { abre: abre[i], cierra: cierra[i] };
  };
  const now = new Date();
  const hhmm = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  const hoy = horasDe(now.getDay());
  if (hoy && hhmm >= hoy.abre && hhmm < hoy.cierra) {
    el.innerHTML = '<span class="abierto"></span>';
    el.firstChild.textContent = `Abierto ahora, hasta las ${hoy.cierra}`;
    return;
  }
  if (hoy && hhmm < hoy.abre) { el.textContent = `Hoy abrimos a las ${hoy.abre}`; return; }
  for (let k = 1; k <= 7; k++) {
    const d = (now.getDay() + k) % 7;
    const h = horasDe(d);
    if (h) {
      const cuando = k === 1 ? 'mañana' : `el ${DIAS[d].replace('miercoles', 'miércoles').replace('sabado', 'sábado')}`;
      el.textContent = `Hoy ya hemos cerrado · ${cuando} abrimos a las ${h.abre}`;
      return;
    }
  }
})();
