import get from 'lodash/get';
import {Mutex} from 'async-mutex';

const mutex = new Mutex();

export const state = () => ({
	scoreboard: [],
	teams: [],
});

export const getters = {
	getScore: (s) => (id) => s.scoreboard.find((team) => team.account_id === id) || {
		score: 0,
		pos: s.scoreboard.length + 1,
	},
	getScoreboard: (s) => {
		const listedTeams = new Set(s.scoreboard.map((team) => team.account_id));
		const nonListedTeams = s.teams.filter(({id}) => !listedTeams.has(id));
		const teamsMap = new Map(s.teams.map((team) => [team.id, team]));

		return [
			...s.scoreboard.map((team) => ({
				...team,
				country: teamsMap.has(team.account_id) ? teamsMap.get(team.account_id).country : null,
			})),
			...nonListedTeams.map((team) => ({
				name: team.name,
				account_id: team.id,
				country: team.country,
				pos: s.scoreboard.length + 1,
				oauth_id: team.oauth_id,
				score: 0,
			})),
		];
	},
};

export const mutations = {
	setScoreboard(s, scoreboard) {
		s.scoreboard = scoreboard;
	},
	setTeams(s, teams) {
		s.teams = teams;
	},
	pushTeams(s, teams) {
		s.teams.push(...teams);
	},
	clearTeams(s) {
		s.teams = [];
	},
};

export const actions = {
	async update({dispatch}, {$axios}) {
		await Promise.all([
			dispatch('updateScoreboard', {$axios}),
			dispatch('updateTeams', {$axios}),
		]);
	},
	async updateScoreboard({commit}, {$axios}) {
		const {data, headers} = await $axios.get('/api/v1/scoreboard');
		if (headers['content-type'] === 'application/json') {
			commit('setScoreboard', data.data);
		} else {
			commit('setIsLoggedIn', false, {root: true});
		}
	},
	async updateTeams({commit, state: s}, {$axios}) {
		await mutex.runExclusive(async () => {
			const isTeamsAlreadyFetched = s.teams.length !== 0;

			const teams = [];
			let page = 1;
			while (true) {
				const {data, headers} = await $axios.get('/api/v1/teams', {params: {page}});
				if (headers['content-type'] !== 'application/json') {
					commit('setIsLoggedIn', false, {root: true});
					return;
				}

				const newTeams = get(data, ['data'], []);

				if (isTeamsAlreadyFetched) {
					teams.push(...newTeams);
				} else {
					commit('pushTeams', newTeams);
				}

				const next = get(data, ['meta', 'pagination', 'next'], null);
				if (next === null) {
					break;
				}

				await new Promise((resolve) => {
					setTimeout(resolve, 500);
				});

				page++;
			}

			if (isTeamsAlreadyFetched) {
				commit('setTeams', teams);
			}
		});
	},
};
