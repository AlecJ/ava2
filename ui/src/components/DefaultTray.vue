<script>
import TerritoryTray from "@/components/TerritoryTray.vue";
import UnitTray from "@/components/UnitTray.vue";
import PurchaseUnitsTray from "@/components/PurchaseUnitsTray.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";

export default {
	components: {
		TerritoryTray,
		UnitTray,
		PurchaseUnitsTray,
		LoadingSpinner,
	},
	props: {
		isLoading: {
			type: Boolean,
			required: false,
		},
		territoryData: {
			type: Object,
			required: false,
		},
		captureTerritory: {
			type: Function,
			required: true,
		},
		currentTurnNum: {
			type: Number,
			required: false,
			default: 0,
		},
		switchUnitMovementMode: {
			type: Function,
			required: true,
		},
		isMovingUnits: {
			type: Boolean,
			required: false,
			default: false,
		},
		moveUnits: {
			type: Function,
			required: true,
		},
		currentPhaseNum: {
			type: Number,
			required: false,
			default: 0,
		},
		selectedTerritoryForMovement: {
			type: String,
			required: false,
		},
		isPurchasingUnits: {
			type: Boolean,
			required: false,
			default: false,
		},
		purchaseUnit: {
			type: Function,
			required: true,
		},
	},
	data() {
		return {
			forceClose: false,
			showTerritoryData: false,
		};
	},
	watch: {
		territoryData(newVal) {
			if (newVal) {
				this.showTerritoryData = true;
			} else {
				// Delay clearing the name until after the sidebar transition ends
				setTimeout(() => {
					if (!this.territoryData) this.showTerritoryData = false;
				}, 400);
			}
		},
		isPurchasingUnits() {
			if (!this.forceClose && !!this.territoryData) {
				this.forceClose = true;

				setTimeout(() => {
					this.forceClose = false;
				}, 200);
			}
		},
	},
	computed: {
		showFullScreen() {
			return this.isPurchasingUnits;
		},
		showHalfScreen() {
			return !!this.territoryData && !this.isPurchasingUnits;
		},
	},
	methods: {},
};
</script>

<template>
	<div
		:class="[
			'right-side-bar',
			{ 'force-close': forceClose },
			{ 'show-full-screen': showFullScreen },
			{ 'show-territory-screen': showHalfScreen },
		]"
		@mousedown.prevent.stop
	>
		<TerritoryTray
			v-show="showTerritoryData && !showFullScreen && !forceClose"
			:isLoading="isLoading"
			:territoryData="territoryData"
			:captureTerritory="captureTerritory"
			:currentTurnNum="currentTurnNum"
			:currentPhaseNum="currentPhaseNum"
			:switchUnitMovementMode="switchUnitMovementMode"
			:isMovingUnits="isMovingUnits"
			:moveUnits="moveUnits"
			:selectedTerritoryForMovement="selectedTerritoryForMovement"
			:isPurchasingUnits="isPurchasingUnits"
		/>

		<PurchaseUnitsTray
			v-if="showFullScreen && !forceClose"
			:purchaseUnit="purchaseUnit"
		/>
	</div>
</template>

<style scoped lang="scss">
.right-side-bar {
	position: fixed;
	top: 12.5%;
	right: 0;
	overflow: hidden;
	z-index: 1;

	width: 80%;
	min-width: 250px;
	height: 75%;
	padding: 1rem;

	background-color: rgba(33, 32, 32, 0.931);
	border: 2px solid white;
	border-radius: 2rem 0 0 2rem;
	border-right: 0;

	transform: translateX(calc(100% - 2rem));
	transition: transform 0.4s ease-in-out;

	color: white;

	&.force-close {
		transform: translateX(calc(100% - 2rem));
		transition: transform 0.2s ease-in-out;
	}

	&.show-full-screen:not(.force-close) {
		transform: translateX(0%);
	}

	&.show-territory-screen:not(.force-close) {
		transform: translateX(60%);
	}
}
</style>
