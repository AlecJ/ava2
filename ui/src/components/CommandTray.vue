<script>
import { countries } from "@/data/countries";
import UnitTray from "@/components/UnitTray.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";

export default {
	components: {
		UnitTray,
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
		currentPhase: {
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
	},
	data() {
		return {
			territoryName: null,
			teamName: null,
			power: 0,
			units: [],
			isSelectingTerritory: false,
		};
	},
	watch: {
		territoryData(newVal) {
			if (newVal) {
				// Show the name immediately when a country is selected
				this.territoryName = newVal.name;
				this.teamName = this.getCountryName();
				this.power = newVal.power;
				this.units = newVal.units;
				this.units.sort((a, b) => a.movement - b.movement);
			} else {
				// Delay clearing the name until after the sidebar transition ends
				setTimeout(() => {
					this.resetData();
				}, 300);
			}
		},
	},
	computed: {
		countryFlagSrc() {
			const country = countries.find((c) => c.name === this.teamName);

			return country ? country.flagIcon : "";
		},
	},
	methods: {
		resetData() {
			this.territoryName = null;
			this.teamName = null;
			this.power = 0;
			this.units = [];
		},
		getCountryName() {
			if (!this.territoryData) return null;

			return countries[this.territoryData?.team].name;
		},
		toggleUnit(unit, index) {
			// once you find the index of the first movement, just use index
			const movementIndex = this.units.findIndex(
				(u) => u.movement === unit.movement
			);

			// this sets the unit to `selected` if it is not already
			this.units[movementIndex + index].selected = !this.units[
				movementIndex + index
			].selected
				? true
				: false;
		},
		confirmUnitSelection() {
			const selectedUnits = this.units.filter((unit) => unit.selected);
			this.moveUnits(selectedUnits);

			this.switchUnitMovementMode(false);

			// need to reset or update territories
			this.isSelectingTerritory = false;

			// select new territory, move camera
		},
	},
};
</script>

<template>
	<div
		:class="['right-side-bar', { active: !!territoryData }]"
		@mousedown.prevent.stop
	>
		<div class="territory-name">{{ territoryName }}</div>
		<div class="territory-info-row">
			<div class="controlling-country">
				<div class="left">Occupied by:</div>
				<div class="right">
					<img
						:src="countryFlagSrc"
						:alt="teamName"
						class="flag-icon"
					/>
				</div>
			</div>
			<div class="territory-power">
				<div class="left">Production Score:</div>
				<div class="right">{{ power }}</div>
			</div>
		</div>

		<div class="command-tray-content">
			<LoadingSpinner v-if="isLoading" />

			<UnitTray
				v-if="!isLoading"
				:isMovingUnits="isMovingUnits"
				:playerTurn="currentTurnNum % 5"
				:units="units"
				:toggleUnit="toggleUnit"
			/>

			<div v-if="!isLoading && isMovingUnits">
				<p>Select a Territory</p>
				<p>
					You have selected:
					{{
						selectedTerritoryForMovement
							? selectedTerritoryForMovement
							: "No territory selected."
					}}
				</p>
			</div>
		</div>

		<div class="command-tray-buttons">
			<button
				:disabled="!isMovingUnits"
				@click="() => switchUnitMovementMode(false)"
			>
				Back
			</button>

			<button
				v-if="!isMovingUnits"
				@click="switchUnitMovementMode(true)"
				class="move-units-button"
			>
				Move Units
			</button>

			<button
				v-if="isMovingUnits"
				:disabled="!selectedTerritoryForMovement"
				@click="confirmUnitSelection"
			>
				Confirm Unit Movement
			</button>
		</div>
	</div>
</template>

<style scoped lang="scss">
.right-side-bar {
	position: fixed;
	top: 12.5%;
	right: 0;
	overflow: hidden;
	z-index: 1;

	width: 30%;
	min-width: 250px;
	max-width: 600px;
	height: 75%;
	padding: 1rem;

	background-color: rgba(33, 32, 32, 0.931);
	border: 2px solid white;
	border-radius: 2rem 0 0 2rem;
	border-right: 0;

	display: grid;
	grid-template-rows: 1fr 1fr 5fr 1fr;
	place-items: center;
	pointer-events: auto;

	transform: translateX(90%);
	transition: transform 0.3s ease-in-out;

	color: white;

	&.active {
		transform: translateX(0%);
	}

	.territory-name {
		font-size: clamp(1rem, 2vw, 2rem);
	}

	.territory-info-row {
		width: 100%;
		display: grid;
		grid-template-columns: 1fr 1fr;

		.controlling-country,
		.territory-power {
			width: 100%;
			padding: 1rem;
			display: grid;
			grid-template-columns: 1fr 1fr;

			align-content: center;
			justify-items: center;

			.left,
			.right {
				text-align: right;
				align-self: center;
			}
		}

		.controlling-country {
			border-right: 1px solid white;

			.flag-icon {
				width: 3rem;
			}
		}
	}

	.command-tray-content {
		width: 100%;
		height: 100%;
		display: grid;
		place-items: center;
		overflow-y: auto;
	}
}
</style>
