<template>
	<section class="Settings">
		<h2 class="title"><span>Settings</span></h2>
		<div class="subtitle">
			User settings
		</div>
		<form
			id="user-settings-form"
			method="post"
			accept-charset="utf-8"
			autocomplete="off"
			role="form"
			@submit="onSubmitUser"
		>
			<div class="form-group">
				<label for="user-name-input">
					User Name
				</label>
				<input
					id="user-name-input"
					v-model="userForm.name"
					class="form-control"
					type="text"
					name="name"
				>
			</div>
			<div class="form-group">
				<label for="user-email-input">
					Email
				</label>
				<input
					id="user-email-input"
					v-model="userForm.email"
					class="form-control"
					type="email"
					name="email"
				>
			</div>
			<div class="form-group">
				<label for="user-confirm-input">
					Current Password
				</label>
				<input
					id="user-confirm-input"
					v-model="userForm.confirm"
					class="form-control"
					type="password"
					name="confirm"
				>
			</div>
			<div class="form-group">
				<label for="user-password-input">
					New Password
				</label>
				<input
					id="user-password-input"
					v-model="userForm.password"
					class="form-control"
					type="password"
					name="password"
				>
			</div>
			<div class="form-group">
				<label for="user-affiliation-input">
					Affiliation
				</label>
				<input
					id="user-affiliation-input"
					v-model="userForm.affiliation"
					class="form-control"
					type="text"
					name="affiliation"
				>
			</div>
			<div class="form-group">
				<label for="user-website-input">
					Website
				</label>
				<input
					id="user-website-input"
					v-model="userForm.website"
					class="form-control"
					type="url"
					name="website"
				>
			</div>
			<div class="form-group">
				<label for="user-country-input">
					Country
				</label>
				<select
					id="user-country-input"
					v-model="userForm.country"
					class="form-control"
					name="country"
				>
					<option value=""/>
					<option v-for="[code, countryName] in countries" :key="code" :value="code">
						{{countryName}}
					</option>
				</select>
			</div>

			<div class="form-group">
				<button
					v-if="!userForm.isSubmitting"
					id="user-submit"
					type="submit"
					tabindex="5"
				>
					Submit
				</button>
				<pulse-loader v-else color="white"/>
			</div>

			<div class="result">
				<span v-if="userForm.isSuccess" class="success">
					Your profile has been updated
				</span>
				<ul v-if="userForm.errors.length > 0" class="errors">
					<li v-for="error in userForm.errors" :key="error">
						{{error}}
					</li>
				</ul>
			</div>
		</form>

		<div v-if="isInTeam" class="subtitle">
			Team settings
		</div>

		<form
			v-if="isInTeam"
			id="team-settings-form"
			method="post"
			accept-charset="utf-8"
			autocomplete="off"
			role="form"
			@submit="onSubmitTeam"
		>
			<div class="form-group">
				<label for="team-name-input">
					Team Name
				</label>
				<input
					id="team-name-input"
					v-model="teamForm.name"
					class="form-control"
					type="text"
					name="name"
				>
			</div>
			<div class="form-group">
				<label for="team-confirm-input">
					Current Password
				</label>
				<input
					id="team-confirm-input"
					v-model="teamForm.confirm"
					class="form-control"
					type="password"
					name="confirm"
				>
			</div>
			<div class="form-group">
				<label for="team-password-input">
					New Password
				</label>
				<input
					id="team-password-input"
					v-model="teamForm.password"
					class="form-control"
					type="password"
					name="password"
				>
			</div>
			<div class="form-group">
				<label for="team-affiliation-input">
					Affiliation
				</label>
				<input
					id="team-affiliation-input"
					v-model="teamForm.affiliation"
					class="form-control"
					type="text"
					name="affiliation"
				>
			</div>
			<div class="form-group">
				<label for="team-website-input">
					Website
				</label>
				<input
					id="team-website-input"
					v-model="teamForm.website"
					class="form-control"
					type="url"
					name="website"
				>
			</div>
			<div class="form-group">
				<label for="team-country-input">
					Country
				</label>
				<select
					id="team-country-input"
					v-model="teamForm.country"
					class="form-control"
					name="country"
				>
					<option value=""/>
					<option v-for="[code, countryName] in countries" :key="code" :value="code">
						{{countryName}}
					</option>
				</select>
			</div>

			<div class="form-group">
				<button
					v-if="!teamForm.isSubmitting"
					id="team-submit"
					type="submit"
					tabindex="5"
				>
					Submit
				</button>
				<pulse-loader v-else color="white"/>
			</div>

			<div class="result">
				<span v-if="teamForm.isSuccess" class="success">
					Your profile has been updated
				</span>
				<ul v-if="teamForm.errors.length > 0" class="errors">
					<li v-for="error in teamForm.errors" :key="error">
						{{error}}
					</li>
				</ul>
			</div>
		</form>
	</section>
