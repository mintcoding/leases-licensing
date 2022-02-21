// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import resource from 'vue-resource'
import App from './App'
import router from './router'
import helpers from '@/utils/helpers'
import hooks from './packages'
import api_endpoints from './api'
//import("./scss/custom.scss");
//require('../node_modules/font-awesome/css/font-awesome.min.css' )
require('@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css')
require('@/../node_modules/select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css')
//require('@/../node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css')
//require('@/../node_modules/datatables.net-bs/css/dataTables.bootstrap.min.css')

Vue.config.devtools = true;
Vue.config.productionTip = false
Vue.use( resource );

// ckeditor4 is installed in 'wildlifecompliance/templates/wildlifecompliance/base.html'
import CKEditor from 'ckeditor4-vue';
Vue.use( CKEditor );

// Add CSRF Token to every request
Vue.http.interceptors.push( function ( request, next ) {
  // modify headers
  if ( request.url != api_endpoints.countries ) {
    request.headers.set( 'X-CSRFToken', helpers.getCookie( 'csrftoken' ) );
  }

  // continue to next interceptor
  next();
} );


/* eslint-disable no-new */
new Vue( {
  el: '#app',
  router,
  template: '<App/>',
  components: {
    App
  }
} )
