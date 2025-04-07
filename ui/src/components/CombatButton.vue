<script>
export default {
	props: {
		active: {
			type: Boolean,
			required: false,
			default: false,
		},
		setShowBattles: {
			type: Function,
			required: true,
		},
		showBattles: {
			type: Boolean,
			required: false,
			default: false,
		},
	},
};
</script>

<template>
	<button
		:disabled="!active"
		@mousedown.prevent.stop
		@click="setShowBattles(!showBattles)"
	>
		View Battles
	</button>
</template>

<style scoped lang="scss">
button {
	position: relative;
	width: calc(2rem + 10rem);
	height: 3rem;
	left: 0;
	margin: 0;

	background-color: rgba(33, 32, 32, 0.931);
	border: 2px solid white;
	border-radius: 0 2rem 2rem 0;
	border-left: 0;

	transition: left 0.3s ease;

	&:hover:not(:disabled) {
		left: 2rem;
	}

	&:disabled {
		color: #4a4a4a;
	}
}
</style>
