<script>
export default {
	props: {
		endPhase: {
			type: Function,
			required: true,
		},
		endTurn: {
			type: Function,
			required: true,
		},
		currentPhaseNum: {
			type: Number,
			required: false,
			default: 0,
		},
	},
};
</script>

<template>
	<button v-if="currentPhaseNum === 0" @click="endPhase">
		End Purchase Unit Phase
	</button>
	<button v-else-if="currentPhaseNum === 1" @click="endPhase">
		End Combat Move Phase
	</button>
	<button v-else-if="currentPhaseNum === 2" @click="endPhase">
		End Combat Phase
	</button>
	<button v-else-if="currentPhaseNum === 3" @click="endPhase">
		End Noncombat Move Phase
	</button>
	<button v-else-if="currentPhaseNum === 4" @click="endTurn">End Turn</button>
	<!-- <button v-else @click="nextPhase" disabled>
		Waiting for other players...
	</button> -->
</template>

<style scoped lang="scss">
button {
	position: absolute;
	bottom: 1.5rem;
	width: 15%;
	height: 3rem;
}
</style>
