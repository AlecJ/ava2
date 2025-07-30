<script>
import { useSessionStore } from "@/stores/session";
import { useWorldStore } from "@/stores/world";
import { unitIcons } from "@/data/unitIcons";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import UnitBox from "@/components/UnitBox.vue";

export default {
	components: {
		LoadingSpinner,
		UnitBox,
	},
	props: {
		isLoading: {
			type: Boolean,
			required: false,
		},
		player: {
			type: Object,
			required: true,
		},
		setIsSelectingTerritory: {
			type: Function,
			required: true,
		},
		selectedTerritory: {
			type: String,
			required: false,
		},
	},
	data() {
		return {
			sessionStore: null,
			worldStore: null,
			playerUnits: [],
		};
	},
	watch: {
		player: {
			handler(newPlayer) {
				if (newPlayer && newPlayer.mobilization_units) {
					this.playerUnits = [...this.player.mobilization_units].map(
						(unit) => ({
							unit_type: unit,
							team: newPlayer.team,
						})
					);
				}
			},
			immediate: true,
			deep: true,
		},
		mobilizationUnits: {
			handler(newMobilizationUnits) {
				if (!newMobilizationUnits.length) {
					this.setIsSelectingTerritory(false);
				}
			},
			immediate: true,
		},
	},
	computed: {
		selectedUnits() {
			return this.playerUnits.filter((unit) => unit.selected);
		},
		mobilizationUnits() {
			return this.player.mobilization_units;
		},
	},
	methods: {
		getUnitIconSrc(unit) {
			const unitIcon = unitIcons.find((u) => u.name === unit);

			return unitIcon ? unitIcon.unitIcon : "";
		},
		placeUnits() {
			this.worldStore.mobilizeUnits(
				this.selectedUnits,
				this.selectedTerritory
			);
		},
	},
	created() {
		this.sessionStore = useSessionStore();
		this.worldStore = useWorldStore();
	},
	mounted() {
		if (this.mobilizationUnits.length) this.setIsSelectingTerritory(true);
	},
	unmounted() {
		this.setIsSelectingTerritory(false);
	},
};
</script>

<template>
	<div class="mobilization-tray">
		<div class="mobilization-tray-title">Mobilize Units</div>
		<LoadingSpinner v-if="isLoading" />
		<div class="mobilization-tray-content" v-else>
			<div class="mobilization-tray-desc" v-if="mobilizationUnits.length">
				Place your purchased units on territories you control with an
				industrial complex. Sea units are placed in a sea zone adjacent
				to an industrial complex.
			</div>
			<div class="mobilization-tray-desc" v-else>
				You have no mobilization forces to place.<br />You can end your
				turn.
			</div>
			<UnitBox
				class="mobilization-tray-units"
				v-if="mobilizationUnits.length"
				:units="playerUnits"
			>
			</UnitBox>
			<div v-if="mobilizationUnits.length" class="selected-territory">
				Selected territory:
				{{ selectedTerritory || "None" }}
			</div>
			<button
				v-if="mobilizationUnits.length"
				:disabled="!selectedTerritory"
				@click="placeUnits"
				class="place-units-button"
			>
				Place Units
			</button>
		</div>
	</div>
</template>

<style scoped lang="scss">
.mobilization-tray {
	width: 24rem;
	height: 100%;

	.mobilization-tray-title {
		font-size: 1.5rem;
		font-weight: bold;
		text-align: center;
	}

	.mobilization-tray-content {
		height: 90%;
		display: grid;
		align-items: center;
		justify-items: center;

		.mobilization-tray-desc {
			font-size: 1rem;
			text-align: center;
		}

		.mobilization-tray-units {
		}

		.selected-territory {
			font-size: 1.2rem;
			text-align: center;
		}

		.place-units-button {
			width: 10rem;
		}
	}
}
</style>
