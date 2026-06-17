import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'node:path';

export default defineConfig({
  root: __dirname,
  plugins: [svelte()],
  base: './',
  build: {
    outDir: resolve(__dirname, '../../sites/agoramarket.com/pages'),
    emptyOutDir: true,
    assetsDir: 'assets'
  }
});
