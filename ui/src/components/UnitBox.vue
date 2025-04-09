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
		readOnly: {
			type: Boolean,
			required: false,
			default: false,
		},
		currentPhaseNum: {
			type: Number,
			required: false,
			default: 0,
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

			const alpha = this.readOnly ? "aa" : unit.selected ? "ff" : "50"; // Fully opaque if selected, semi-transparent if not

			return unitCountry
				? "#" + unitCountry.color.toString(16) + alpha
				: "#0c6f13"; // Default color
		},
		getTeamNameForUnit(unit) {
			const team = unit.team;

			return countries[team] ? countries[team].name : "Unknown";
		},
		toggle(unit) {
			if (this.readOnly) return;

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
			v-for="(group, groupIndex, unitTypeIndex) in unitGroups"
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
					:disabled="
						(sortByMovement && groupIndex <= 0) ||
						(unit.unit_type === 'ANTI-AIRCRAFT' &&
							currentPhaseNum !== 3)
					"
					:style="{
						backgroundColor: getColorForUnit(unit),
					}"
					@click="toggle(unit)"
				>
					<img
						:src="getUnitIconSrc(unit)"
						:alt="unit.unit_type"
						class="unit-icon"
						:title="unit.unit_type"
					/>
					<div
						v-if="unit.roll"
						class="roll-indicator"
						:class="{
							success: unit.roll.result,
							failure: !unit.roll.result,
						}"
						:style="{
							animationDelay: `${(unitTypeIndex + index) * 0.12}s`,
						}"
					>
						{{ unit.roll.roll }}
					</div>
					<div
						v-if="
							['TRANSPORT', 'AIRCRAFT-CARRIER'].includes(
								unit.unit_type
							)
						"
						class="cargo-dots"
					>
						<span
							v-for="n in unit.cargo"
							:key="n"
							class="cargo-dot"
						></span>
					</div>
				</button>
			</div>
		</div>
	</div>
</template>

<style scoped lang="scss">
.unit-box {
	width: 100%;
	padding: 0;

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

			button {
				position: relative;
				width: 3rem;
				height: 3rem;

				margin: 0;
				margin-bottom: 0.5rem;

				border-radius: 50%;
				background-color: #00000000;
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

				.roll-indicator {
					position: absolute;
					width: 1.5rem;
					height: 1.5rem;
					transform: translate(80%, -60%);

					border-radius: 50%;
					display: grid;
					place-items: center;

					font-size: 0.8rem;
					font-weight: bold;
					color: white;

					animation: indicatorAnimation 1s ease-in forwards;
					opacity: 0;

					&.success {
						background-color: rgb(17, 122, 17);
					}

					&.failure {
						background-color: rgb(255, 43, 43);
					}
				}
			}

			@keyframes indicatorAnimation {
				from {
					opacity: 0;
					transform: translate(80%, -60%);
				}
				to {
					opacity: 1;
					transform: translate(80%, -80%);
				}
			}
		}
	}
}
</style>
