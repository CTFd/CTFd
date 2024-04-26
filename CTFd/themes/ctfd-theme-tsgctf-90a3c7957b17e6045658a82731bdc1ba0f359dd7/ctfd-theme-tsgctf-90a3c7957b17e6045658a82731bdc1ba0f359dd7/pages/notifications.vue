<template>
	<section class="Notifications">
		<h2 class="title"><span>Notifications</span></h2>
		<div v-if="!isPushEnabled" class="enable-notifications-area">
			<div class="enable-notifications" @click="enableNotifications">
				<bell-ring/> <span>Enable Push Notification</span>
			</div>
		</div>
		<div class="lang-switcher">
			<span class="lang" :class="{active: language === 'ja'}" @click="$store.commit('setLanguage', 'ja')">
				<img src="https://hatscripts.github.io/circle-flags/flags/jp.svg" width="15">
				<span class="lang-name">JA</span>
			</span> /
			<span class="lang" :class="{active: language === 'en'}" @click="$store.commit('setLanguage', 'en')">
				<img src="https://hatscripts.github.io/circle-flags/flags/gb.svg" width="15">
				<span class="lang-name">EN</span>
			</span>
		</div>
		<div v-for="notification, i in notifications" :key="notification.id" class="notification">
			<hr v-if="i !== 0">
			<div class="title">{{notification.title}}</div>
			<div class="date">
				<iso-timeago :datetime="notification.date" :auto-update="60"/>
			</div>
			<div class="content">{{getContent(notification)}}</div>
		</div>
		<div v-if="notifications.length === 0" class="no-notification">
			No notifications yet!
		</div>
	</section>
</template>

<script>
import IsoTimeago from '~/components/IsoTimeago.vue';
import {mapGetters, mapState} from 'vuex';
import BellRing from 'vue-material-design-icons/BellRing.vue';

export default {
	components: {IsoTimeago, BellRing},
	async asyncData(context) {
		await context.store.dispatch('notifications/updateNotifications', context);
	},
	head() {
		return {
			title: 'Notifications - TSG CTF',
		};
	},
	computed: {
		...mapGetters({
			notifications: 'notifications/getNotifications',
		}),
		...mapState(['language', 'isPushEnabled']),
	},
	methods: {
		getContent(notification) {
			const sections = notification.content.split(/^---$/m);
			if (sections.length < 2 || this.language !== 'ja') {
				return sections[0].trim();
			}
			return sections[1].trim();
		},
		async enableNotifications() {
			await this.$OneSignal.showNativePrompt();
			this.$store.commit('setIsPushEnabled', true);
		},
	},
};
</script>

<style lang="postcss">
.Notifications {
	.lang-switcher {
		text-align: center;
		margin-bottom: 5rem;
		font-size: 1.5rem;

		.lang {
			display: inline-block;
			cursor: pointer;

			&.active {
				border-bottom: 1.5px white solid;
			}
		}

		img, .lang-name {
			vertical-align: middle;
		}
	}

	.enable-notifications-area {
		text-align: center;
	}

	.enable-notifications {
		display: inline-block;
		width: auto;
		cursor: pointer;
		background-color: #e54b4d;
		padding: 0.2rem 2rem;
		margin-bottom: 1rem;
		border-radius: 9999px;

		& > * {
			vertical-align: middle;
		}
	}

	.notification {
		width: 100%;
		max-width: 50rem;
		position: relative;
		color: white;
		margin: 1rem auto;
		box-sizing: border-box;
		border-radius: 3px;

		.title {
			font-family: 'Fredoka One', cursive;
			font-weight: 300;
			font-size: 2rem;
			text-align: center;
			text-transform: uppercase;
			letter-spacing: 1px;
			margin-top: 3rem;
			word-break: break-word;
			text-align: center;
		}

		.date {
			text-align: center;
			font-size: 1rem;
			margin-bottom: 1rem;
		}

		.content {
			white-space: pre-line;
			font-size: 1.5rem;
			font-family: 'Roboto';
			text-align: justify;
		}
	}

	.no-notification {
		text-align: center;
		font-size: 2.5rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;
		padding: 0;
		line-height: 2rem;
	}
}
</style>
