const path = require('path')
//const axios = require('axios').default;
import { defineConfig } from "vite";
import vue from '@vitejs/plugin-vue';

function resolve (dir) {
  return path.join(__dirname, '..', dir)
}

function getCookie ( name ) {
var value = null;
if ( document.cookie && document.cookie !== '' ) {
  var cookies = document.cookie.split( ';' );
  for ( var i = 0; i < cookies.length; i++ ) {
    var cookie = cookies[ i ].trim();
    if ( cookie.substring( 0, name.length + 1 )
      .trim() === ( name + '=' ) ) {
      value = decodeURIComponent( cookie.substring( name.length + 1 ) );
      break;
    }
  }
}
return value;
}

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
            '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
            '@common-utils':  path.resolve(__dirname, 'src/components/common/'),
            'datetimepicker': 'eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js',
            'easing': 'jquery.easing/jquery.easing.js',
        },
    },
    /*
    chainWebpack: config => {
        config.resolve.alias.set('@vue-utils', path.resolve(__dirname, 'src/utils/vue'));
        config.resolve.alias.set('@common-utils', path.resolve(__dirname, 'src/components/common/'));
        config.resolve.alias.set('datetimepicker','eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js');
        config.resolve.alias.set('easing','jquery.easing/jquery.easing.js');
    },
    configureWebpack: {
        plugins:[
            new webpack.ProvidePlugin({
               axios: "axios",
               $: "jquery",
               jQuery: "jquery",
               "select2": "../node_modules/select2/dist/js/select2.full.min.js",
               moment: "moment",
               swal: 'sweetalert2',
               _: 'lodash',
               datetimepicker:"../node_modules/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js"
           })
        ],
        devServer: {
            //headers: { "Access-Control-Allow_origin": "*" },
            //headers: { 'X-CSRFToken': getCookie( 'csrftoken' ) },
            proxy: "http://localhost:8080",
            //proxy: "http://api.back.end",
        }
    }
    */
});

