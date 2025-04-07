<script>
import { useWorldStore } from "@/stores/world";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import UnitBox from "@/components/UnitBox.vue";

export default {
	components: {
		LoadingSpinner,
		UnitBox,
	},
	props: {},
	data() {
		return {
			worldStore: null,
			selectedBattle: null,
		};
	},
	watch: {
		battleList: {
			handler(newVal) {
				if (newVal.length > 0) {
					this.selectedBattle = newVal[0];
				}
			},
			immediate: true,
		},
	},
	computed: {
		battleList() {
			return this.worldStore?.getCombatTerritories || [];
		},
		selectedTerritory() {
			return this.worldStore?.getTerritory(this.selectedBattle);
		},
	},
	methods: {},
	created() {
		this.worldStore = useWorldStore();
	},
};
</script>

<template>
	<div class="combat-tray">
		<div class="battle-list">
			<div class="battle-list-header">Current Battles</div>
			<button
				v-for="battle in battleList"
				:key="battle"
				class="battle-button"
				:class="{ selected: battle === selectedBattle }"
				@click="selectedBattle = battle"
			>
				{{ battle }}
			</button>
		</div>
		<div class="current-battle-tray">
			{{ selectedTerritory }}
		</div>
	</div>
</template>

<style scoped lang="scss">
.combat-tray {
	width: 100%;
	height: 100%;
	justify-self: start;

	display: grid;
	grid-template-columns: 1fr 3fr;

	.battle-list {
		height: 100%;
		padding-top: 0.5rem;
		padding-right: 0.75rem;
		overflow-y: auto;

		display: grid;
		grid-auto-rows: min-content;
		gap: 0.5rem;

		border-right: 2px solid #ccc; // remove
		// border-radius: 8px; // remove

		.battle-list-header {
			font-size: clamp(1rem, 5vw, 1.3rem);
			font-weight: bold;
			text-align: center;
		}

		.battle-button {
			width: 100%;
			height: 3rem;
			margin: 0;
			border: unset;

			&.selected {
				border: 1px solid gold;
			}
		}
	}
}
</style>
