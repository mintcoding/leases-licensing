import { fileURLToPath, URL } from 'url'

//import path from 'path';
//import { fileURLToPath } from 'url';
//const __filename = fileURLToPath(import.meta.url);
//console.log(__filename)
//const __dirname = path.dirname(__filename);
//console.log(__dirname)
import { defineConfig, splitVendorChunkPlugin } from 'vite'
import vue from '@vitejs/plugin-vue'
/*
import { viteCommonjs, esbuildCommonjs } from '@originjs/vite-plugin-commonjs'
*/
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
      //viteCommonjs(),
      vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@vue-utils': fileURLToPath(new URL('src/utils/vue', import.meta.url)),
      '@common-utils': fileURLToPath(new URL('src/components/common', import.meta.url)),
        /*
      '@': path.resolve(__dirname, "./src"),
      '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
      '@common-utils':  path.resolve(__dirname, 'src/components/common/'),
      */
    }
  },
  build: {
      manifest: true,
      //polyfillModulePreload: false,
      target: "es2021",
      outDir: '../../static/leaseslicensing_vue',
      rollupOptions: {
          plugins: [commonjs(), resolve(), ],
          //input: 'src/main.js',
          //external: ['jquery', 'datatables.net'],
          //external: ['jquery',],
          output: {
              //dir: '../../static/leaseslicensing_vue',
              //format: 'cjs',
              manualChunks(id) {
                  if (id.includes('node_modules')) {
                      return 'vendor'
                  }
              }
          },
      },
  },
})
