<script>
import { useSessionStore } from "@/stores/session";
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
			sessionStore: null,
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
			return this.worldStore?.getBattles || [];
		},
		selectedTerritory() {
			if (!this.selectedBattle) return null;

			return this.worldStore?.getTerritory(this.selectedBattle);
		},
		playerTeamNum() {
			return this.sessionStore?.getPlayerTeamNum;
		},
		playerUnits() {
			if (!this.selectedTerritory) return [];

			return this.selectedTerritory.units.filter(
				(unit) => unit.team === this.playerTeamNum
			);
		},
		enemyUnits() {
			if (!this.selectedTerritory) return [];

			return this.selectedTerritory.units.filter(
				(unit) => unit.team !== this.playerTeamNum
			);
		},
	},
	methods: {},
	created() {
		this.sessionStore = useSessionStore();
		this.worldStore = useWorldStore();
	},
};
</script>

<template>
	<div class="combat-tray">
		<div class="battle-list">
			<div class="battle-list-header">Current Battles</div>
			<div v-if="battleList.length === 0">
				No battles available. You can skip this phase.
			</div>
			<button
				v-else
				v-for="battle in battleList"
				:key="battle"
				class="battle-button"
				:class="{ selected: battle === selectedBattle }"
				@click="selectedBattle = battle"
			>
				{{ battle }}
			</button>
		</div>
		<div v-if="battleList.length > 0" class="current-battle-tray">
			<div class="unit-tray-container">
				<div class="left-column">
					Your Units
					<UnitBox :units="playerUnits" readOnly></UnitBox>
				</div>
				<div class="right-column">
					Enemy Units
					<UnitBox :units="enemyUnits" readOnly></UnitBox>
				</div>
			</div>
			<div class="battle-tray-buttons">
				<button class="battle-tray-button">Attack</button>
				<button class="battle-tray-button">Retreat</button>
			</div>
		</div>
		<div v-else-if="false" class="casualty-tray">Casualty Tray</div>
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

		text-align: center;
		font-size: 1rem;

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

	.current-battle-tray {
		width: 100%;
		height: 100%;

		display: grid;
		justify-items: center;
		grid-template-rows: 5fr 1fr;

		.unit-tray-container {
			width: 100%;
			padding: 0 1rem;

			display: grid;
			grid-template-columns: 1fr 1fr;

			.left-column,
			.right-column {
				padding: 0 1rem;
				overflow-y: auto;
				display: grid;
				grid-template-rows: 5rem 1fr;
				justify-items: center;
				font-size: 1.5rem;
			}

			.left-column {
				border-right: 2px solid #ccc;
			}
		}

		.battle-tray-buttons {
			width: 50%;

			display: grid;
			grid-template-columns: 1fr 1fr;
			place-items: center;

			Button {
				width: 6rem;
			}
		}
	}
}
</style>
