<template>
	<a v-if="isStatic" :href="to">
		<slot/>
	</a>
	<nuxt-link v-else :to="to">
		<slot/>
	</nuxt-link>
</template>

<script>
import {mapState} from 'vuex';

export default {
	props: {
		to: {
			required: true,
			type: String,
		},
	},
	computed: {
		...mapState(['isStatic']),
	},
};
</script>
