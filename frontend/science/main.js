// Entry for the phase-3 science sections. Each page carries one root element; only the matching
// module is loaded (code splitting keeps the shared chart helpers in one chunk).
const pages = [
  ['se', () => import('./estimation.js')],
  ['rk', () => import('./ranking.js')],
  ['bm', () => import('./benchmark.js')],
  ['nv', () => import('./bearings.js').then(m => ({ init: m.initNVH }))],
  ['an', () => import('./bearings.js').then(m => ({ init: m.initAnomaly }))],
  ['sg', () => import('./bearings.js').then(m => ({ init: m.initSignatures }))],
  ['ru', () => import('./degradation.js').then(m => ({ init: m.initRUL }))],
  ['pu', () => import('./degradation.js').then(m => ({ init: m.initPump }))],
  ['ol', () => import('./degradation.js').then(m => ({ init: m.initOil }))],
  ['cp', () => import('./energy.js').then(m => ({ init: m.initChangepoint }))],
  ['pk', () => import('./energy.js').then(m => ({ init: m.initPeak }))],
  ['cl', () => import('./energy.js').then(m => ({ init: m.initClimate }))],
];
for (const [id, load] of pages) {
  const root = document.getElementById(id);
  if (!root) continue;
  load().then(m => m.init()).catch(err => {
    const s = document.getElementById(`${id}-status`);
    if (s) s.textContent = `Não foi possível carregar os dados da análise (${err.message}).`;
  });
}
