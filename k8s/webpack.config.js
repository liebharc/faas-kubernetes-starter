const path = require('path');
const webpack = require('webpack');
const { readdirSync } = require('fs');

const dir = 'services';
const entry = readdirSync(dir)
	.filter((item) => /\.(t|j)s$/.test(item))
	.filter((item) => !/\.d\.(t|j)s$/.test(item))
	.reduce(
		(acc, fileName) => ({
			...acc,
			[fileName.replace(/\.(t|j)s$/, '')]: {
				import: `./${dir}/${fileName}`,
				runtime: false,
				library: {
					type: 'umd',
				},
			},
		}),
		{}
	);

module.exports = {
	entry,
	mode: 'production',
	plugins: [new webpack.IgnorePlugin({ resourceRegExp: /^pg-native$/ })],
	module: {
		rules: [
			{
				test: /\.tsx?$/,
				use: 'ts-loader',
				exclude: /node_modules/,
			},
		],
	},
	resolve: {
		modules: ['node_modules'],
		extensions: ['.tsx', '.ts', '.js', '.json'],
	},
	target: 'node',
	devtool: 'source-map',
};
