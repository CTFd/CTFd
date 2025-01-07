<template>
	<time
		v-if="isStatic"
		:class="klass"
		:datetime="datetime"
	>
		{{dateText}}
	</time>
	<timeago
		v-else
		:class="klass"
		:datetime="datetime"
		:auto-update="autoUpdate"
	/>
</template>

<script>
import {mapState} from 'vuex';

export default {
	props: {
		klass: {
			required: false,
			default: '',
			type: String,
		},
		datetime: {
			required: true,
			type: Date,
		},
		autoUpdate: {
			required: true,
			type: Number,
		},
	},
	computed: {
		...mapState(['isStatic']),
		date() {
			return new Date(this.datetime);
		},
		dateText() {
			const month = (this.date.getUTCMonth() + 1).toString().padStart(2, '0');
			const date = this.date.getUTCDate().toString().padStart(2, '0');
			const hour = this.date.getUTCHours().toString().padStart(2, '0');
			const minute = this.date.getUTCMinutes().toString().padStart(2, '0');
			const second = this.date.getUTCSeconds().toString().padStart(2, '0');
			return `${month}/${date} ${hour}:${minute}:${second}`;
		},
	},
};
</script>
