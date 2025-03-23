//импортим все нужные плагины
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const webpack = require('webpack');

module.exports = (env) => {

    const isDev = env.mode === 'development'; 
    const isProd = !isDev; 

    return {    

        mode: env.mode ?? 'development', 

        entry: path.resolve(__dirname, 'src', 'index.js'), 

        output: {
            filename: '[name].[contenthash].js', 
            path: path.resolve(__dirname, 'build'), 
            assetModuleFilename: "assets/[hash][ext]",
            clean: true 
        },

        module: { 
            rules: [
                
                {
                    test: /\.html$/i,
                    loader: "html-loader", 
                }, 

                {
                    test: /\.css$/i, 
                    use: [
                      
                      isDev ? "style-loader" : MiniCssExtractPlugin.loader, 
                      
                      "css-loader",
                      {
                        loader: "postcss-loader", 
                        options: {
                            postcssOptions: {
                                plugins: [require('postcss-preset-env')]
                            }
                        }
                      },
                    ],
                },

                {
                    test: /\.otf?$/i, 
                    type: "asset/resource",
                    generator: {
                        filename: 'fonts/[name][ext]'
                    }
                },
                {
                    test: /\.(?:js|mjs|cjs)$/, 
                    exclude: /node_modules/,
                    use: {
                      loader: 'babel-loader',
                      options: {
                        presets: [
                          ['@babel/preset-env', { targets: "defaults" }]
                        ]
                      }
                    }
                },
            ]
        },

        plugins: [
            new HtmlWebpackPlugin({ template: path.resolve(__dirname, 'src', 'index.html') }),
            !isDev && new MiniCssExtractPlugin() 
        ],

        devtool: isDev && 'inline-source-map', 

        devServer: isDev ? {
            port: env.port ?? 3000,
            hot: true,
        } : undefined,
    }
}