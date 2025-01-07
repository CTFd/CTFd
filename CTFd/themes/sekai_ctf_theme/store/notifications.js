export const state = () => ({
	notifications: [],
});

export const getters = {
	getNotifications: (s) => s.notifications
		.slice()
		.sort((a, b) => b.id - a.id)
		.map((notification) => ({
			...notification,
			date: new Date(notification.date),
		})),
};

export const mutations = {
	setNotifications(s, payload) {
		s.notifications = payload;
	},
};

export const actions = {
	async updateNotifications({commit}, {$axios}) {
		const {data, headers} = await $axios.get('/api/v1/notifications');
		if (headers['content-type'] === 'application/json') {
			commit('setNotifications', data.data);
		} else {
			commit('setIsLoggedIn', false, {root: true});
		}
	},
};
