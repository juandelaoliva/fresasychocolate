// "Monta tu vaso": the menu's three steps as radio chips. Adds up the price and lists the allergens
// of the chosen cream and topping (numbers from the shop's menu, data-al on each option). Options
// whose allergens aren't known yet carry data-al-pending and send the customer to ask in the shop.
(function () {
  const form = document.getElementById('builder');
  if (!form) return;
  const BASE = 3.5;
  const NAMES = { 1: 'gluten', 2: 'leche', 3: 'huevo', 4: 'sésamo', 5: 'soja', 6: 'pistachos', 7: 'frutos de cáscara', 8: 'avellanas', 9: 'mantequilla', 10: 'coco' };
  const desc = document.getElementById('total-desc');
  const price = document.getElementById('total-price');
  const al = document.getElementById('total-al');
  const euros = (n) => n.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';

  function update() {
    const picked = ['crema', 'topping'].map((n) => form.querySelector(`input[name="${n}"]:checked`)).filter((i) => i && i.value);
    const total = picked.reduce((sum, i) => sum + Number(i.dataset.price), BASE);
    const codes = [...new Set(picked.flatMap((i) => (i.dataset.al ? i.dataset.al.split(',').map(Number) : [])))].sort((a, b) => a - b);
    desc.textContent = ['Vaso de fresas', ...picked.map((i) => i.value)].join(' + ');
    price.textContent = euros(total);
    const pending = picked.filter((i) => 'alPending' in i.dataset).map((i) => i.value);
    const parts = [];
    if (codes.length) parts.push('Alérgenos: ' + codes.map((c) => NAMES[c]).join(', '));
    if (pending.length) parts.push('Pregunta en tienda los alérgenos de: ' + pending.join(', '));
    al.textContent = parts.length ? parts.join(' · ') : 'Sin alérgenos de la carta';
  }

  form.addEventListener('change', update);
  form.addEventListener('submit', (e) => e.preventDefault());
  update();
})();
