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
