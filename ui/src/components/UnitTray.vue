<script>
import { unitIcons } from "@/data/unitIcons";
import { countries } from "@/data/countries";

export default {
	props: {
		units: {
			type: Array,
			required: false,
		},
		isMovingUnits: {
			type: Boolean,
			required: false,
			default: false,
		},
		confirmedSelection: {
			type: Boolean,
			required: false,
			default: false,
		},
		playerTurn: {
			type: Number,
			required: false,
			default: 0,
		},
		toggleUnit: {
			type: Function,
			required: false,
		},
	},
	computed: {
		playerUnits() {
			return this.units.filter((unit) => unit.team === this.playerTurn);
		},
		movementGroups() {
			return this.playerUnits.reduce((acc, unit) => {
				if (acc[unit.movement] === undefined) {
					acc[unit.movement] = [];
				}

				acc[unit.movement].push(unit);

				return acc;
			}, {});
		},
		friendlyUnits() {
			// Allies players are teams 0, 1, and 2
			// Axis players are teams 3 and 4
			return this.units.filter((unit) => {
				if (this.playerTurn <= 2) {
					return unit.team <= 2 && unit.team !== this.playerTurn;
				} else {
					// For team 3, we want to include both team 1 and team 2 units
					return unit.team >= 3 && unit.team !== this.playerTurn;
				}
			});
		},
		enemyUnits() {
			// Allies players are teams 0, 1, and 2
			// Axis players are teams 3 and 4
			return this.units.filter((unit) => {
				if (this.playerTurn <= 2) {
					return unit.team >= 3;
				} else {
					// For team 3, we want to include both team 1 and team 2 units
					return unit.team <= 2;
				}
			});
		},
		selectedUnits() {
			return this.units.filter((unit) => unit.selected);
		},
		countryFlagSrc() {
			const country = countries.find((c) => c.name === this.teamName);

			return country ? country.flagIcon : "";
		},
	},
	methods: {
		getUnitIconSrc(unit) {
			const unitIcon = unitIcons.find((u) => u.name === unit.unit_type);

			return unitIcon ? unitIcon.unitIcon : "";
		},
		getColorForUnit(unit) {
			const unitCountry = countries[unit.team];

			const alpha = unit.selected ? "ff" : "40"; // Fully opaque if selected, semi-transparent if not

			return unitCountry
				? "#" + unitCountry.color.toString(16) + alpha
				: "#0c6f13"; // Default color
		},
		getTeamNameForUnit(unit) {
			const team = unit.team;

			return countries[team] ? countries[team].name : "Unknown";
		},
	},
};
</script>

<template>
	<div class="unit-box-header">Units in Territory</div>
	<div v-if="!isMovingUnits" class="unit-box">
		<!-- units will be sorted by remaining movement ascending -->
		<div
			v-for="(group, movement) in movementGroups"
			:key="movement"
			class="unit-box-movement-group"
		>
			Remaining Movement: {{ movement }}
			<div class="unit-box-group-container">
				<button
					:disabled="Number(movement) === 0"
					v-for="(unit, index) in group"
					:key="`${index}-${unit.unit_type}`"
					class="unit-button"
					:style="{
						backgroundColor: getColorForUnit(unit),
					}"
					:onClick="() => toggleUnit(unit, index)"
				>
					<img
						:src="getUnitIconSrc(unit)"
						:alt="unit.name"
						class="unit-icon"
						:title="unit.unit_type"
					/>
				</button>
			</div>
		</div>

		<div v-if="friendlyUnits.length" class="friendly-units-in-territory">
			Friendly Units in Territory:
			<div class="unit-box-group-container">
				<div
					v-for="(unit, index) in friendlyUnits"
					:key="`${index}-${unit.unit_type}`"
					class="unit-button"
					:style="{
						backgroundColor: getColorForUnit(unit),
					}"
				>
					<img
						:src="getUnitIconSrc(unit)"
						:alt="unit.name"
						class="unit-icon"
						:title="
							unit.unit_type + ' - ' + getTeamNameForUnit(unit)
						"
					/>
				</div>
			</div>
		</div>

		<div v-if="enemyUnits.length" class="enemy-units-in-territory">
			Enemy Units in Territory:
			<div class="unit-box-group-container">
				<div
					v-for="(unit, index) in enemyUnits"
					:key="`${index}-${unit.unit_type}`"
					class="unit-button"
					:style="{
						backgroundColor: getColorForUnit(unit),
					}"
				>
					<img
						:src="getUnitIconSrc(unit)"
						:alt="unit.name"
						class="unit-icon"
						:title="
							unit.unit_type + ' - ' + getTeamNameForUnit(unit)
						"
					/>
				</div>
			</div>
		</div>
	</div>

	<div v-else class="unit-box">
		<div class="selected-units">
			Units to be Moved:
			<div class="unit-box-group-container">
				<div
					v-for="(unit, index) in selectedUnits"
					:key="`${index}-${unit.unit_type}`"
					class="unit-button"
					:style="{
						backgroundColor: getColorForUnit(unit),
					}"
				>
					<img
						:src="getUnitIconSrc(unit)"
						:alt="unit.name"
						class="unit-icon"
						:title="
							unit.unit_type + ' - ' + getTeamNameForUnit(unit)
						"
					/>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped lang="scss">
.unit-box-header {
	width: 100%;
	padding-top: 0.5rem;
	text-align: center;
	font-size: 1.2rem;
}

.unit-box {
	width: 100%;
	height: 100%;

	padding: 1rem;
	// background-color: rgba(0, 0, 0, 0.4);

	p {
		padding-bottom: 0.5rem;
		font-size: 1rem;
	}

	.unit-box-movement-group {
		font-size: 0.8rem;
	}

	.friendly-units-in-territory,
	.enemy-units-in-territory {
		font-size: 1rem;
		padding-top: 0.75rem;
	}

	.unit-box-movement-group,
	.friendly-units-in-territory,
	.enemy-units-in-territory,
	.selected-units {
		.unit-box-group-container {
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(3rem, 1fr));

			button:active {
				cursor: pointer;
			}

			.unit-button {
				width: 3rem; /* Adjust size */
				height: 3rem;
				margin: 0;

				border-radius: 50%; /* Makes it circular */
				background-color: #00000000; /* Default color */
				border: none;
				display: flex;
				justify-content: center;
				align-items: center;

				transition:
					background-color 0.3s ease,
					transform 0.2s ease;

				.unit-icon {
					width: 3rem;
					height: auto;
				}
			}
		}
	}
}
</style>
