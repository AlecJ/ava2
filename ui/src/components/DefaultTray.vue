<script>
import TerritoryTray from "@/components/TerritoryTray.vue";
import PurchaseUnitsTray from "@/components/PurchaseUnitsTray.vue";
import CombatTray from "@/components/CombatTray.vue";
import PlaceMobilizationUnitsTray from "@/components/PlaceMobilizationUnitsTray.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";

export default {
	components: {
		TerritoryTray,
		PurchaseUnitsTray,
		CombatTray,
		PlaceMobilizationUnitsTray,
		LoadingSpinner,
	},
	props: {
		isLoading: {
			type: Boolean,
			required: false,
		},
		player: {
			type: Object,
			required: false,
		},
		territoryData: {
			type: Object,
			required: false,
		},
		neighboringTerritoriesData: {
			type: Object,
			required: false,
		},
		currentTurnNum: {
			type: Number,
			required: false,
			default: 0,
		},
		currentPhaseNum: {
			type: Number,
			required: false,
			default: 0,
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
		showBattles: {
			type: Boolean,
			required: false,
			default: false,
		},
		isPlacingMobilizationUnits: {
			type: Boolean,
			required: false,
			default: false,
		},
		setIsSelectingTerritory: {
			type: Function,
			required: true,
		},
		selectedTerritory: {
			type: String,
			required: false,
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
			return this.isPurchasingUnits || this.showBattles;
		},
		showHalfScreen() {
			return (
				!this.showFullScreen &&
				(!!this.territoryData || this.isPlacingMobilizationUnits)
			);
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
			v-show="
				showTerritoryData &&
				!isPurchasingUnits &&
				!isPlacingMobilizationUnits &&
				!forceClose
			"
			:isLoading="isLoading"
			:player="player"
			:territoryData="territoryData"
			:neighboringTerritoriesData="neighboringTerritoriesData"
			:currentTurnNum="currentTurnNum"
			:currentPhaseNum="currentPhaseNum"
			:setIsSelectingTerritory="setIsSelectingTerritory"
			:selectedTerritory="selectedTerritory"
		/>

		<PurchaseUnitsTray
			v-if="isPurchasingUnits && !forceClose"
			:purchaseUnit="purchaseUnit"
		/>

		<CombatTray v-if="showBattles && !forceClose" />

		<PlaceMobilizationUnitsTray
			v-if="isPlacingMobilizationUnits && !forceClose"
			:player="player"
			:setIsSelectingTerritory="setIsSelectingTerritory"
			:selectedTerritory="selectedTerritory"
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
		transform: translateX(calc(100% - 26rem));
	}
}
</style>
