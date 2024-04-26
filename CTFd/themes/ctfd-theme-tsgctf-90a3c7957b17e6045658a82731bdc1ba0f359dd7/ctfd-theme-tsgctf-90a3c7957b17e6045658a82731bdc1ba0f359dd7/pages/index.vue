<template>
	<section class="Index">
		<div class="index-content">
			<h1 class="ctf-logo"><span>T</span><span>S</span><span>G</span> <span>C</span><span>T</span><span>F</span></h1>
			<p class="subtitle">Pwn, Web, Crypto, PPC, Rev, etc...</p>
			<div class="timer">{{timer}}</div>
			<div v-if="!isLoggedIn" class="buttons">
				<iso-link to="/login" class="button login">Login</iso-link>
				<iso-link to="/register" class="button register">Register</iso-link>
			</div>
		</div>
	</section>
</template>

<script>
import IsoLink from '~/components/IsoLink.vue';
import {mapState} from 'vuex';

const contestStart = new Date('2021-10-02T07:00:00Z').getTime();
const contestEnd = new Date('2021-10-03T07:00:00Z').getTime();

export default {
	components: {IsoLink},
	data() {
		return {
			remainingTime: this.getRemaining(),
		};
	},
	head() {
		return {
			title: 'TSG CTF 2021',
		};
	},
	computed: {
		timer() {
			const days = Math.floor(this.remainingTime / 1000 / 60 / 60 / 24)
				.toString()
				.padStart(2, '0');
			const hours = (Math.floor(this.remainingTime / 1000 / 60 / 60) % 24).toString().padStart(2, '0');
			const minutes = (Math.floor(this.remainingTime / 1000 / 60) % 60).toString().padStart(2, '0');
			const seconds = (Math.floor(this.remainingTime / 1000) % 60).toString().padStart(2, '0');
			return `${days}:${hours}:${minutes}:${seconds}`;
		},
		...mapState(['isLoggedIn']),
	},
	mounted() {
		this.interval = setInterval(() => {
			this.remainingTime = this.getRemaining();
		}, 1000);
	},
	destroyed() {
		clearInterval(this.interval);
	},
	methods: {
		getRemaining() {
			const now = Date.now();
			if (now > contestEnd) {
				return 0;
			}
			if (now > contestStart) {
				return contestEnd - now;
			}
			return contestStart - now;
		},
	},
};
</script>

<style lang="postcss">
@property --shadow-color {
	syntax: '<color>';
	inherits: false;
	initial-value: rgba(238, 255, 82, 0.1);
}

/* We are hacker :) */
@keyframes blinkLogo {
	0% { --shadow-color: rgba(238, 255, 82, 0.1); }
	1% { --shadow-color: rgba(238, 255, 82, 0); }

	11% { --shadow-color: rgba(238, 255, 82, 0.1); }
	11.5% { --shadow-color: rgba(238, 255, 82, 0); }
	12% { --shadow-color: rgba(238, 255, 82, 0.1); }
	12.5% { --shadow-color: rgba(238, 255, 82, 0); }
	13% { --shadow-color: rgba(238, 255, 82, 0.1); }
	13.5% { --shadow-color: rgba(238, 255, 82, 0); }

	24% { --shadow-color: rgba(238, 255, 82, 0.1); }
	25% { --shadow-color: rgba(238, 255, 82, 0); }
	25.5% { --shadow-color: rgba(238, 255, 82, 0.1); }
	26.5% { --shadow-color: rgba(238, 255, 82, 0); }
	27% { --shadow-color: rgba(238, 255, 82, 0.1); }
	27.5% { --shadow-color: rgba(238, 255, 82, 0); }

	50% { --shadow-color: rgba(238, 255, 82, 0.1); }
	51% { --shadow-color: rgba(238, 255, 82, 0); }
	51.5% { --shadow-color: rgba(238, 255, 82, 0.1); }
	52% { --shadow-color: rgba(238, 255, 82, 0); }
	52.5% { --shadow-color: rgba(238, 255, 82, 0.1); }
	53.5% { --shadow-color: rgba(238, 255, 82, 0); }
	54% { --shadow-color: rgba(238, 255, 82, 0.1); }
	54.5% { --shadow-color: rgba(238, 255, 82, 0); }

	65% { --shadow-color: rgba(238, 255, 82, 0.1); }
	66% { --shadow-color: rgba(238, 255, 82, 0); }

	76% { --shadow-color: rgba(238, 255, 82, 0.1); }
	76.5% { --shadow-color: rgba(238, 255, 82, 0); }
	77% { --shadow-color: rgba(238, 255, 82, 0.1); }
	77.5% { --shadow-color: rgba(238, 255, 82, 0); }
	78% { --shadow-color: rgba(238, 255, 82, 0.1); }
	79% { --shadow-color: rgba(238, 255, 82, 0); }
	79.5% { --shadow-color: rgba(238, 255, 82, 0.1); }
	80% { --shadow-color: rgba(238, 255, 82, 0); }
}

.Index {
	margin: 0 auto;
	height: calc(100vh - 4rem);
	display: flex;
	justify-content: center;
	align-items: center;
	text-align: center;

	.index-content {
		max-width: 100%;
	}

	.ctf-logo {
		font-family: 'Fredoka One', cursive;
		font-size: 8rem;
		font-weight: 300;
		color: rgb(252 255 68);
		-webkit-text-fill-color: transparent;
		animation: 10s blinkLogo infinite;
		animation-timing-function: step-end;
		text-shadow:
			0 0 3px var(--shadow-color),
			0 0 10px var(--shadow-color),
			0 0 20px var(--shadow-color),
			0 0 30px var(--shadow-color),
			0 0 40px var(--shadow-color),
			0 0 50px var(--shadow-color),
			0 0 70px var(--shadow-color),
			0 0 100px var(--shadow-color);
		background: linear-gradient(90deg, rgb(71 229 67) 0%, rgb(252 255 68) 100%);
		background-clip: text;
		display: block;
		letter-spacing: 1px;
		mix-blend-mode: screen;

		@media (max-width: 900px) {
			font-size: 18vw;
		}
	}

	.subtitle {
		font-family: 'Roboto', sans-serif;
		font-size: 1.5rem;
		margin-top: -1rem;
		opacity: 0.3;
	}

	.buttons {
		display: flex;
		margin-top: 1rem;
		justify-content: center;
	}

	.button {
		display: block;
		margin: 0 0.5rem;
		width: 10rem;
		height: 2.6rem;
		line-height: 2.6rem;
		border-radius: 9999px;
		font-size: 1.5rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;

		&.login {
			background: linear-gradient(90deg, #6299a7 0%, #21207d 100%);
		}

		&.register {
			background: linear-gradient(90deg, #ffc107 0%, #f44336 100%);
		}
	}

	.timer {
		margin-top: 1rem;
		font-family: 'Roboto', sans-serif;
		font-size: 4rem;
	}
}
</style>
