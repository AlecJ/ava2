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
	},
};
</script>

<template>
	<div class="purchase-tray">
		<div class="purchase-tray-title">Purchase Units</div>
		<div class="purchase-tray-desc">
			Units purchased now will be placed during the mobilization phase at
			the end of your turn.
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

	.purchase-tray-title {
		font-size: 1.5rem;
		font-weight: bold;
		text-align: center;
	}

	.purchase-tray-desc {
		font-size: 1rem;
		text-align: center;
		margin-bottom: 1rem;
	}

	.unit-board {
		width: 100%;

		display: grid;
		grid-template-columns: repeat(auto-fill, 150px);
		gap: 1rem;
		overflow-y: auto;
		overflow-x: hidden;

		.purchase-unit-button {
			width: 150px;
			height: 200px;
			padding: 0.2rem;
			margin: 0 0.75rem;

			display: grid;
			place-items: center;
			grid-template-rows: 20% 35% 15% 30%;

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
				max-width: 100%;
				max-height: 100%;
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
