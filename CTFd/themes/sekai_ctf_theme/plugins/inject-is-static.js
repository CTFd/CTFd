export default ({app}, inject) => {
	app.isStatic = process.env.NUXT_ENV_STATIC === 'true';
};
