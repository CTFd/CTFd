<template>
	<div class="Challenge">
		<div class="list-marker">
			<div class="checkbox" :class="{solved: challenge.solved_by_me}"/>
		</div>
		<div class="list-content">
			<div class="title" @click="onClickTitle">
				<span class="title-name">{{challenge.name}}</span>
				<span class="points"> {{challenge.value}}pts </span>
			</div>
			<div class="subtitle">
				{{challenge.solves}} solves -
				<span
					v-for="tag in tags"
					:key="tag"
					class="tag"
					:class="[tag]"
				>
					{{tag}}
				</span>
			</div>
			<marquee v-if="isOpen && isSolvesOpen" class="solves">
				<span v-if="challenge.solveInfos === undefined">Loading...</span>
				<span v-else>
					<span v-for="j in 100" :key="j">
						<span v-for="solve, i in challenge.solveInfos" :key="solve.account_id">
							{{formatOrdinals(i + 1)}}:
							<iso-link :to="`/teams/${solve.account_id}`">{{solve.name}}</iso-link>
							<liquid-spot v-if="i === 0" class="first-blood" name="first blood"/>
						</span>
						<span :style="{display: 'inline-block', width: '3rem'}"/>
					</span>
				</span>
			</marquee>
			<div v-if="isOpen" class="content" :class="{'is-solves-open': isSolvesOpen}">
				<div v-if="challenge.details" class="details">
					<div
						class="solve-count"
						:class="{
							'someone-solved': challenge.solves > 0,
							'is-solves-open': isSolvesOpen,
							solved: challenge.solved_by_me,
						}"
						@click="toggleSolves"
					>
						{{getSolvesText(challenge.details.solves)}}
					</div>
					<div class="description-header">
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
						<div v-if="author" class="author">
							<span class="author-name">Author: {{author}}</span>
						</div>
					</div>
					<div class="description">
						<!-- eslint-disable vue/no-v-html -->
						<div
							ref="description"
							class="description-column"
							v-html="$md.render(getDescription())"
						/>
						<!-- eslint-enable vue/no-v-html -->
					</div>
					<div class="attachments">
						<a
							v-for="file in challenge.details.files"
							:key="file"
							class="attachment"
							:href="getFileLink(file)"
							target="_blank"
							rel="noopener noreferrer"
						>
							{{getFileName(file)}}
						</a>
					</div>
				</div>
				<div v-else class="description-loading">
					<pulse-loader color="white"/>
				</div>
				<form class="flag-form" @submit="onSubmitFlag">
					<input
						v-model="flagText"
						type="text"
						name="flag"
						class="flag-input"
						autocomplete="off"
						autocorrect="off"
						autocapitalize="off"
						spellcheck="false"
						:class="{yay, boo}"
						:readonly="yay"
						:placeholder="getPlaceholderText(challenge)"
						:disabled="challenge.solved_by_me || isEnded"
					>
					<button type="submit" class="flag-submit" :disabled="yay || challenge.solved_by_me || isEnded">Send</button>
				</form>
			</div>
		</div>
	</div>
</template>

<script>
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import {mapState} from 'vuex';
import IsoLink from '~/components/IsoLink.vue';
import LiquidSpot from 'vue-material-design-icons/LiquidSpot.vue';

