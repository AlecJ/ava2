<script>
import { unitIcons } from "@/data/unitIcons";

export default {
	props: {
		units: {
			type: Array,
			required: false,
		},
		summedUnits: {
			type: Array,
			required: false,
		},
		selectedUnits: {
			type: Object,
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
		getTotalUnitTypeCount: {
			type: Function,
			required: false,
		},
		addUnit: {
			type: Function,
			required: false,
		},
		minusUnit: {
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
	},
	methods: {
		getUnitIconSrc(unit) {
			const unitIcon = unitIcons.find((u) => u.name === unit.unit_type);

			return unitIcon ? unitIcon.unitIcon : "";
		},
	},
};
</script>

<template>
	<!-- v-if="!selectMode" -->
	<div class="unit-box">
		Units

		<!-- units will be sorted by remaining movement ascending -->
		<div
			v-for="(group, movement) in movementGroups"
			:key="movement"
			class="unit-box-movement-group"
		>
			Remaining Movement: {{ movement }}
			<div class="unit-box-group-container">
				<div
					v-for="(unit, index) in group"
					:key="`${index}-${unit.unit_type}`"
					class="unit-box-unit"
				>
					<img
						:src="getUnitIconSrc(unit)"
						:alt="unit.name"
						class="unit-icon"
					/>
				</div>
			</div>
		</div>
	</div>

	<!-- <div v-else-if="!confirmedSelection" class="unit-box">
		Units:
		<div
			class="unit-row"
			v-for="(unit, index) in summedUnits"
			:key="`${index}-${unit.unit_type}`"
		>
			<div>{{ unit.unit_type }}</div>
			<div>
				{{ selectedUnits[unit.unit_type] || 0 }} / {{ unit.count }}
			</div>
			<button
				:disabled="(selectedUnits[unit.unit_type] ?? 0) === unit.count"
				@click="addUnit(unit.unit_type)"
			>
				+
			</button>
			<button
				:disabled="(selectedUnits[unit.unit_type] ?? 0) < 1"
				@click="minusUnit(unit.unit_type)"
			>
				-
			</button>
		</div>
	</div>

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
.unit-box {
	width: 100%;
	height: 100%;
	max-height: 100%;

	padding: 1rem;
	overflow-y: scroll;

	.unit-box-movement-group {
		font-size: 0.8rem;

		.unit-box-group-container {
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(3rem, 1fr));
		}

		.unit-box-unit {
			.unit-icon {
				width: 3rem;
				height: 3rem;
			}
		}
	}
}
</style>