</template>

<script>
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import flatten from 'lodash/flatten';
import {mapState} from 'vuex';

export default {
	components: {PulseLoader},
	async asyncData(context) {
		await context.store.dispatch('updateCsrfToken', context);
	},
	data() {
		return {
			userForm: {
				name: '',
				email: '',
				confirm: '',
				password: '',
				affiliation: '',
				website: '',
				country: '',
				isSuccess: false,
				isSubmitting: false,
				errors: [],
			},
			teamForm: {
				name: '',
				confirm: '',
				password: '',
				affiliation: '',
				website: '',
				country: '',
				isSuccess: false,
				isSubmitting: false,
				errors: [],
			},
		};
	},
	head() {
		return {
			title: 'Settings - TSG CTF',
		};
	},
	computed: {
		...mapState(['isLoggedIn', 'isInTeam', 'csrfToken', 'user', 'team', 'countries']),
	},
	watch: {
		user(newValue) {
			Object.assign(this.userForm, newValue);
		},
		team(newValue) {
			Object.assign(this.teamForm, newValue);
		},
	},
	mounted() {
		if (!this.isLoggedIn) {
			this.$router.replace({
				path: '/login',
			});
			return;
		}

		Object.assign(this.userForm, this.user);
		Object.assign(this.teamForm, this.team);
	},
	methods: {
		async onSubmitUser(event) {
			event.preventDefault();
			const form = new FormData(event.target);

			this.userForm.isSubmitting = true;
			this.userForm.isSuccess = false;
			this.userForm.errors = [];

			const {data} = await this.$axios.patch('/api/v1/users/me', Object.fromEntries(form), {
				headers: {
					'content-type': 'application/json',
				},
				validateStatus: null,
			});
			this.userForm.isSubmitting = false;

			if (data.success) {
				this.userForm.isSuccess = true;
				await this.$store.dispatch('updateUser', {$axios: this.$axios});
			} else {
				this.userForm.errors = flatten(Object.values(data.errors));
			}
		},
		async onSubmitTeam(event) {
			event.preventDefault();
			const form = new FormData(event.target);

			this.teamForm.isSubmitting = true;
			this.teamForm.isSuccess = false;
			this.teamForm.errors = [];

			const {data} = await this.$axios.patch('/api/v1/teams/me', Object.fromEntries(form), {
				headers: {
					'content-type': 'application/json',
				},
				validateStatus: null,
			});
			this.teamForm.isSubmitting = false;

			if (data.success) {
				this.teamForm.isSuccess = true;
				await this.$store.dispatch('updateTeam', {$axios: this.$axios});
			} else {
				this.teamForm.errors = flatten(Object.values(data.errors));
			}
		},
	},
};
</script>

<style lang="postcss">
.Settings {
	text-align: center;

	.title {
		margin-bottom: 0;
	}

	.subtitle {
		font-size: 2rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;
		text-align: center;
		text-transform: uppercase;
		letter-spacing: 1px;
		margin-top: 3rem;
		margin-bottom: 1rem;
		word-break: break-word;

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
		flex: 0 0 10rem;
		width: 10rem;
		text-align: right;
		padding-right: 1rem;
	}

	.form-control {
		flex: 1 1 0;
		width: 0;
		font-size: 1.2rem;
		max-width: 20rem;
	}

	.result {
		font-size: 1.5rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;

		.success {
			color: #45d823;
		}

		.errors {
			color: #f44336;
			padding: 0;
			line-height: 2rem;
		}
	}

	button[type='submit'] {
		width: 10rem;
		margin: 1rem 0;
	}
}
</style>
