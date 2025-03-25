<script>
export default {
	props: {
		active: {
			type: Boolean,
			required: false,
			default: false,
		},
		setPurchasingUnits: {
			type: Function,
			required: true,
		},
	},
};
</script>

<template>
	<button
		:disabled="!active"
		@click="
			() => {
				setPurchasingUnits(true);
			}
		"
	>
		Purchase Units
	</button>
</template>

<style scoped lang="scss">
button {
	position: absolute;
	top: 37.5%;
	width: calc(2rem + 15%);
	height: 3rem;
	left: -2rem;
	margin-left: 0;

	background-color: rgba(33, 32, 32, 0.931);
	border: 2px solid white;
	border-radius: 0 2rem 2rem 0;
	border-left: 0;

	transition: left 0.3s ease;

	&:hover:not(:disabled) {
		left: 0%;
	}
}
</style>
