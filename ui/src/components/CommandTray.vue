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
		playerTurn: {
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
	},
	data() {
		return {
			territoryName: null,
			teamName: null,
			power: 0,
			units: [],
			selectedUnits: {},
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
			} else {
				// Delay clearing the name until after the sidebar transition ends
				setTimeout(() => {
					this.resetData();
				}, 300);
			}
		},
	},
	computed: {
		playerUnits() {
			return this.units.filter((unit) => unit.team === this.playerTurn);
		},
		summedUnits() {
			const reducedUnits = this.playerUnits.reduce((acc, unit) => {
				acc[unit.unit_type] = (acc[unit.unit_type] || 0) + 1;
				return acc;
			}, {});

			return Object.entries(reducedUnits).map(([unit_type, count]) => ({
				unit_type,
				count,
			}));
		},
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
		getTotalUnitTypeCount(unitType) {
			const foundUnit = this.summedUnits.find(
				(unit) => unit.unit_type === unitType
			);

			return foundUnit ? foundUnit.count : 0;
		},
		addUnit(unitType) {
			this.selectedUnits[unitType] ??= 0;

			console.log(this.getTotalUnitTypeCount(unitType));

			if (
				this.selectedUnits[unitType] <
				this.getTotalUnitTypeCount(unitType)
			) {
				this.selectedUnits[unitType]++;
			}
		},
		minusUnit(unitType) {
			if (this.selectedUnits[unitType] > 0) {
				this.selectedUnits[unitType]--;
			}
		},
		confirmUnitSelection() {
			const confirmedUnits = { ...this.selectedUnits };
			this.moveUnits(confirmedUnits);

			this.switchUnitMovementMode(false);

			this.selectedUnits = {};
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
		</div>

		<!-- <div v-else-if="!isMovingUnits" class="territory-info">
			<UnitTray
				:playerTurn="playerTurn"
				:units="units"
				:summedUnits="summedUnits"
			/>
			<button
				v-if="currentPhase === 1 && units.length > 0"
				@click="switchUnitMovementMode(true)"
				class="move-units-button"
			>
				Move Units
			</button>
		</div> -->

		<!-- <div
			v-else-if="isMovingUnits && !isSelectingTerritory"
			class="territory-unit-movement"
		>
			<div>Unit Movement</div>
			<p>Which units do you want to move</p>
			<UnitTray
				selectMode
				:units="units"
				:summedUnits="summedUnits"
				:selectedUnits="selectedUnits"
				:getTotalUnitTypeCount="getTotalUnitTypeCount"
				:addUnit="addUnit"
				:minusUnit="minusUnit"
			/>
			<button @click="isSelectingTerritory = true">
				Confirm Unit Selection
			</button>
			<button
				@click="
					() => {
						switchUnitMovementMode(false);
						selectedUnits = {};
					}
				"
			>
				Back
			</button>
		</div> -->

		<!-- <div v-else class="territory-unit-movement">
			<div>Unit Movement</div>
			<p>Which units do you want to move</p>
			<p>
				You have selected:
				{{
					selectedTerritoryForMovement
						? selectedTerritoryForMovement
						: "No territory selected."
				}}
			</p>
			<button
				:disabled="!selectedTerritoryForMovement"
				@click="confirmUnitSelection"
			>
				Accept
			</button>
			<button @click="isSelectingTerritory = false">Back</button>
		</div> -->
		<div class="command-tray-buttons">Move units</div>
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
}
</style>
