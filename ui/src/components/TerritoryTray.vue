<script>
import { useWorldStore } from "@/stores/world";
import { countries } from "@/data/countries";
import UnitBox from "@/components/UnitBox.vue";
import ShipLoadingTray from "@/components/ShipLoadingTray.vue";

import LoadingSpinner from "@/components/LoadingSpinner.vue";

export default {
	components: {
		UnitBox,
		ShipLoadingTray,
		LoadingSpinner,
	},
	props: {
		isLoading: {
			type: Boolean,
			required: false,
		},
		player: {
			type: Object,
			required: true,
		},
		territoryData: {
			type: Object,
			required: false,
		},
		neighboringTerritoriesData: {
			type: Object,
			required: false,
			default: [],
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
			worldStore: null,
			territoryName: null,
			teamName: null,
			power: 0,
			units: [],
			neighboringLandUnits: [],
			isSelectingTerritory: false,
			isLoadingTransports: false,
			transportToUnload: null,
		};
	},
	watch: {
		territoryData(newVal) {
			if (newVal) {
				// this triggers everytime the world state is updated
				// if its the same territory, some values will not change
				if (newVal.name !== this.territoryName) {
					this.isLoadingTransports = false;
				}

				this.territoryName = newVal.name;
				this.teamName = this.getCountryName();
				this.power = newVal.power;
				this.units = newVal.units;
				this.units.sort((a, b) => a.movement - b.movement);
				this.neighboringLandUnits = [];
				this.isSelectingTerritory = false;
				this.transportToUnload = null;
			} else {
				// Delay clearing the name until after the sidebar transition ends
				setTimeout(() => {
					this.resetData();
				}, 500);
			}
		},
		neighboringTerritoriesData() {
			this.neighboringLandUnits = this.calcNeighboringLandUnits();
		},
	},
	computed: {
		countryFlagSrc() {
			const country = countries.find((c) => c.name === this.teamName);

			return country ? country.flagIcon : "";
		},
		playerTeamNum() {
			return countries.findIndex(
				(country) => country.name === this.player.country
			);
		},
		currentPlayerTurn() {
			return this.currentTurnNum % 5;
		},
		isPlayerTurn() {
			return this.playerTeamNum === this.currentPlayerTurn;
		},
		isMovementPhase() {
			return this.currentPhaseNum === 1 || this.currentPhaseNum === 3;
		},
		playerUnits() {
			return this.units.filter(
				(unit) => unit.team === this.playerTeamNum
			);
		},
		friendlyUnits() {
			// Allies players are teams 0, 2, and 4
			// Axis players are teams 1 and 3
			return this.units.filter((unit) => {
				if ([0, 2, 4].includes(this.playerTeamNum)) {
					return (
						[0, 2, 4].includes(unit.team) &&
						unit.team !== this.playerTeamNum
					);
				} else {
					return (
						[1, 3].includes(unit.team) &&
						unit.team !== this.playerTeamNum
					);
				}
			});
		},
		enemyUnits() {
			// Allies players are teams 0, 2, and 4
			// Axis players are teams 1 and 3
			return this.units.filter((unit) => {
				if ([0, 2, 4].includes(this.playerTeamNum)) {
					return [1, 3].includes(unit.team);
				} else {
					return [0, 2, 4].includes(unit.team);
				}
			});
		},
		selectedUnits() {
			return this.units.filter((unit) => unit.selected);
		},
		transportsInTerritory() {
			return this.playerUnits.filter(
				(unit) =>
					unit.unit_type === "TRANSPORT" ||
					unit.unit_type === "AIRCRAFT-CARRIER"
			);
		},
		territoryHasTransports() {
			return this.playerUnits.some(
				(unit) =>
					unit.unit_type === "TRANSPORT" ||
					unit.unit_type === "AIRCRAFT-CARRIER"
			);
		},
	},
	methods: {
		resetData() {
			if (!this.territoryData) {
				this.territoryName = null;
				this.teamName = null;
				this.power = 0;
				this.units = [];
				this.isSelectingTerritory = false;
				this.isLoadingTransports = false;
			}
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
		switchTerritorySelectionMode(bool) {
			this.isSelectingTerritory = bool;
			this.setIsSelectingTerritory(bool);
		},
		switchLoadingTransportsMode(bool) {
			this.isLoadingTransports = bool;
		},
		placeUnits() {
			this.worldStore.mobilizeUnits(
				this.selectedUnits,
				this.selectedTerritory
			);
		},
		confirmUnitSelection() {
			this.worldStore.moveUnits(
				this.territoryName,
				this.selectedTerritory,
				this.selectedUnits
			);

			this.switchTerritorySelectionMode(false);
		},
		calcNeighboringLandUnits() {
			return this.neighboringTerritoriesData
				.filter((territory) => {
					return !territory.is_ocean && territory.units?.length;
				})
				.flatMap((territory) => {
					return territory.units
						.filter(
							(unit) =>
								["INFANTRY", "TANK", "ARTILLERY"].includes(
									unit.unit_type
								) && unit.team === this.playerTeamNum
						)
						.map((unit) => {
							return { ...unit, territory: territory.name };
						});
				});
		},
		setTransportToUnload(transport) {
			this.transportToUnload = transport;
			this.switchTerritorySelectionMode(!!transport);
		},
		confirmTransportUnload() {
			this.worldStore.unloadTransport(
				this.territoryName,
				this.selectedTerritory,
				this.transportToUnload
			);

			this.switchTerritorySelectionMode(false);
			this.setTransportToUnload(null);
		},
	},
	created() {
		this.worldStore = useWorldStore();
	},
};
</script>

<template>
	<div class="territory-tray">
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

		<div class="territory-tray-content">
			<LoadingSpinner v-if="isLoading" />

			<div class="unit-box-header" v-if="!isLoadingTransports">
				Units in Territory
			</div>
			<div class="unit-box-header" v-if="transportToUnload">
				Unloading Transport
			</div>

			<div class="unit-box-header" v-else>Nearby Units to Load</div>
			<!-- units will be sorted by remaining movement ascending -->
			<UnitBox
				v-if="!isSelectingTerritory && !transportToUnload"
				:readOnly="!isPlayerTurn || !isMovementPhase"
				:units="
					isLoadingTransports ? neighboringLandUnits : playerUnits
				"
				:sortByMovement="true"
			></UnitBox>

			<div
				v-if="
					friendlyUnits.length &&
					!isSelectingTerritory &&
					!isLoadingTransports &&
					!transportToUnload
				"
				class="friendly-units-in-territory"
			>
				Friendly Units in Territory:
				<UnitBox :units="friendlyUnits" readOnly></UnitBox>
			</div>

			<div
				v-if="
					enemyUnits.length &&
					!isSelectingTerritory &&
					!isLoadingTransports &&
					!transportToUnload
				"
				class="enemy-units-in-territory"
			>
				Enemy Units in Territory:
				<UnitBox :units="enemyUnits" readOnly></UnitBox>
			</div>

			<div
				v-if="isSelectingTerritory && !transportToUnload"
				class="unit-box"
			>
				<div class="selected-units">
					Units to be Moved:
					<UnitBox :units="selectedUnits" readOnly></UnitBox>
				</div>
			</div>

			<ShipLoadingTray
				v-if="isLoadingTransports"
				:territoryName="territoryName"
				:landUnits="neighboringLandUnits"
				:transports="transportsInTerritory"
				:transportToUnload="transportToUnload"
				:setTransportToUnload="setTransportToUnload"
			></ShipLoadingTray>

			<div v-if="isSelectingTerritory">
				<p>Select a Territory</p>
				<p>
					You have selected:
					{{ selectedTerritory || "None" }}
				</p>
			</div>
		</div>

		<div
			class="territory-tray-buttons"
			v-if="isPlayerTurn && isMovementPhase"
		>
			<button
				v-if="!isSelectingTerritory && !isLoadingTransports"
				:disabled="!selectedUnits.length"
				@click="switchTerritorySelectionMode(true)"
			>
				Move Units
			</button>
			<button
				v-if="
					!isSelectingTerritory &&
					territoryHasTransports &&
					!isLoadingTransports
				"
				@click="switchLoadingTransportsMode(true)"
			>
				Load/Unload Ships
			</button>
			<button
				v-if="isSelectingTerritory || isLoadingTransports"
				@click="
					switchTerritorySelectionMode(false);
					switchLoadingTransportsMode(false);
					setTransportToUnload(null);
				"
			>
				Back
			</button>
			<button
				v-if="isSelectingTerritory && !transportToUnload"
				:disabled="!selectedTerritory"
				@click="confirmUnitSelection"
			>
				Confirm Unit Movement
			</button>
			<button
				v-if="!!transportToUnload"
				:disabled="!selectedTerritory"
				@click="confirmTransportUnload"
			>
				Confirm Unloading
			</button>
		</div>
	</div>
</template>

<style scoped lang="scss">
.territory-tray {
	width: 24rem;
	// width: 42%;
	// min-width: 24rem;
	height: 100%;
	justify-self: start;

	display: grid;
	grid-template-rows: 1fr 1fr 5fr 1fr;
	place-items: center;
	pointer-events: auto;

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

	.territory-tray-content {
		width: 100%;
		height: 100%;
		overflow-y: auto;
	}

	.unit-box-header {
		width: 100%;
		padding-top: 0.5rem;
		text-align: center;
		font-size: 1.2rem;
	}

	.territory-tray-buttons {
		display: grid;
		grid-template-columns: auto auto;
	}
}
</style>
