export default ({$axios, store, env}) => {
	$axios.onRequest((config) => {
		if (store.state.csrfToken !== undefined) {
			config.headers.common['csrf-token'] = store.state.csrfToken;
		}
		if (store.state.isStatic) {
			config.headers.common.cookie = `session=${env.session}`;
		}
	});
};
