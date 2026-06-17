import App from './App.svelte';

const app = new App({
  target: document.getElementById('app')
});

window.__PYTHIA_SEARCH_BOOTED = true;

export default app;
