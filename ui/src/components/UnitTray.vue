<script>
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
	},
};
</script>

<template>
	<div v-if="!selectMode" class="unit-box">
		Units:
		<div
			v-for="(unit, index) in summedUnits"
			:key="`${index}-${unit.unit_type}`"
		>
			<div>{{ unit.unit_type }}</div>
			<div>x{{ unit.count }}</div>
		</div>
	</div>

	<div v-else-if="!confirmedSelection" class="unit-box">
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
	</div>
</template>

<style scoped lang="scss">
.unit-row {
	display: grid;
	align-items: center;
	justify-items: center;
	grid-template-columns: 3fr 1fr 1fr 1fr;

	button {
		margin: 0.25rem;
	}
}
</style>
