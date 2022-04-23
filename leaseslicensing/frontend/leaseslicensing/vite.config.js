//import { fileURLToPath, URL } from 'url'

const path = require('path')
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
      vue(),
        AutoImport({
            imports: [
                {
                    'axios': [
                        ['default', 'axios'],
                    ],
                }
            ]
        }),
  ],
  resolve: {
    alias: {
      //'@': fileURLToPath(new URL('./src', import.meta.url))
      '@': path.resolve(__dirname, "./src"),
      '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
      '@common-utils':  path.resolve(__dirname, 'src/components/common/'),
    }
  },
    /*
  build: {
      rollupOptions: {
          plugins: [commonjs(), resolve(), ],
          input: 'src/main.js',
          output: {
              dir: 'dist',
              format: 'cjs',
          },
      },
  },
  */
})
