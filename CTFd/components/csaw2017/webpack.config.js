const webpack = require('webpack')
const path = require('path')

module.exports = {
  entry: './components/chalboard.js',
  output: {
    filename: 'chalboard.bundle.js',
    path: path.resolve(__dirname, '../../static/csaw2017/js')
  },
  module: {
    loaders: [
      {
        test: /\.jsx?/,
        loader: 'babel-loader'
      },
      {
        test: /.scss/,
        loader: 'style-loader!css-loader!sass-loader'
      }
    ]
  },
  plugins: [
    // new webpack.DefinePlugin({
    //   'process.env.NODE_ENV': JSON.stringify('production')
    // })
  ]
}