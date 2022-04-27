//import { fileURLToPath, URL } from 'url'

const path = require('path')
import { defineConfig, splitVendorChunkPlugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
//import { viteCommonjs, esbuildCommonjs } from '@originjs/vite-plugin-commonjs'
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
      //viteCommonjs(),
      vue(),
      /*
      AutoImport({
          imports: [
              {
                  'axios': [
                      ['axios', 'axios'],
                  ],
              }
          ]
      }),
      //splitVendorChunkPlugin(),
      */
  ],
    /*
  optimizeDeps: {
      esbuildOptions: {
          plugins: [
              esbuildCommonjs(['jquery', 'datatables.net', ])
          ]
      }
  },
  */
  resolve: {
    alias: {
      //'@': fileURLToPath(new URL('./src', import.meta.url))
      '@': path.resolve(__dirname, "./src"),
      '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
      '@common-utils':  path.resolve(__dirname, 'src/components/common/'),
    }
  },
  build: {
      manifest: true,
      //polyfillModulePreload: false,
      target: "es2015",
      outDir: '../../static/leaseslicensing_vue',
      /*
      rollupOptions: {
          plugins: [commonjs(), resolve(), ],
          //input: 'src/main.js',
          //external: ['jquery', 'datatables.net'],
          //external: ['jquery',],
          output: {
              dir: '../../static/leaseslicensing_vue',
              format: 'cjs',
              manualChunks(id) {
                  if (id.includes('node_modules')) {
                      return 'vendor'
                  }
              }
          },
      },
      */
  },
})
