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
			playerUnits: [],
		};
	},
	watch: {
		battleList: {
			handler(newVal) {
				if (newVal.length > 0) {
					this.selectedBattle =
						newVal.find((battle) => battle.result === null) ||
						newVal[0];

					this.updatePlayerUnits();
				}
			},
			immediate: true,
		},
		selectedTerritory: {
			handler(newTerritory) {
				if (!newTerritory || !this.selectedBattle) return;

				this.updatePlayerUnits();
			},
			immediate: true,
			deep: true,
		},
	},
	computed: {
		battleList() {
			return this.worldStore?.getBattles || [];
		},
		hasUnresolvedBattles() {
			return this.worldStore?.getBattles.some(
				(battle) => battle.result === null
			);
		},
		selectedTerritory() {
			if (!this.selectedBattle) return null;

			return this.worldStore?.getTerritory(this.selectedBattle.location);
		},
		playerTeamNum() {
			return this.sessionStore?.getPlayerTeamNum;
		},
		enemyUnits() {
			if (!this.selectedTerritory || !this.selectedBattle) return [];

			return this.selectedTerritory.units
				.filter((unit) => unit.team !== this.playerTeamNum)
				.map((unit) => ({
					...unit,
					roll: this.selectedBattle.defender_rolls.find(
						(roll) => roll.unit_id === unit.unit_id
					),
					is_battleship_hit:
						this.selectedBattle.hit_battleships.includes(
							unit.unit_id
						),
				}));
		},
		isSelectingCasualties() {
			return this.selectedBattle?.is_resolving_turn;
		},
		attackerCasualtyCount() {
			if (!this.selectedBattle) return 0;

			return this.selectedBattle.defender_rolls.filter(
				(roll) => roll.result
			).length;
		},
		maxPossibleCasualtyCount() {
			if (!this.selectedBattle) return 0;

			return this.playerUnits.reduce(
				(acc, unit) =>
					acc +
					(unit.unit_type === "BATTLESHIP" && !unit.is_battleship_hit
						? 2
						: 1),
				0
			);
		},
		selectedUnits() {
			return this.playerUnits
				.filter((unit) => unit.selected || unit.selectedCount > 0)
				.flatMap((unit) =>
					unit.selected
						? [unit]
						: Array(unit.selectedCount).fill(unit)
				);
		},
	},
	methods: {
		attack() {
			if (!this.selectedBattle) return;

			this.worldStore?.combatAttack(this.selectedBattle.location);
		},
		retreat() {
			if (!this.selectedBattle) return;

			this.worldStore?.combatRetreat(this.selectedBattle.location);
		},
		selectCasualties() {
			if (!this.selectedBattle) return;

			this.worldStore?.combatSelectCasualties(
				this.selectedBattle.location,
				this.selectedUnits
			);
		},
		updatePlayerUnits() {
			if (!this.selectedTerritory || !this.selectedBattle) return;

			this.playerUnits = [...this.selectedTerritory.units]
				.filter((unit) => unit.team === this.playerTeamNum)
				.map((unit) => ({
					...unit,
					roll: this.selectedBattle.attacker_rolls.find(
						(roll) => roll.unit_id === unit.unit_id
					),
					is_battleship_hit:
						this.selectedBattle.hit_battleships.includes(
							unit.unit_id
						),
					selectedCount: 0,
				}));
		},
	},
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
				:class="{
					selected: battle === selectedBattle,
					win: battle.result === 'attacker',
					lose: battle.result === 'defender',
				}"
				@click="selectedBattle = battle"
			>
				{{ battle.location }}
			</button>
		</div>
		<div v-if="battleList.length > 0" class="current-battle-tray">
			<div class="unit-tray-container">
				<div class="left-column">
					Your Units
					<UnitBox
						:units="playerUnits"
						:readOnly="
							!isSelectingCasualties ||
							attackerCasualtyCount === 0
						"
						:canAddToSelectedUnits="
							selectedUnits.length <
							Math.min(
								attackerCasualtyCount,
								maxPossibleCasualtyCount
							)
						"
					></UnitBox>
				</div>
				<div class="right-column">
					Enemy Units
					<UnitBox :units="enemyUnits" readOnly></UnitBox>
				</div>
			</div>
			<div v-if="!hasUnresolvedBattles" class="battle-tray-buttons">
				All combats finished. You can skip this phase.
			</div>
			<div v-else-if="!isSelectingCasualties" class="battle-tray-buttons">
				<button
					class="battle-tray-button"
					:disabled="!selectedBattle"
					@click="attack"
				>
					Attack
				</button>
				<button
					class="battle-tray-button"
					:disabled="!selectedBattle || selectedBattle.turn === 0"
					@click="retreat"
				>
					Retreat
				</button>
			</div>
			<div v-else class="battle-tray-buttons">
				<div class="casualty-count">
					Casualties to select: {{ selectedUnits.length || 0 }} /
					{{
						Math.min(
							attackerCasualtyCount,
							maxPossibleCasualtyCount
						)
					}}
				</div>
				<button
					class="battle-tray-button"
					:disabled="
						!selectedBattle ||
						selectedUnits.length !==
							Math.min(
								attackerCasualtyCount,
								maxPossibleCasualtyCount
							)
					"
					@click="selectCasualties"
				>
					Resolve Combat Turn
				</button>
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

			&.win {
				background-color: #41803d;
			}

			&.lose {
				background-color: #843d3d;
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
			width: 100%;

			display: grid;
			gap: 3rem;
			grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
			place-items: center;

			font-size: 1.15rem;

			* {
				min-width: 6rem;
				justify-self: start;

				&:first-child {
					justify-self: end;
				}
			}

			.casualty-count {
				font-size: 1rem;
				padding-right: 1rem;
			}
		}
	}
}
</style>
