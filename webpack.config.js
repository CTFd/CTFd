const path = require('path')
const webpack = require('webpack')
const FixStyleOnlyEntriesPlugin = require("webpack-fix-style-only-entries")
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const UglifyJsPlugin = require('uglifyjs-webpack-plugin')
const RemoveStrictPlugin = require('remove-strict-webpack-plugin')
const WebpackShellPlugin = require('webpack-shell-plugin');
const VueLoaderPlugin = require('vue-loader/lib/plugin');

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
      'pages/setup': 'assets/js/pages/setup.js',
      'pages/challenges': 'assets/js/pages/challenges.js',
      'pages/scoreboard': 'assets/js/pages/scoreboard.js',
      'pages/settings': 'assets/js/pages/settings.js',
      'pages/stats': 'assets/js/pages/stats.js',
      'pages/notifications': 'assets/js/pages/notifications.js',
      'pages/teams/private': 'assets/js/pages/teams/private.js',
    }
  },
  'themes/admin': {
    'css': {
      'admin': 'assets/css/admin.scss',
      'challenge-board': 'assets/css/challenge-board.scss',
      'codemirror': 'assets/css/codemirror.scss',
    },
    'js': {
      'pages/main': 'assets/js/pages/main.js',
      'pages/challenge': 'assets/js/pages/challenge.js',
      'pages/challenges': 'assets/js/pages/challenges.js',
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

function getJSConfig(root, type, entries, mode) {
  const out = {}
  const ext = mode == 'development' ? 'dev' : 'min'
  const chunk_file = `[name].${ext}.chunk.js`

  for (let key in entries) {
    out[key] = path.resolve(__dirname, 'CTFd', root, entries[key])
  }

  return {
    entry: out,
    mode: mode,
    output: {
      path: path.resolve(__dirname, 'CTFd', root, 'static', type),
      publicPath: '/' + root + '/static/' + type,
      filename: `[name].${ext}.js`,
      chunkFilename: chunk_file,
    },
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          echarts: {
            name: 'echarts',
            filename: `echarts.bundle.${ext}.js`,
            test: /echarts/,
            priority: 1,
            enforce: true,
          },
          vendor: {
            name: 'vendor',
            filename: `vendor.bundle.${ext}.js`,
            test: /node_modules/,
            // maxSize: 1024 * 256,
            enforce: true,
          },
          graphs: {
            name: 'graphs',
            filename: `graphs.${ext}.js`,
            test: /graphs/,
            priority: 1,
            reuseExistingChunk: true,
          },
          helpers: {
            name: 'helpers',
            filename: `helpers.${ext}.js`,
            test: /helpers/,
            priority: 1,
            reuseExistingChunk: true,
          },
          components: {
            name: 'components',
            filename: `components.${ext}.js`,
            test: /components/,
            priority: 1,
            reuseExistingChunk: true,
          },
          default: {
            filename: `core.${ext}.js`,
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
            uglifyOptions: {
              compress: {
                // Remove console.log in production
                drop_console: mode === 'production'
              },
            },
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
        {
          test: /\.vue$/,
          loader: 'vue-loader',
          options: {
            loaders: {
              css: ['vue-style-loader', {
                loader: 'css-loader',
              }],
              js: [
                'babel-loader',
              ],
            },
            cacheBusting: true,
          },
        },
        // This rule is magically used to load the <style> section of VueJS SFC.
        // Don't really understand what magic Vue is using here but it works.
        {
          test: /\.css$/,
          use: [
            'vue-style-loader',
            'css-loader'
          ]
        },
      ],
    },
    plugins: [
      new VueLoaderPlugin(),
      new webpack.NamedModulesPlugin(),
      new RemoveStrictPlugin(),
      // Identify files that are generated in development but not in production and create stubs to avoid a 404
      // Pretty nasty hack, would be a little better if this was purely JS
      new WebpackShellPlugin({
        onBuildEnd:[
          mode == 'development' ? 'echo Skipping JS stub generation' : 'python3 -c \'exec(\"\"\"\nimport glob\nimport os\n\nstatic_js_dirs = [\n    "CTFd/themes/core/static/js/**/*.dev.js",\n    "CTFd/themes/admin/static/js/**/*.dev.js",\n]\n\nfor js_dir in static_js_dirs:\n    for path in glob.glob(js_dir, recursive=True):\n        if path.endswith(".dev.js"):\n            path = path.replace(".dev.js", ".min.js")\n            if os.path.isfile(path) is False:\n                open(path, "a").close()\n\"\"\")\''
        ],
        safe: true,
      }),
    ],
    resolve: {
      extensions: ['.js'],
      alias: {
        core: path.resolve(__dirname, 'CTFd/themes/core/assets/js/'),
      },
    },
  }
}

function getCSSConfig(root, type, entries, mode) {
  const out = {}
  const ext = mode == 'development' ? 'dev' : 'min'
  const ouptut_file = `[name].${ext}.css`
  const chunk_file = `[id].${ext}.css`

  for (let key in entries) {
    out[key] = path.resolve(__dirname, 'CTFd', root, entries[key])
  }

  return {
    entry: out,
    mode: mode,
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
        filename: ouptut_file,
        chunkFilename: chunk_file
      }),
    ],
  }
}

const mapping = {
  'js': getJSConfig,
  'css': getCSSConfig,
}

module.exports = (env, options) => {
  let output = []
  let mode = options.mode
  for (let root in roots) {
    for (let type in roots[root]) {
      let entry = mapping[type](root, type, roots[root][type], mode);
      output.push(entry)
    }
  }
  return output
}
