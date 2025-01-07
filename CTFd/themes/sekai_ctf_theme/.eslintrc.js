module.exports = {
	root: true,
	ignorePatterns: ['static/**/*.js'],
	env: {
		browser: true,
		node: true,
	},
	parserOptions: {
		parser: 'babel-eslint',
	},
	extends: ['@nuxtjs', '@hakatashi'],
	plugins: ['prettier'],
	rules: {
		'node/no-unsupported-features': 'off',
		'node/no-unsupported-features/es-syntax': 'off',
		semi: ['error', 'always'],
		'import/order': 'off',
		'import/extensions': 'off',
		// destroyed was introduced in Vue v3
		'vue/no-deprecated-destroyed-lifecycle': 'off',
	},
	settings: {
		'import/resolver': 'nuxt',
	},
};
