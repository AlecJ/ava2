<script>
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
		playerTurn: {
			type: Number,
			required: false,
			default: 0,
		},
	},
	data() {
		return {
			selectedUnits: {},
		};
	},
	methods: {
		getTotalUnitTypeCount(unitType) {
			const foundUnit = this.units.find(
				(unit) =>
					unit.type === unitType && unit.team === this.playerTurn
			);

			return foundUnit ? foundUnit.count : 0;
		},
		addUnit(unitType) {
			this.selectedUnits[unitType] ??= 0;

			if (
				this.selectedUnits[unitType] <
				this.getTotalUnitTypeCount(unitType)
			) {
				this.selectedUnits[unitType]++;
				this.test = true;
			}
		},
		minusUnit(unitType) {
			if (this.selectedUnits[unitType] > 0) {
				this.selectedUnits[unitType]--;
			}
		},
	},
};
</script>

<template>
	<div v-if="!selectMode" class="unit-box">
		Units:
		<div v-for="(unit, index) in units" :key="`${index}-${unit.type}`">
			<div>{{ unit.type }}</div>
			<div>x{{ unit.count }}</div>
		</div>
	</div>

	<div v-else class="unit-box">
		Units:
		<div v-for="(unit, index) in units" :key="`${index}-${unit.type}`">
			<div>{{ unit.type }}</div>
			<div>{{ selectedUnits[unit.type] || 0 }} / {{ unit.count }}</div>
			<button
				:disabled="(selectedUnits[unit.type] ?? 0) === unit.count"
				@click="addUnit(unit.type)"
			>
				+
			</button>
			<button
				:disabled="(selectedUnits[unit.type] ?? 0) < 1"
				@click="minusUnit(unit.type)"
			>
				-
			</button>
		</div>
	</div>
</template>

<style scoped lang="scss"></style>
