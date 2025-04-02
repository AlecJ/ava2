<script>
import { useWorldStore } from "@/stores/world";
import { countries } from "@/data/countries";
import { unitIcons } from "@/data/unitIcons";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import UnitBox from "@/components/UnitBox.vue";

export default {
	components: {
		LoadingSpinner,
		UnitBox,
	},
	props: {
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
							team: this.playerTeamNum,
						})
					);
				}
			},
			immediate: true,
			deep: true,
		},
	},
	computed: {
		playerTeamNum() {
			return countries.findIndex(
				(country) => country.name === this.player.country
			);
		},
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
		this.worldStore = useWorldStore();
	},
	mounted() {
		this.setIsSelectingTerritory(true);
	},
	unmounted() {
		this.setIsSelectingTerritory(false);
	},
};
</script>

<template>
	<div class="mobilization-tray">
		<div class="mobilization-tray-title">Mobilize Units</div>
		<div class="mobilization-tray-desc" v-if="mobilizationUnits.length">
			Place your purchased units on territories you control with an
			industrial complex. Sea units are placed in a sea zone adjacent to
			an industrial complex.
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
		<div v-if="mobilizationUnits.length">
			Selected territory:
			{{ selectedTerritory || "None" }}
		</div>
		<button v-if="mobilizationUnits.length" @click="placeUnits">
			Place Units
		</button>
	</div>
</template>

<style scoped lang="scss">
.mobilization-tray {
	width: 24rem;
	height: 100%;
	justify-self: start;

	display: grid;
	grid-template-rows: 1fr 1fr 7fr 1fr 1fr;

	.unit-board {
		width: 100%;

		display: grid;
		grid-template-columns: repeat(auto-fill, 150px);

		.purchase-unit-button {
			width: 150px;
			height: 200px;

			.unit-icon {
				width: 3rem;
				height: auto;
			}
		}
	}
}
</style>
