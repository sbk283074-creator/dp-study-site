/* BPhO Round 0 — curriculum aggregator.
   The module files (modules-1.js … modules-7.js) each push onto window.BPHO_MODULES.
   This file assembles them into the shape app.js expects. */

window.BPHO_CURRICULUM = {
  modules: (window.BPHO_MODULES || [])
};
