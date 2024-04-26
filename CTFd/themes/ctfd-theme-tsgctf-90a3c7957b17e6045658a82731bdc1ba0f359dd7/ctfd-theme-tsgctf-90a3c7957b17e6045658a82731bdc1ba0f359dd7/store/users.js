export const state = () => ({
	users: [],
});

export const getters = {
	getUser: (s) => (id) => s.users.find((user) => user.id === id),
};

export const mutations = {
	setUser(s, user) {
		s.users.push(user);
	},
};

export const actions = {
	async getUser(
		{
			commit,
			getters: {getUser},
		},
		{$axios, id},
	) {
		if (getUser(id)) {
			return;
		}
		const {data, headers} = await $axios.get(`/api/v1/users/${id}`);
		if (headers['content-type'] === 'application/json') {
			commit('setUser', data.data);
		} else {
			commit('setIsLoggedIn', false, {root: true});
		}
	},
	async getUsers({commit, dispatch}, {$axios, ids}) {
		await Promise.all(ids.map((id) => (
			dispatch('getUser', {$axios, id})
		)));
	},
};
