<template>
	<section class="Team">
		<h2 class="title">
			<span>{{team.name}}</span>
		</h2>
		<div v-if="team.oauth_id" class="verified">
			<a
				class="verified-badge"
				:href="`https://ctftime.org/team/${team.oauth_id}`"
				target="_blank"
				rel="noopener noreferrer"
			>
				<span>Verified with CTFTime</span>
				<check-circle :size="16"/>
			</a>
		</div>
		<div class="score">{{formatOrdinals(score.pos)}} {{score.score}}pts</div>
		<div class="members-head">Members</div>
		<div class="members">
			<div v-for="member in team.members" :key="member" class="member">
				<span v-if="getUser(member)">{{getUser(member).name}}</span>
				<pulse-loader v-else color="white" size="10px"/>
			</div>
		</div>
		<div class="table-wrap">
			<table class="scoreboard">
				<thead>
					<tr>
						<td scope="col"><b>Challenge</b></td>
						<td scope="col"><b>Category</b></td>
						<td scope="col"><b>Value</b></td>
						<td scope="col"><b>Solver</b></td>
						<td scope="col"><b>Time</b></td>
					</tr>
				</thead>
				<tbody>
					<tr v-for="solve in team.solves" :key="solve.challenge_id">
						<td>
							<b>{{solve.challenge.name}}</b>
						</td>
						<td>{{solve.challenge.category}}</td>
						<td>{{solve.challenge.value}}</td>
						<td>
							<span v-if="getUser(solve.user)">
								{{getUser(solve.user).name}}
							</span>
							<pulse-loader v-else color="white" size="10px"/>
						</td>
						<td><iso-timeago :datetime="solve.date" :auto-update="60"/></td>
					</tr>
				</tbody>
			</table>
		</div>
	</section>
</template>

<script>
import {mapGetters, mapState} from 'vuex';
import IsoTimeago from '~/components/IsoTimeago.vue';
import CheckCircle from 'vue-material-design-icons/CheckCircle.vue';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

// https://stackoverflow.com/a/13627586/2864502
const formatOrdinals = (i) => {
	const j = i % 10;
	const k = i % 100;
	if (j === 1 && k !== 11) {
		return `${i}st`;
	}
	if (j === 2 && k !== 12) {
		return `${i}nd`;
	}
	if (j === 3 && k !== 13) {
		return `${i}rd`;
	}
	return `${i}th`;
};

export default {
	components: {PulseLoader, IsoTimeago, CheckCircle},
	async asyncData(context) {
		const [team] = await Promise.all([
			context.store.dispatch('teams/getTeam', {...context, id: context.route.params.id}),
			context.store.dispatch('scoreboard/updateScoreboard', context),
		]);
		if (team === null) {
			context.error({statusCode: 404, message: 'Team not found'});
		}
	},
	head() {
		return {
			title: `Team ${this.team && this.team.name} - TSG CTF`,
		};
	},
	computed: {
		team(context) {
			return this.teams.get(parseInt(this.$route.params.id)) || {};
		},
		score(context) {
			return this.$store.getters['scoreboard/getScore'](parseInt(this.$route.params.id)) || {};
		},
		...mapState({
			isStatic: 'isStatic',
			isLoggedIn: 'isLoggedIn',
			isVerified: 'isVerified',
			teams: (state) => state.teams.teams,
		}),
		...mapGetters({
			getUser: 'users/getUser',
		}),
	},
	mounted() {
		if (!this.isStatic && !this.isLoggedIn) {
			this.$router.replace({
				path: '/login',
			});
			return;
		}

		if (!this.isStatic && !this.isVerified) {
			this.$router.replace({
				path: '/confirm',
			});
			return;
		}

		const solvers = Array.from(new Set([...this.team.solves.map(({user}) => user), ...this.team.members]));
		this.$store.dispatch('users/getUsers', {$axios: this.$axios, ids: solvers});
	},
	methods: {formatOrdinals},
};
</script>

<style lang="postcss">
.Team {
	.title {
		text-transform: none;
		margin-bottom: 0;
		z-index: -1;
		display: flex;
		justify-content: center;
		flex-direction: column;
		align-items: center;

		&::before {
			content: 'Team';
			font-family: initial;
			color: rgba(255, 255, 255, 0.6);
			font-size: 1rem;
			line-height: 0.2rem;
			text-align: center;
			left: 0;
			right: 0;
			bottom: calc(100% - 0.3rem);
		}
	}

	.verified {
		margin: 1rem 0;
		text-align: center;
	}

	.verified-badge {
		display: inline-block;
		margin: 0 auto;
		background-color: #c31b1b;
		color: white;
		height: 1.5rem;
		line-height: 1.5rem;
		padding: 0 1rem;
		border-radius: 0.5rem;

		& > *, svg {
			vertical-align: text-bottom;
		}
	}

	.score {
		text-align: center;
		font-family: 'Roboto';
		font-size: 2rem;
	}

	.members-head {
		font-family: 'Roboto';
		font-size: 1.2rem;
		text-align: center;
		margin-top: 2rem;
	}

	.members {
		display: flex;
		flex-wrap: wrap;
		width: 100%;
		max-width: 30rem;
		margin: 0 auto 0;
		justify-content: center;
	}

	.member {
		font-size: 1.5rem;
		margin: 0 0.5rem;
	}

	table {
		max-width: 1000px;
		margin-top: 4rem;
	}

	thead {
		font-size: 1.4rem;
	}

	tbody {
		font-size: 1.2rem;
	}
}
</style>
