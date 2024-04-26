<template>
	<section class="JoinTeam">
		<h2 class="title"><span>Join or Create Team</span></h2>
		<div class="subtitle">In order to participate you must either join or create a team.</div>
		<div class="ctftime-login-area">
			<ctftime-login-button prefix="Join/Create team with"/>
		</div>
		<iso-link to="/teams/join" class="button join">Join Team</iso-link>
		<iso-link to="/teams/new" class="button new">Create Team</iso-link>
	</section>
</template>

<script>
import IsoLink from '~/components/IsoLink.vue';
import CtftimeLoginButton from '../components/CtftimeLoginButton.vue';
import {mapState} from 'vuex';

export default {
	components: {IsoLink, CtftimeLoginButton},
	head() {
		return {
			title: 'Team - TSG CTF',
		};
	},
	computed: {
		...mapState(['isInTeam', 'isVerified', 'isLoggedIn', 'team']),
	},
	mounted() {
		if (!this.isVerified) {
			this.$router.replace({
				path: '/confirm',
			});
			return;
		}

		if (!this.isLoggedIn) {
			this.$router.replace({
				path: '/login',
			});
			return;
		}

		if (this.isInTeam && this.team && this.team.id) {
			this.$router.replace({
				path: `/teams/${this.team.id}`,
			});
		}
	},
};
</script>

<style lang="postcss">
.JoinTeam {
	text-align: center;

	.title {
		margin-bottom: 0;
	}

	.subtitle {
		margin-bottom: 2rem;
		font-size: 1.5rem;
	}

	.button {
		display: block;
		margin: 1rem auto;
		width: 18rem;
		height: 3rem;
		line-height: 3rem;
		border-radius: 9999px;
		font-size: 1.5rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;

		&.join {
			background: linear-gradient(90deg, #3e91a6 0%, #5e0fa9 100%);
		}

		&.new {
			background: linear-gradient(90deg, #a6643e 0%, #a90f5d 100%);
		}
	}
}
</style>
