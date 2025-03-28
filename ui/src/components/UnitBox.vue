<script>
import { unitData } from "@/data/unitData";
import { unitIcons } from "@/data/unitIcons";
import { countries } from "@/data/countries";

export default {
	props: {
		units: {
			type: Array,
			required: true,
		},
		sortByMovement: {
			type: Boolean,
			required: false,
			default: false,
		},
	},
	computed: {
		unitsSortedByMovement() {
			if (!this.sortByMovement) return {};

			return this.units.reduce((acc, unit) => {
				if (acc[unit.movement] === undefined) {
					acc[unit.movement] = [];
				}

				acc[unit.movement].push(unit);

				return acc;
			}, {});
		},
		unitsSortedByType() {
			if (this.sortByMovement) return {};

			const groupedUnits = this.units.reduce((acc, unit) => {
				if (acc[unit.unit_type] === undefined) {
					acc[unit.unit_type] = [];
				}

				acc[unit.unit_type].push(unit);

				return acc;
			}, {});

			return Object.keys(unitData)
				.filter((type) => groupedUnits[type])
				.reduce((acc, type) => {
					acc[type] = groupedUnits[type];
					return acc;
				}, {});
		},
		unitGroups() {
			return this.sortByMovement
				? this.unitsSortedByMovement
				: this.unitsSortedByType;
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
		toggle(unit) {
			if (!unit.selected) {
				unit.selected = true;
			} else {
				unit.selected = !unit.selected;
			}
		},
	},
};
</script>

<template>
	<div class="unit-box">
		<!-- units will be sorted by remaining movement ascending -->
		<div
			v-for="(group, groupIndex) in unitGroups"
			:key="groupIndex"
			class="unit-box-group"
		>
			<div v-if="sortByMovement">
				Remaining Movement: {{ groupIndex }}
			</div>
			<div class="unit-box-group-container">
				<button
					v-for="(unit, index) in group"
					:key="`${index}-${unit.unit_type}`"
					class="unit-button"
					:style="{
						backgroundColor: getColorForUnit(unit),
					}"
					:onClick="() => toggle(unit)"
				>
					<img
						:src="getUnitIconSrc(unit)"
						:alt="unit.unit_type"
						class="unit-icon"
						:title="unit.unit_type"
					/>
				</button>
			</div>
		</div>
	</div>
</template>

<style scoped lang="scss">
.unit-box {
	width: 100%;
	height: 100%;

	padding: 1rem;
	// background-color: rgba(0, 0, 0, 0.4);

	p {
		padding-bottom: 0.5rem;
		font-size: 1rem;
	}

	.unit-box-group {
		font-size: 0.8rem;
	}

	.unit-box-group,
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
