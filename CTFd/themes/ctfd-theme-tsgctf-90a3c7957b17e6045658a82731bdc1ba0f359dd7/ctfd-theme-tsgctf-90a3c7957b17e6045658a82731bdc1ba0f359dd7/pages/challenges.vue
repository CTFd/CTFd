<template>
	<section class="Challenges">
		<h2 class="title"><span>Challenges</span></h2>
		<div v-if="isStarted" class="hide-solved">
			<input id="checkbox" v-model="isHideSolved" type="checkbox">
			<label for="checkbox">Hide solved</label>
		</div>
		<div v-if="isEnded" class="ended">TSG CTF has been ended!<br>Thank you for your pariticipation!</div>
		<div v-if="isStarted">
			<div v-for="category in categories" :key="category.name" class="category">
				<h3 class="category-name">{{category.name}}</h3>
				<ul class="challenges">
					<challenge
						v-for="challenge in category.challenges.filter(({solved}) => !isHideSolved || !solved)"
						:key="challenge.id"
						:challenge="challenge"
					/>
				</ul>
			</div>
		</div>
		<div v-else class="not-started">
			<p>Hang tight!</p>
			<p class="protip">
				ProTip: We listen to
				<a
					v-if="melody === 0"
					href="https://www.youtube.com/watch?v=d_T1StgldnM"
					target="_blank"
					rel="noopener noreferrer"
				>
					the aesthetic Iwashi melody
				</a>
				<a
					v-if="melody === 1"
					href="https://www.youtube.com/watch?v=ceyr4ezheOg"
					target="_blank"
					rel="noopener noreferrer"
				>
					the comfortable Maguro melody
				</a>
				<a
					v-if="melody === 2"
					href="https://www.youtube.com/watch?v=C9PFVo1FEwU"
					target="_blank"
					rel="noopener noreferrer"
				>
					the cozy Yatsume melody
				</a>
				<a
					v-if="melody === 3"
					href="https://www.youtube.com/watch?v=ok7UX3utzvI"
					target="_blank"
					rel="noopener noreferrer"
				>
					the intoxicant Kurage melody
				</a>
				to tune up our mind. Follow us?
			</p>
		</div>
	</section>
</template>

<script>
import {mapGetters, mapState} from 'vuex';
import Challenge from '~/components/Challenge.vue';

export default {
	components: {Challenge},
	async asyncData(context) {
		await Promise.all([
			context.store.dispatch('updateDates', context),
			context.store.dispatch('challenges/updateChallenges', context),
		]);
	},
	data() {
		return {
			melody: 0,
			isHideSolved: false,
		};
	},
	head() {
		return {
			title: 'Challenges - TSG CTF',
		};
	},
	computed: {
		...mapGetters({
			categories: 'challenges/getCategories',
		}),
		...mapState({
			isStatic: 'isStatic',
			isLoggedIn: 'isLoggedIn',
			isStarted: 'isStarted',
			isEnded: 'isEnded',
			isVerified: 'isVerified',
			isInTeam: 'isInTeam',
			challenges: (state) => state.challenges.challenges,
		}),
	},
	watch: {
		isInTeam(newValue) {
			if (newValue === false) {
				this.$router.replace({
					path: '/team',
				});
			}
		},
	},
	mounted() {
		if (!this.isStatic && !this.isVerified) {
			this.$router.replace({
				path: '/confirm',
			});
			return;
		}

		if (!this.isStatic && !this.isLoggedIn) {
			this.$router.replace({
				path: '/login',
			});
			return;
		}

		if (!this.isStatic && !this.isInTeam) {
			this.$router.replace({
				path: '/team',
			});
		}

		this.melody = Math.floor(Math.random() * 4);
		if (!this.isStatic) {
			this.interval = setInterval(() => {
				this.$store.dispatch('updateDates', {$axios: this.$axios});
				this.$store.dispatch('challenges/updateChallenges', {$axios: this.$axios});
			}, 60 * 1000);
		}
	},
	destroyed() {
		clearInterval(this.interval);
	},
};
</script>

<style lang="postcss">
.Challenges {
	max-width: 800px;
	margin: 0 auto;
	min-height: 100vh;

	.title {
		margin-bottom: 0;
		word-break: break-word;
	}

	.hide-solved {
		text-align: center;
		font-family: 'Roboto';
		font-size: 1.2rem;
	}

	.ended {
		font-size: 2rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;
		text-align: center;
		text-transform: uppercase;
		letter-spacing: 1px;
		margin-top: 3rem;
		margin-bottom: 1rem;
		word-break: break-word;
	}

	.category {
		margin-top: 3rem;
		text-align: center;
	}

	.category-name {
		display: inline-block;
		text-transform: capitalize;
		font-family: 'Roboto';
		font-size: 2rem;
		text-align: center;
		padding: 0.5rem 1rem;
		background: #520514;
		position: relative;
		margin-bottom: 1rem;

		&::before {
			content: '';
			position: absolute;
			border: dashed 1px white;
			top: 0.2rem;
			left: 0.2rem;
			right: 0.2rem;
			bottom: 0.2rem;
			opacity: 0.5;
		}
	}

	.challenges {
		list-style: none;
		padding: 0;
	}

	.not-started {
		text-align: center;
		font-size: 2.5rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;
		padding: 0;
		margin-top: 6rem;
		line-height: 2rem;
	}

	.protip {
		font-family: 'Roboto';
		font-size: 1rem;
		margin-top: 2rem;
		opacity: 0.3;

		a {
			color: cyan;
		}
	}
}
</style>
