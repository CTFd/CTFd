<template>
	<section class="Register">
		<h2 class="title"><span>Register</span></h2>
		<div class="subtitle">or <iso-link to="/login">Login</iso-link></div>
		<div class="ctftime-login-area">
			<ctftime-login-button prefix="Register with"/>
		</div>
		<hr>
		<h3 class="title"><span>Legacy Registration</span></h3>
		<form
			class="login-form"
			:class="{active: isLegacyActive}"
			method="post"
			accept-charset="utf-8"
			autocomplete="off"
			@click="isLegacyActive = true"
		>
			<div class="form-group">
				<label for="name-input">
					User Name
				</label>
				<input
					id="name-input"
					class="form-control"
					type="text"
					name="name"
				>
			</div>
			<div class="form-group">
				<label for="email-input">
					Email
				</label>
				<input
					id="email-input"
					class="form-control"
					type="email"
					name="email"
				>
			</div>
			<div class="form-group">
				<label for="password-input">
					Password
				</label>
				<input
					id="password-input"
					class="form-control"
					type="password"
					name="password"
				>
			</div>
			<div>
				Individual registration is recommended. You can create team account later.
			</div>
			<div v-if="isError" class="error">
				Registration errored. Maybe username already taken?
			</div>
			<div>
				<button id="submit" type="submit" tabindex="5">
					Submit
				</button>
			</div>
			<input type="hidden" name="nonce" :value="csrfToken">
		</form>
	</section>
</template>

<script>
import IsoLink from '~/components/IsoLink.vue';
import CtftimeLoginButton from '../components/CtftimeLoginButton.vue';
import {mapState} from 'vuex';

export default {
	components: {IsoLink, CtftimeLoginButton},
	async asyncData(context) {
		await context.store.dispatch('updateCsrfToken', context);
	},
	data() {
		return {
			isError: false,
			isLegacyActive: false,
		};
	},
	head() {
		return {
			title: 'Register - TSG CTF',
		};
	},
	computed: {
		...mapState(['isLoggedIn', 'csrfToken']),
	},
	mounted() {
		if (document.referrer) {
			const referrer = new URL(document.referrer);
			if (referrer.pathname === '/register') {
				this.isError = true;
			}
		}
	},
};
</script>

<style lang="postcss">
.Register {
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

	.ctftime-login-area {
		text-align: center;
	}

	.login-form {
		opacity: 0.1;
		transition: opacity 0.3s;

		&.active {
			opacity: 1;
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

	.error {
		font-size: 1.5rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;

		color: #f44336;
		padding: 0;
		line-height: 2rem;
	}

	button[type='submit'] {
		width: 10rem;
		margin: 1rem 0;
	}
}
</style>
