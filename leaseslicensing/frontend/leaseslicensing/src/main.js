// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import { createApp } from 'vue'
//import { router } from './router'
import { router } from './router/index'
import App from './App.vue'
import helpers from '@/utils/helpers'
import api_endpoints from './api'
import CKEditor from '@ckeditor/ckeditor5-vue';
//import axios from 'axios';
import jQuery from 'jquery'
import '@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css';
import '@/../node_modules/select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css';
import '@/../node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css';
import "@/../node_modules/select2/dist/css/select2.min.css";

window.jQuery = window.$ = jQuery;
/*
import moment from 'moment';
import { extendMoment } from 'moment-range';
import jszip from 'jszip';
import "sweetalert2";

import 'jquery-validation';

extendMoment(moment);

import 'datatables.net';
import 'datatables.net-bs5';
import 'datatables.net-responsive-bs';
import 'datatables.net-buttons';


// Add CSRF Token to every request
axios.interceptors.request.use( function ( config ) {
  // modify headers
  if ( config.url != api_endpoints.countries ) {
    //config.headers.set( 'X-CSRFToken', helpers.getCookie( 'csrftoken' ) );
    //config.headers.set( 'Content-Type', "application/json" );
    //config.headers.set( "Access-Control-Allow-Origin", "*" );
  }
} );
*/
console.log(axios)
/* eslint-disable no-new */
const app = createApp(App)
app.config.globalProperties.$axios = axios;
app.use(CKEditor)
console.log("router")
app.use(router)
router.isReady().then(() => app.mount('#app'))

