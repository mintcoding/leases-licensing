// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
//import Vue from 'vue'
import { createApp } from 'vue';
import router from './router';
import App from './App';
import helpers from '@/utils/helpers';
import api_endpoints from './api';
import CKEditor from '@ckeditor/ckeditor5-vue';

import { extendMoment } from 'moment-range';
import jszip from 'jszip';

import "datatables.net-bs5";
import "datatables.net-buttons-bs5";
import "datatables.net-responsive-bs5";
import 'datatables.net-buttons/js/dataTables.buttons.js';
import 'datatables.net-buttons/js/buttons.html5.js';

import 'jquery-validation';
//import './global.css';
/*
@import url('~sweetalert2/dist/sweetalert2.css');
@import url('~@fortawesome/fontawesome-free/css/all.min.css');
@import url('~select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css');
@import url('~datatables.net-bs5/css/dataTables.bootstrap5.min.css');

@import '~sweetalert2/dist/sweetalert2.css';
@import '~@fortawesome/fontawesome-free/css/all.min.css';
@import '~select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css';
@import '~datatables.net-bs5/css/dataTables.bootstrap5.min.css';
*/

import '../node_modules/sweetalert2/dist/sweetalert2.css';
import '../node_modules/@fortawesome/fontawesome-free/css/all.min.css';
import '../node_modules/select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css';
import '../node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css';

extendMoment(moment);

// Add CSRF Token to every request
const customHeaders = new Headers({
    'X-CSRFToken': helpers.getCookie( 'csrftoken' ),
});
const customHeadersJSON = new Headers({
    'X-CSRFToken': helpers.getCookie( 'csrftoken' ),
    'Content-Type': 'application/json',
});
fetch = (originalFetch => {
    return (...args) => {
        if (args.length > 1) {
            //console.log(typeof(args[1].body))
            if (typeof(args[1].body) === 'string') {
                args[1].headers = customHeadersJSON;
            } else {
                args[1].headers = customHeaders;
            }
            //console.log(args[1].headers)
            //args[1].headers = customHeaders;
        }
        const result = originalFetch.apply(this, args);
        //return result.then(console.log('Request was sent'));
        return result;
    };
})(fetch);
/* eslint-disable no-new */
const app = createApp(App)

app.use(CKEditor)
app.use(router)
router.isReady().then(() => app.mount('#app'))
//app.mount('#app')

