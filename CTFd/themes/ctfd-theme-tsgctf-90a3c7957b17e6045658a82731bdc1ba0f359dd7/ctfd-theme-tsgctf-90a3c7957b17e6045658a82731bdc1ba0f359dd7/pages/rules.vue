<template>
	<section class="Rules">
		<h2 class="title"><span>Rules</span></h2>
		<!-- eslint-disable vue/no-v-html -->
		<div
			class="description"
			v-html="$md.render(rules)"
		/>
		<!-- eslint-enable vue/no-v-html -->
	</section>
</template>

<script>
import {mapState} from 'vuex';

export default {
	async asyncData(context) {
		await context.store.dispatch('updateRules', context);
	},
	head() {
		return {
			title: 'Rules - TSG CTF',
		};
	},
	computed: {
		...mapState(['rules']),
	},
};
</script>

<style lang="postcss">
.Rules {
	h1, h2, h3 {
		font-family: 'Fredoka One', cursive;
		font-weight: 300;
		text-align: center;
		text-transform: uppercase;
		letter-spacing: 1px;
		margin-top: 3rem;
		margin-bottom: 1rem;
		word-break: break-word;
	}

	h1 {
		font-size: 2rem;
	}

	h2 {
		font-size: 1.5rem;
	}

	h3 {
		font-size: 1rem;
	}

	strong {
		color: #ffeb3b;
	}

	p,
	ul,
	ol {
		font-family: 'Roboto';
		width: 100%;
		max-width: 50rem;
		margin: 0 auto;
		font-size: 1.4rem;
		line-height: 2rem;
	}
}
</style>
