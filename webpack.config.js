const path = require('path')
const webpack = require('webpack')
const FixStyleOnlyEntriesPlugin = require("webpack-fix-style-only-entries")
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const UglifyJsPlugin = require('uglifyjs-webpack-plugin')
const RemoveStrictPlugin = require('remove-strict-webpack-plugin')

const roots = {
  'themes/core': {
    'css': {
      'challenge-board': 'assets/css/challenge-board.scss',
      'fonts': 'assets/css/fonts.scss',
      'main': 'assets/css/main.scss',
      'core': 'assets/css/core.scss',
      'codemirror': 'assets/css/codemirror.scss',
    },
    'js': {
      'pages/main': 'assets/js/pages/main.js',
      'pages/challenges': 'assets/js/pages/challenges.js',
      'pages/scoreboard': 'assets/js/pages/scoreboard.js',
      'pages/settings': 'assets/js/pages/settings.js',
      'pages/stats': 'assets/js/pages/stats.js',
      'pages/teams/private': 'assets/js/pages/teams/private.js',
    }
  },
  'themes/admin': {
    'css': {
      'admin': 'assets/css/admin.scss',
      'challenge-board': 'assets/css/challenge-board.scss',
    },
    'js': {
      'pages/main': 'assets/js/pages/main.js',
      'pages/challenge': 'assets/js/pages/challenge.js',
      'pages/configs': 'assets/js/pages/configs.js',
      'pages/notifications': 'assets/js/pages/notifications.js',
      'pages/editor': 'assets/js/pages/editor.js',
      'pages/pages': 'assets/js/pages/pages.js',
      'pages/reset': 'assets/js/pages/reset.js',
      'pages/scoreboard': 'assets/js/pages/scoreboard.js',
      'pages/statistics': 'assets/js/pages/statistics.js',
      'pages/submissions': 'assets/js/pages/submissions.js',
      'pages/team': 'assets/js/pages/team.js',
      'pages/teams': 'assets/js/pages/teams.js',
      'pages/user': 'assets/js/pages/user.js',
      'pages/users': 'assets/js/pages/users.js',
    }
  },
}

function getJSConfig(root, type, entries) {
  const out = {}
  for (let key in entries) {
    out[key] = path.resolve(__dirname, 'CTFd', root, entries[key])
  }

  return {
    entry: out,
    output: {
      path: path.resolve(__dirname, 'CTFd', root, 'static', type),
      publicPath: '/' + root + '/static/' + type,
      chunkFilename: '[name].chunk.js',
    },
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          plotly: {
            name: 'plotly',
            filename: 'plotly.bundle.js',
            test: /plotly/,
            priority: 1,
            enforce: true,
          },
          vendor: {
            name: 'vendor',
            filename: 'vendor.bundle.js',
            test: /node_modules/,
            // maxSize: 1024 * 256,
            enforce: true,
          },
          graphs: {
            name: 'graphs',
            filename: 'graphs.js',
            test: /graphs/,
            priority: 1,
            reuseExistingChunk: true,
          },
          helpers: {
            name: 'helpers',
            filename: 'helpers.js',
            test: /helpers/,
            priority: 1,
            reuseExistingChunk: true,
          },
          default: {
            filename: 'core.js',
            minChunks: 2,
            priority: -1,
            reuseExistingChunk: true,
          },
        },
      },
      minimizer: [
        new UglifyJsPlugin({
            cache: true,
            parallel: true,
            sourceMap: true
        }),
      ],
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          use: {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true,
              presets: [
                ['@babel/preset-env', { useBuiltIns: 'entry', modules: 'commonjs' }],
              ],
            }
          }
        },
      ],
    },
    plugins: [
      new webpack.NamedModulesPlugin(),
      new RemoveStrictPlugin(),
    ],
    resolve: {
      extensions: ['.js'],
      alias: {
        core: path.resolve(__dirname, 'CTFd/themes/core/assets/js/'),
      },
    },
  }
}

function getCSSConfig(root, type, entries) {
  const out = {}
  for (let key in entries) {
    out[key] = path.resolve(__dirname, 'CTFd', root, entries[key])
  }

  return {
    entry: out,
    output: {
      path: path.resolve(__dirname, 'CTFd', root, 'static', type),
      publicPath: '/' + root + '/static/' + type,
    },
    optimization: {
      minimizer: [
        new OptimizeCssAssetsPlugin({})
      ]
    },
    module: {
      rules: [
        {
          test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?(#\w+)?$/,
          use: [
            {
              loader: 'file-loader',
              options: {
                name: '[name].[ext]',
                publicPath: '../fonts',
                outputPath: '../fonts',
              }
            }
          ]
        },
        {
          test: /\.(s?)css$/,
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: 'css-loader',
              options: {
                importLoaders: 2,
              }
            },
            {
              loader: 'string-replace-loader',
              options: {
                multiple: [
                  // Replace core font-faces
                  { search: "font-face\s*{\s*font-family:\s*[\"']Lato[\"']", replace: "font-face{font-family:'LatoOffline'", flags: 'gm' },
                  { search: "font-face\s*{\s*font-family:\s*[\"']Raleway[\"']", replace: "font-face{font-family:'RalewayOffline'", flags: 'gm' },
                  // Replace Font-Awesome font-faces
                  { search: "font-face\s*{\s*font-family:\s*[\"']Font Awesome 5 Free[\"']", replace: "font-face{font-family:'Font Awesome 5 Free Offline'", flags: 'gm' },
                  { search: "font-face\s*{\s*font-family:\s*[\"']Font Awesome 5 Brands[\"']", replace: "font-face{font-family:'Font Awesome 5 Brands Offline'", flags: 'gm' },
                  // Replace Font-Awesome class rules
                  { search: "far\s*{\s*font-family:\s*[\"']Font Awesome 5 Free[\"']", replace: "far{font-family:'Font Awesome 5 Free','Font Awesome 5 Free Offline'", flags: 'gm' },
                  { search: "fas\s*{\s*font-family:\s*[\"']Font Awesome 5 Free[\"']", replace: "fas{font-family:'Font Awesome 5 Free','Font Awesome 5 Free Offline'", flags: 'gm' },
                  { search: "fab\s*{\s*font-family:\s*[\"']Font Awesome 5 Brands[\"']", replace: "fab{font-family:'Font Awesome 5 Brands','Font Awesome 5 Brands Offline'", flags: 'gm' },
                ],
                strict: true,
              }
            },
            {
              loader: 'sass-loader',
            },
          ],
        },
      ]
    },
    resolve: {
      extensions: ['.css'],
      alias: {
        core: path.resolve(__dirname, 'CTFd/themes/core/assets/css/'),
      },
    },
    plugins: [
      new FixStyleOnlyEntriesPlugin(),
      new MiniCssExtractPlugin({
        filename: '[name].css',
        chunkFilename: '[id].css'
      }),
    ],
  }
}

const mapping = {
  'js': getJSConfig,
  'css': getCSSConfig,
}

module.exports = []
for (let root in roots) {
  for (let type in roots[root]) {
    module.exports.push(mapping[type](root, type, roots[root][type]))
  }
}
