<script>
import { countries } from "@/data/countries";
import UnitTray from "@/components/UnitTray.vue";

export default {
	components: {
		UnitTray,
	},
	props: {
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
			const foundUnit = this.units.find(
				(unit) =>
					unit.type === unitType && unit.team === this.playerTurn
			);

			return foundUnit ? foundUnit.count : 0;
		},
		addUnit(unitType) {
			this.selectedUnits[unitType] ??= 0;

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
	},
};
</script>

<template>
	<div
		:class="['right-side-bar', { active: !!territoryData }]"
		@mousedown.prevent.stop
	>
		<div v-if="!isMovingUnits" class="territory-info">
			<div class="country-name">{{ territoryName }}</div>
			<div class="controlling-country">Occupied by: {{ teamName }}</div>
			<div class="territory-power">Production Score: {{ power }}</div>
			<UnitTray :playerTurn="playerTurn" :units="units" />
			<button
				v-if="currentPhase === 1 && units.length > 0"
				@click="() => switchUnitMovementMode(true)"
				class="move-units-button"
			>
				Move Units
			</button>
		</div>
		<div
			v-else-if="isMovingUnits && !isSelectingTerritory"
			class="territory-unit-movement"
		>
			<div>Unit Movement</div>
			<p>Which units do you want to move</p>
			<UnitTray
				selectMode
				:units="units"
				:selectedUnits="selectedUnits"
				:getTotalUnitTypeCount="getTotalUnitTypeCount"
				:addUnit="addUnit"
				:minusUnit="minusUnit"
			/>
			<button @click="() => (this.isSelectingTerritory = true)">
				Confirm Unit Selection
			</button>
		</div>
		<div v-else class="territory-unit-movement">
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
				@click="moveUnits(selectedUnits)"
			>
				Accept
			</button>
			<button @click="">Back</button>
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
	min-width: 200px;
	max-width: 600px;
	height: 75%;
	padding: 1rem;

	background-color: rgba(33, 32, 32, 0.931);
	border: 2px solid white;
	border-radius: 2rem 0 0 2rem;
	border-right: 0;

	display: grid;
	place-items: center;
	pointer-events: auto;

	transform: translateX(90%);
	transition: transform 0.3s ease-in-out;

	color: white;

	&.active {
		transform: translateX(0%);
	}

	.territory-info,
	.territory-unit-movement {
		display: grid;
		place-items: center;
	}
}
</style>
