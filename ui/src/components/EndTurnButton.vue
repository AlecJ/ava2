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
		hasUnresolvedBattles: {
			type: Boolean,
			required: false,
			default: false,
		},
		hasMobilizeUnitsRemaining: {
			type: Boolean,
			required: false,
			default: false,
		},
		isThisPlayersTurn: {
			type: Boolean,
			required: false,
			default: false,
		},
	},
	computed: {
		canEndPurchaseUnitPhase() {
			return (
				this.isThisPlayersTurn &&
				this.currentPhaseNum === 0 &&
				!this.hasUnresolvedBattles
			);
		},
		canEndCombatMovementPhase() {
			return this.isThisPlayersTurn && this.currentPhaseNum === 1;
		},
		canEndCombatPhase() {
			return (
				this.isThisPlayersTurn &&
				this.currentPhaseNum === 2 &&
				!this.hasUnresolvedBattles
			);
		},
		canEndNonCombatMovementPhase() {
			return this.isThisPlayersTurn && this.currentPhaseNum === 3;
		},
		canEndTurn() {
			return (
				this.isThisPlayersTurn &&
				this.currentPhaseNum === 4 &&
				!this.hasMobilizeUnitsRemaining
			);
		},
	},
};
</script>

<template>
	<button
		v-if="currentPhaseNum === 0"
		@click="endPhase"
		:disabled="!canEndPurchaseUnitPhase"
	>
		End Purchase Unit Phase
	</button>
	<button
		v-else-if="currentPhaseNum === 1"
		@click="endPhase"
		:disabled="!canEndCombatMovementPhase"
	>
		End Combat Move Phase
	</button>
	<button
		v-else-if="currentPhaseNum === 2"
		@click="endPhase"
		:disabled="!canEndCombatPhase"
	>
		End Combat Phase
	</button>
	<button
		v-else-if="currentPhaseNum === 3"
		@click="endPhase"
		:disabled="!canEndNonCombatMovementPhase"
	>
		End Noncombat Move Phase
	</button>
	<button
		v-else-if="currentPhaseNum === 4"
		@click="endTurn"
		:disabled="!canEndTurn"
	>
		End Turn
	</button>
	<!-- <button v-else @click="nextPhase" disabled>
		Waiting for other players...
	</button> -->
</template>

<style scoped lang="scss">
button {
	position: absolute;
	bottom: 1.5rem;
	// width: 20%;
	width: calc(2rem + 16rem);
	height: 3rem;
	margin-left: 0;

	background-color: rgba(33, 32, 32, 0.931);
	border: 2px solid white;
	border-radius: 0 2rem 2rem 0;
	border-left: 0;

	left: -2rem;
	transition: left 0.3s ease;

	&:hover:not(:disabled) {
		left: 0%;
	}

	&:disabled {
		color: #4a4a4a;
	}
}
</style>
