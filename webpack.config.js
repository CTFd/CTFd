const path = require('path')
const webpack = require('webpack')
const FixStyleOnlyEntriesPlugin = require("webpack-fix-style-only-entries")
const MiniCssExtractPlugin = require("mini-css-extract-plugin")
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const UglifyJsPlugin = require("uglifyjs-webpack-plugin")

const roots = {
  'themes/core': {
    'css/main': 'assets/css/main.css',
    'css/challenge-board': 'assets/css/challenge-board.css',
    'css/fonts': 'assets/css/fonts.css',
  },
  // 'themes/admin': {
  //   'css/main': 'assets/css/main.css',
  //   'css/challenge-board': 'assets/css/challenge-board.css',
  //   'css/editor': 'assets/css/editor.css',
  // }
}

let baseConfig = {
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        cache: true,
        parallel: true,
        sourceMap: true
      }),
      new OptimizeCssAssetsPlugin({})
    ]
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true,
            presets: ['@babel/preset-env'],
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
        ],
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'fonts',
            }
          }
        ]
      }
    ]
  },
  resolve: {
    extensions: ['.js'],
  },
  plugins: [
    new FixStyleOnlyEntriesPlugin(),
    new MiniCssExtractPlugin({
      filename: '[name].css',
      chunkFilename: '[id].css'
    }),
    new webpack.NamedModulesPlugin(),
  ],
}

module.exports = []
for(let root in roots) {
  const entries = roots[root]
  const config = Object.assign({}, baseConfig)
  config.output = {
    path: path.resolve(__dirname, 'CTFd', root, 'static'),
    publicPath: '/' + root + '/static/',
  };

  config.entry = {}
  for(let key in entries) {
    config.entry[key] = path.resolve(__dirname, 'CTFd', root, entries[key])
  }

  module.exports.push(config)
}
