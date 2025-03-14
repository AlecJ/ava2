<script>
import { unitIcons } from "@/data/unitIcons";
import { countries } from "@/data/countries";

export default {
	props: {
		units: {
			type: Array,
			required: false,
		},
		selectMode: {
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
		confirmedUnits() {
			return this.units.filter(
				(unit) => this.selectedUnits[unit.unit_type] > 0
			);
		},
		movementGroups() {
			return this.units.reduce((acc, unit) => {
				if (acc[unit.movement] === undefined) {
					acc[unit.movement] = [];
				}

				acc[unit.movement].push(unit);

				return acc;
			}, {});
		},
		unitIconSrc() {
			const unit = unitIcons.find((unit) => unit.name === "INFANTRY");

			return unit ? unit.unitIcon : "";
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
	},
};
</script>

<template>
	<!-- v-if="!selectMode" -->
	<div class="unit-box-header">Units in Territory</div>
	<div class="unit-box">
		<!-- units will be sorted by remaining movement ascending -->
		<div
			v-for="(group, movement) in movementGroups"
			:key="movement"
			class="unit-box-movement-group"
		>
			Remaining Movement: {{ movement }}
			<div class="unit-box-group-container">
				<button
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
	</div>

	<!-- 

	<div v-else class="unit-box">
		Units:
		<div
			v-for="(unit, index) in confirmedUnits"
			:key="`${index}-${unit.unit_type}`"
		>
			<div>{{ unit.unit_type }}</div>
			<div>x{{ selectedUnits[unit.unit_type] }}</div>
		</div>
	</div> -->
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

		.unit-box-group-container {
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(3rem, 1fr));

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
				cursor: pointer;
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
