import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'url'
import vue from '@vitejs/plugin-vue';
import commonjs from '@rollup/plugin-commonjs';
import { nodeResolve } from '@rollup/plugin-node-resolve';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
      manifest: true,
      //polyfillModulePreload: false,
      target: "es2015",
      //outDir: '../../static/leaseslicensing_vue',
      rollupOptions: {
          plugins: [commonjs(), nodeResolve(), ],
          //input: 'src/main.js',
          //external: ['jquery', 'datatables.net'],
          //external: ['jquery',],
          output: {
              dir: '../../static/leaseslicensing_vue',
              //format: 'cjs',
              manualChunks(id) {
                  if (id.includes('node_modules')) {
                      return 'vendor'
                  }
              }
          },
      },
  },
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


})