export default {
	components: {PulseLoader, IsoLink, LiquidSpot},
	props: {
		challenge: {
			required: true,
			type: Object,
		},
	},
	data() {
		return {
			isOpen: false,
			yay: false,
			boo: false,
			flagText: '',
			isSolvesOpen: false,
		};
	},
	computed: {
		...mapState(['isEnded', 'isStatic', 'language']),
		tags() {
			return this.challenge.tags.map((tag) => tag.value).filter((tag) => !tag.match(/author:/i));
		},
		author() {
			const authorTag = this.challenge.tags.find((tag) => tag.value.match(/author:/i));
			if (!authorTag) {
				return undefined;
			}
			return authorTag.value.split(':')[1].trim();
		},
	},
	mounted() {
		if (!this.isStatic) {
			this.interval = setInterval(this.updateImgSrc, 60 * 1000);
		}
	},
	destroyed() {
		clearInterval(this.interval);
	},
	methods: {
		onClickTitle() {
			if (this.isOpen) {
				this.isOpen = false;
			} else {
				if (!this.isStatic) {
					this.$store.dispatch('challenges/getDetail', {$axios: this.$axios, id: this.challenge.id});
				}
				this.isOpen = true;
			}
		},
		// https://stackoverflow.com/a/13627586/2864502
		formatOrdinals(i) {
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
		},
		getFileName(path) {
			const components = new URL(path, location.href).pathname.split('/');
			return components[components.length - 1];
		},
		getFileLink(path) {
			if (!this.isStatic) {
				return path;
			}

			const components = new URL(path, location.href).pathname.split('/');
			const fileName = components[components.length - 1];
			const challengeId = components[components.length - 2];
			return `https://tsgctf-ctfd-storage.storage.googleapis.com/tsgctf-ctfd-storage/${challengeId}/${fileName}`;
		},
		getSolvesText(solves) {
			return `${solves} ${solves === 1 ? 'solve' : 'solves'}`;
		},
		getPlaceholderText(challenge) {
			if (challenge.solved_by_me) {
				return 'You already solved this challenge!';
			}

			if (this.isEnded) {
				return 'Contest has been ended';
			}

			return 'TSGCTF{......}';
		},
		toggleSolves() {
			if (this.isSolvesOpen) {
				this.isSolvesOpen = false;
				return;
			}
			if (!this.isStatic) {
				this.$store.dispatch('challenges/getSolveInfos', {$axios: this.$axios, id: this.challenge.id});
			}
			this.isSolvesOpen = true;
		},
		getDescription() {
			const descriptions = this.challenge.details.description.split(/^---$/m);
			if (descriptions.length >= 2 && this.language === 'ja') {
				return descriptions[1];
			}
			return descriptions[0];
		},
		async onSubmitFlag(event) {
			event.preventDefault();
			this.boo = false;
			const form = new FormData(event.target);
			const inputFlag = form.get('flag');
			const {data} = await this.$axios.post(
				'/api/v1/challenges/attempt',
				{
					challenge_id: parseInt(this.challenge.id),
					submission: inputFlag,
				},
				{
					headers: {
						'content-type': 'application/json',
					},
				},
			);
			if (data.data.status === 'correct') {
				this.yay = true;
				this.flagText = 'Brilliant!';
				await this.$store.dispatch('challenges/updateChallenges', {$axios: this.$axios});
			} else {
				this.boo = true;
			}
		},
		updateImgSrc() {
			if (this.$refs.description) {
				const imgs = Array.from(this.$refs.description.querySelectorAll('img'));
				const timestamp = Date.now();
				for (const img of imgs) {
					const srcUrl = new URL(img.src);
					srcUrl.searchParams.set('ts', timestamp.toString());
					img.src = srcUrl.toString();
				}
			}
		},
	},
};
</script>

