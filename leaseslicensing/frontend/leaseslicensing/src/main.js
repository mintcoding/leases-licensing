// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
//import Vue from 'vue'
console.log("main.js")
console.log(process.env.NODE_ENV)
console.log("dev")
//import { createApp } from 'vue/dist/vue.esm-browser.js'
import { createApp } from 'vue'
//import { Resource } from 'vue-resource'
import { router } from './router'
import App from './App.vue'
import helpers from '@/utils/helpers'
//import hooks from '@/utils/hooks'
//import hooks from './packages'
import api_endpoints from './api'
import CKEditor from '@ckeditor/ckeditor5-vue';
import axios from 'axios';
//import("./scss/custom.scss");
//require('../node_modules/font-awesome/css/font-awesome.min.css' )
require('@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css')
require('@/../node_modules/select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css')
require('@/../node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css')
//require('@/../node_modules/datatables.net-bs/css/dataTables.bootstrap.min.css')

/*
Vue.config.devtools = true;
Vue.config.productionTip = false
Vue.use( resource );

// ckeditor4 is installed in 'wildlifecompliance/templates/wildlifecompliance/base.html'
import CKEditor from 'ckeditor4-vue';
Vue.use( CKEditor );
*/
// Add CSRF Token to every request
axios.interceptors.request.use( function ( config ) {
  // modify headers
  if ( config.url != api_endpoints.countries ) {
      /*
    config.headers.set( 'X-CSRFToken', helpers.getCookie( 'csrftoken' ) );
    config.headers.set( 'Content-Type', "application/json" );
    config.headers.set( "Access-Control-Allow-Origin", "*" );
    */
  }
} );

/* eslint-disable no-new */
const app = createApp(App)
app.config.globalProperties.$axios = axios;
app.use(CKEditor)
console.log("router")
app.use(router)
//app.use(Resource)
router.isReady().then(() => app.mount('#app'))
//app.mount('#app')

