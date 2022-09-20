const path = require('path')
const webpack = require('webpack');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    outputDir: path.resolve(__dirname, "../../static/leaseslicensing_vue"),
    publicPath: '/static/leaseslicensing_vue/',
    filenameHashing: false,
    //runtimeCompiler: true,
    chainWebpack: config => {
        config.resolve.alias.set('@vue-utils', path.resolve(__dirname, 'src/utils/vue'));
        config.resolve.alias.set('@common-utils', path.resolve(__dirname, 'src/components/common/'));
        //config.resolve.alias.set('datetimepicker','eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js');
        //config.resolve.alias.set('easing','jquery.easing/jquery.easing.js');
    },
    configureWebpack: {
        plugins:[
            new MiniCssExtractPlugin(),
            new webpack.ProvidePlugin({
               // use fetch api instead
               //axios: "axios",
               //
                /*
               jQuery: "jquery",
               "select2": "../node_modules/select2/dist/js/select2.full.min.js",
               */
               $: "jquery",
               moment: "moment",
               swal: "sweetalert2",
               _: 'lodash',
               select2: 'select2',
               //swal: Swal,
               //_: 'lodash',
               //datetimepicker:"../node_modules/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js"
           })
        ],
        devServer: {
            host: 'localhost',
            allowedHosts: 'all',
            devMiddleware: {
                //index: true,
                writeToDisk: true,
            }
        },
        module: {
            rules: [
              {
                test: /\.css$/i,
                use: [
                    'vue-style-loader',
                    {
                        loader: 'css-loader',
                        options: { importLoaders: 1 }
                            // enable CSS modules
                            //modules: true,
                            // customise generated class names
                            //localIdentName: '[local]_[hash:base64:8]'\
                    },
                    'postcss-loader'
                    //MiniCssExtractPlugin.loader, "css-loader"
                    //"style-loader",
                    /*
                    {
                        loader: "css-loader",
                        options: {
                            //url: true,
                            //import: true,
                            esModule: false,
                            import: {
                                filter: (url, media, resourcePath) => {
                                    console.log("url")
                                    console.log(url)
                                    if (url.includes("node_modules")) {
                                        return true;
                                    } 
                                    return false;
                                },
                            },
                        },
                    }
                    {
                        loader: "postcss-loader",
                        options: {
                            postcssOptions: {
                                plugins: [
                                    [
                                        "postcss-preset-env",
                                        {
                                            // Options
                                        },
                                    ],
                                ],
                            },
                        },
                    }
                    */
                ],
                  /*
                options: {
                    import: {
                        filter: (url, media, resourcePath) => {
                            if (url.includes("node_modules")) {
                                return true;
                            } 
                            return false;
                        },
                    },
                },
                */
              },
              /* config.module.rule('images') */
              {
                test: /\.(png|jpe?g|gif|webp|avif)(\?.*)?$/,
                type: 'asset/resource',
                generator: {
                  filename: 'img/[name][ext]'
                }
              },
              /* config.module.rule('fonts') */
              {
                test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/i,
                type: 'asset/resource',
                generator: {
                  filename: 'fonts/[name][ext]'
                }
              },
            ],
        },
    }
};
