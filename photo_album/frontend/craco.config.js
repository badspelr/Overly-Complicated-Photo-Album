const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  webpack: {
    plugins: {
      add: [
        new BundleTracker({
          path: __dirname,
          filename: 'webpack-stats.json',
        }),
      ],
    },
    configure: (webpackConfig) => {
      webpackConfig.output.publicPath = '/static/';
      webpackConfig.output.filename = 'static/js/[name].[contenthash].js';
      webpackConfig.output.chunkFilename = 'static/js/[name].[contenthash].chunk.js';
      return webpackConfig;
    },
  },
};
