// Ayudas públicas en modo «ventana»: el enlace del pie abre la información en una ventana encima de la página.
// Sin JS (o sin <dialog>), el enlace lleva a la página de financiación.
(function () {
  const dlg = document.getElementById('fin-dialogo');
  if (!dlg || typeof dlg.showModal !== 'function') return;
  let origen = null;
  document.querySelectorAll('[data-fin-abrir]').forEach((a) => a.addEventListener('click', (e) => {
    e.preventDefault();
    origen = a;
    dlg.showModal();
    document.documentElement.classList.add('fin-abierto');
  }));
  dlg.querySelector('[data-fin-cerrar]').addEventListener('click', () => dlg.close());
  // Un toque fuera de la ventana (en el fondo oscuro) también la cierra.
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('close', () => {
    document.documentElement.classList.remove('fin-abierto');
    if (origen) origen.focus();
  });
})();
