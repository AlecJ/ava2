<script>
import { unitIcons } from "@/data/unitIcons";
import LoadingSpinner from "@/components/LoadingSpinner.vue";

export default {
	components: {
		LoadingSpinner,
	},
	props: {
		purchaseUnit: {
			type: Function,
			required: true,
		},
	},
	data() {
		return {
			units: [
				"INFANTRY",
				"ARTILLERY",
				"TANK",
				"FIGHTER",
				"BOMBER",
				"BATTLESHIP",
				"DESTROYER",
				"AIRCRAFT-CARRIER",
				"TRANSPORT",
				"SUBMARINE",
				"INDUSTRIAL-COMPLEX",
				"ANTI-AIRCRAFT",
			],
		};
	},
	watch: {},
	computed: {},
	methods: {
		getUnitIconSrc(unit) {
			const unitIcon = unitIcons.find((u) => u.name === unit);

			return unitIcon ? unitIcon.unitIcon : "";
		},
		// getColorForUnit(unit) {
		// 	const unitCountry = countries[unit.team];

		// 	const alpha = unit.selected ? "ff" : "40"; // Fully opaque if selected, semi-transparent if not

		// 	return unitCountry
		// 		? "#" + unitCountry.color.toString(16) + alpha
		// 		: "#0c6f13"; // Default color
		// },
		// getTeamNameForUnit(unit) {
		// 	const team = unit.team;

		// 	return countries[team] ? countries[team].name : "Unknown";
		// },
	},
};
</script>

<template>
	<div class="purchase-tray">
		<div class="purchase-tray-title">Purchase Units</div>
		<div class="purchase-tray-desc">
			Units purchased now will be added to the game at the end of your
			turn.
		</div>
		<div class="unit-board">
			<button
				class="purchase-unit-button"
				v-for="unit in units"
				:key="`${unit}`"
				@click="purchaseUnit(unit)"
			>
				<img
					:src="getUnitIconSrc(unit)"
					:alt="unit"
					class="unit-icon"
					:title="unit"
				/>
			</button>
		</div>
	</div>
</template>

<style scoped lang="scss">
.purchase-tray {
	width: 100%;
	height: 100%;

	display: grid;

	.unit-board {
		width: 100%;

		display: grid;
		grid-template-columns: repeat(auto-fill, 150px);

		.purchase-unit-button {
			width: 150px;
			height: 200px;

			.unit-icon {
				width: 3rem;
				height: auto;
			}
		}
	}
}
</style>
