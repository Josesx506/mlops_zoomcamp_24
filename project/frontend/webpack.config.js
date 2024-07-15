const path = require("path");
const json5 = require("json5");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { DefinePlugin } = require("webpack");

module.exports = {
    mode: "development",
    entry: "./src/index.js",
    devServer: {
      static: {
        directory: path.join(__dirname, "dist"),
      },
      compress: true,
      port: 9300,
      historyApiFallback: true,
    },
    output: {
      filename: "bundle.js",
      path: path.resolve(__dirname, "dist"),
      clean: true,
    },
    module: {
      rules: [
        {
          test: /\.css$/i,
          use: ["style-loader", "css-loader"],
        },
        {
          test: /\.(png|svg|jpg|jpeg|gif)$/i,
          type: "asset/resource",
        },
        {
          test: /\.(woff|woff2|eot|truetype|opentype)$/i,
          type: "asset/resource",
        },
        {
          test: /\.(geojson)$/,
          use: ["file-loader"],
        },
      ],
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: "./src/index.html",
            filename: "index.html",
            inject: "body",
            scriptLoading: "defer",
        }),
      new DefinePlugin({
        "process.env.APP_SERVER_HOST": JSON.stringify(process.env.APP_SERVER_HOST || "http://127.0.0.1:8534")
      })
    ],
};