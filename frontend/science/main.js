// Entry for the phase-3 science sections. Each page carries one root element; only the matching
// module is loaded (code splitting keeps the shared chart helpers in one chunk).
const pages = [
  ['se', () => import('./estimation.js')],
  ['rk', () => import('./ranking.js')],
  ['bm', () => import('./benchmark.js')],
];
for (const [id, load] of pages) {
  const root = document.getElementById(id);
  if (!root) continue;
  load().then(m => m.init()).catch(err => {
    const s = document.getElementById(`${id}-status`);
    if (s) s.textContent = `Não foi possível carregar os dados da análise (${err.message}).`;
  });
}
