<template>
	<a href="/oauth" class="CtftimeLoginButton button-style">
		<span>{{prefix}}</span><img alt="CTFTime" src="@/static/ctftime.svg">
	</a>
</template>

<script>
export default {
	props: {
		prefix: {
			required: true,
			type: String,
		},
	},
};
</script>

<style lang="postcss">
.CtftimeLoginButton {
	display: inline-block;
	width: auto;
	padding: 0 2rem;
	max-width: 35rem;
	background: linear-gradient(90deg, #3e91a6 0%, #5e0fa9 80%, #E3000B, 80.1%, #E3000B 100%);
	overflow: hidden;
	height: 4rem;
	margin: 5rem 0 1rem;

	& > * {
		vertical-align: middle;
	}

	img {
		height: 4rem;
	}
}
</style>
