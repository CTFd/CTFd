<template>
	<section class="JoinTeam">
		<h2 class="title"><span>Join Team</span></h2>
		<div class="subtitle">Please enter team name and password provided by your team leader.</div>
		<form
			class="login-form"
			method="post"
			accept-charset="utf-8"
			autocomplete="off"
		>
			<div class="form-group">
				<label for="name-input">
					Team Name
				</label>
				<input
					id="name-input"
					class="form-control"
					type="text"
					name="name"
				>
			</div>
			<div class="form-group">
				<label for="password-input">
					Team Password
				</label>
				<input
					id="password-input"
					class="form-control"
					type="password"
					name="password"
				>
			</div>
			<div>
				<button id="submit" type="submit" tabindex="5">
					Join
				</button>
			</div>
			<input type="hidden" name="nonce" :value="csrfToken">
		</form>
	</section>
</template>

<script>
import {mapState} from 'vuex';

export default {
	async asyncData(context) {
		await context.store.dispatch('updateCsrfToken', context);
	},
	data() {
		return {
			isError: false,
		};
	},
	head() {
		return {
			title: 'Join Team - TSG CTF',
		};
	},
	computed: {
		...mapState(['csrfToken']),
	},
	mounted() {
		if (document.referrer) {
			const referrer = new URL(document.referrer);
			if (referrer.pathname === '/teams/join') {
				this.isError = true;
			}
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

		a {
			color: #90cbff;
		}
	}

	.form-group {
		display: flex;
		justify-content: center;
		line-height: 2rem;
		padding: 0.6rem 0;
		align-items: center;
	}

	label {
		font-size: 1rem;
		width: 10rem;
		text-align: right;
		padding-right: 1rem;
	}

	.form-control {
		font-size: 1.2rem;
		width: 20rem;
	}

	button[type='submit'] {
		width: 10rem;
		margin: 1rem 0;
	}
}
</style>
