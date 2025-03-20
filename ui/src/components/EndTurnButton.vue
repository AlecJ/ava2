<script>
export default {
	props: {
		endTurn: {
			type: Function,
			required: true,
		},
		nextPhase: {
			type: Function,
			required: true,
		},
		currentPhase: {
			type: Number,
			required: false,
			default: 0,
		},
	},
};
</script>

<template>
	<button @click="endTurn">End Turn</button>
	<!-- <button v-if="currentPhase === 0" @click="nextPhase">
		End Purchase Unit Phase
	</button>
	<button v-else-if="currentPhase === 1" @click="nextPhase">
		End Combat Move Phase
	</button>
	<button v-else-if="currentPhase === 2" @click="nextPhase">
		End Combat Phase
	</button>
	<button v-else-if="currentPhase === 3" @click="nextPhase">
		End Noncombat Move Phase
	</button>
	<button v-else-if="currentPhase === 4" @click="nextPhase">
		End Mobilize Phase
	</button>
	<button v-else @click="nextPhase" disabled>
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
