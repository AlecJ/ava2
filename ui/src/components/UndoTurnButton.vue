<script>
import { useWorldStore } from "@/stores/world";

export default {
	props: {
		active: {
			type: Boolean,
			required: false,
			default: false,
		},
		currentPhaseNum: {
			type: Number,
			required: false,
			default: 0,
		},
		isThisPlayersTurn: {
			type: Boolean,
			required: false,
			default: false,
		},
	},
	data() {
		return {
			worldStore: null,
		};
	},
	created() {
		this.worldStore = useWorldStore();
	},
};
</script>

<template>
	<button
		:disabled="
			!isThisPlayersTurn ||
			(currentPhaseNum !== 1 && currentPhaseNum !== 3)
		"
		@mousedown.prevent.stop
		@click="worldStore.undoPhase"
	>
		Undo Phase
	</button>
</template>

<style scoped lang="scss">
button {
	position: absolute;
	bottom: 5.5rem;
	width: calc(2rem + 10rem);
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

	&:disabled {
		color: #4a4a4a;
	}
}
</style>