<style lang="postcss">
.Challenge {
	margin-bottom: 10px;
	display: flex;
	text-align: left;

	.list-marker {
		flex: 0 0 48px;
		position: relative;

		.checkbox {
			width: 42px;
			height: 42px;
			position: absolute;
			top: 3px;
			left: 0;
			background: url('../static/checkbox_off.svg');
			background-size: cover;
			opacity: 0.8;

			&.solved {
				background: url('../static/checkbox_on.svg');
			}
		}
	}

	.list-content {
		width: 100%;
	}

	&:not(:last-child) .list-marker::before {
		content: '';
		position: absolute;
		background: rgba(255, 255, 255, 0.5);
		top: 46px;
		left: 20px;
		bottom: -10px;
		width: 3px;
		border-radius: 3px;
	}

	.title {
		font-size: 2.5rem;
		font-family: 'Fredoka One', cursive;
		font-weight: 300;
		display: inline-block;
		letter-spacing: 1px;
		cursor: pointer;
	}

	.title-name {
		color: rgb(82, 186, 255);
		-webkit-text-fill-color: transparent;
		background: linear-gradient(90deg, rgb(71 229 67) 0%, rgb(252 255 68) 100%);
		background-clip: text;
	}

	.points {
		background: rgba(255, 255, 255, 0.6);
		display: inline-block;
		color: #0d030e;
		-webkit-text-fill-color: #0d030e;
		font-size: 1.2rem;
		margin-left: 0.2rem;
		padding: 0.1rem 0.3rem;
		vertical-align: middle;
		letter-spacing: 0;
		border-radius: 3px;
	}

	.subtitle {
		line-height: 2rem;
	}

	.tag {
		margin: 0 0.3rem;
		padding: 0.2rem 0.8rem;
		background: rgba(255, 255, 255, 0.5);
		color: #333;
		border-radius: 10rem;
		font-weight: bold;
		font-size: 0.8rem;

		&.beginner {
			background: rgb(82, 186, 255);
		}

		&.broken {
			background: rgb(255, 82, 82);
		}
	}

	.content {
		margin-top: 1rem;
		margin-left: 0.5rem;
		margin-bottom: 1.5rem;
		background: rgba(255, 255, 255, 0.2);
		padding: 1rem;
		width: auto;
		box-sizing: border-box;
		border-radius: 1rem;
		position: relative;
		border-top-right-radius: 0;

		&.is-solves-open {
			margin-top: 0;
			border-top-left-radius: 0;
		}
	}

	.solve-count {
		background: #2f2f44;
		position: absolute;
		bottom: 100%;
		right: 0;
		padding: 0 0.3rem;
		border-radius: 5px;
		border-bottom-right-radius: 0;
		border-bottom-left-radius: 0;
		cursor: pointer;

		&.someone-solved {
			background: #ff5722;
		}

		&.solved {
			background: #4caf50;
		}

		&.is-solves-open {
			bottom: calc(100% + 2rem);
		}
	}

	.solves {
		display: block;
		height: 2rem;
		line-height: 2rem;
		padding: 0 0.5rem;
		margin-top: 1rem;
		margin-left: 0.5rem;
		border-top-left-radius: 1rem;

		text-align: right;
		background: #272b24;

		overflow: hidden;

		.first-blood {
			color: red;
			vertical-align: text-top;
		}

		a {
			color: #03a9f4;
		}
	}

	.description-header {
		display: flex;
		justify-content: space-between;
	}

	.author {
		display: block;
	}

	.lang-switcher {
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

	.description {
		font-size: 1.2rem;
		margin-bottom: 1rem;
		font-family: Roboto, sans-serif;
		letter-spacing: 0.05em;
		display: flex;
		line-height: 1.6em;

		.description-column {
			flex: 1 0 0;
			padding: 0 0.5rem;

			&:nth-child(2) p {
				font-weight: normal;
				letter-spacing: 0;
			}
		}

		strong {
			color: #ffeb3b;
		}

		p {
			margin: 0.5rem 0;
			font-weight: bold;
		}

		a {
			color: #03a9f4;
		}

		code {
			background: #333;
			padding: 0.1rem 0.5rem;
			font-weight: normal;
		}

		pre {
			background: #333;
			padding: 0.5rem;
			white-space: pre-line;
			word-break: break-all;

			code {
				background: transparent;
				padding: 0;
			}
		}

		hr {
			opacity: 0.4;
			margin: 1.5rem 1rem;
		}

		img {
			max-width: 100%;
		}
	}

	.attachments {
		display: flex;
		flex-wrap: wrap;
	}

	.attachment {
		min-width: 15rem;
		margin: 0.5rem;
		height: 3rem;
		line-height: 3rem;
		background: #222;
		border-radius: 3px;
		text-align: center;
		padding: 0 1rem;

		&::before {
			content: '';
			background: url('https://cdn.jsdelivr.net/gh/google/material-design-icons@2.2.0/file/2x_web/ic_attachment_white_18dp.png');
			background-size: cover;
			display: inline-block;
			width: 1.4rem;
			height: 1.4rem;
			vertical-align: middle;
		}
	}

	.description-loading {
		height: 6rem;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.flag-form {
		display: flex;
		margin-top: 1rem;
	}

	.flag-input {
		flex: 1 1 0;
		width: 0;
		height: 2.5rem;
		border-radius: 9999px;
		margin-right: 0.5rem;
		padding: 0 1rem;
		font-family: 'Roboto', sans-serif;
		font-size: 1.4rem;
		background: #ddd;
		color: #333;

		&[disabled] {
			background: #aaa;
			color: black;
		}

		&.yay {
			background: linear-gradient(
				-45deg,
				#ee7752,
				#e73c7e,
				#23a6d5,
				#23d5ab,
				#ee7752,
				#e73c7e,
				#23a6d5,
				#23d5ab,
				#ee7752,
				#e73c7e,
				#23a6d5,
				#23d5ab,
				#ee7752,
				#e73c7e,
				#23a6d5,
				#23d5ab,
				#ee7752,
				#e73c7e,
				#23a6d5,
				#23d5ab
			);
			background-size: 1000% 1000%;
			animation: Gradient 3s ease-out 1 both;
			color: white;
			font-size: 2rem;
			font-family: 'Fredoka One', cursive;
			font-weight: 300;

			@keyframes Gradient {
				0% {
					background-position: 0% 50%;
				}
				100% {
					background-position: 100% 50%;
				}
			}
		}

		&.boo {
			animation-name: shake;
			animation-duration: 0.7s, 0.35s;
			animation-iteration-count: 1, 2;
		}

		@keyframes shake {
			0%,
			20%,
			40%,
			60%,
			80% {
				transform: translateX(8px);
			}
			50% {
				color: indianred;
			}
			10%,
			30%,
			50%,
			70%,
			90% {
				transform: translateX(-8px);
			}
		}
	}

	.flag-submit {
		flex: 0 0 6rem;

		&[disabled] {
			cursor: default;
			background: #888;
		}
	}
}
</style>
