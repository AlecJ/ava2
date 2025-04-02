<script>
import { unitIcons } from "@/data/unitIcons";
import { unitData } from "@/data/unitData";
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
			// units: [
			// 	"INFANTRY",
			// 	"ARTILLERY",
			// 	"TANK",
			// 	"FIGHTER",
			// 	"BOMBER",
			// 	"BATTLESHIP",
			// 	"DESTROYER",
			// 	"AIRCRAFT-CARRIER",
			// 	"TRANSPORT",
			// 	"SUBMARINE",
			// 	"INDUSTRIAL-COMPLEX",
			// 	"ANTI-AIRCRAFT",
			// ],
		};
	},
	watch: {},
	computed: {
		units() {
			return Object.keys(unitData).map((unit) => {
				return { type: unit, ...unitData[unit] };
			});
		},
	},
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
				:key="`${unit.type}`"
				@click="purchaseUnit(unit.type)"
			>
				<div class="unit-name-and-cost">
					<p class="cost">{{ unit.cost }}</p>
					<p class="name">{{ unit.type }}</p>
				</div>

				<img
					:src="getUnitIconSrc(unit.type)"
					:alt="unit.type"
					class="unit-icon"
					:title="unit.type"
				/>
				<div class="unit-details">
					<p>attack: {{ unit.attack }}</p>
					<p>defense: {{ unit.defense }}</p>
					<p>movement: {{ unit.movement }}</p>
				</div>
				<div class="unit-description">
					<p>{{ unit.description }}</p>
				</div>
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
		gap: 1rem;

		.purchase-unit-button {
			width: 150px;
			height: 200px;
			padding: 0.2rem;

			display: grid;
			place-items: center;
			grid-template-rows: 1fr 4fr 3fr 2fr;

			.unit-name-and-cost {
				display: grid;
				grid-template-columns: 1fr 5fr;

				.cost {
					width: 1.6rem;
					height: 1.6rem;
					background-color: orange;
					border-radius: 50%;

					display: grid;
					place-items: center;
				}
			}

			.unit-icon {
				width: 50%;
				height: auto;
			}

			.unit-details {
				display: grid;
				grid-template-columns: auto auto;

				justify-items: start;

				font-size: 0.75rem;
			}

			.unit-description {
				font-size: 0.75rem;
			}
		}
	}
}
</style>
