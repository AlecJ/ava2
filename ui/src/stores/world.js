import { defineStore } from "pinia";

import tileData from "@/data/territories.json" assert { type: "json" };

export const useWorldStore = defineStore("world", {
	state: () => ({
		countries: {},
	}),
	actions: {
		initCountries() {
			this.countries = Object.fromEntries(
				Object.entries(tileData).filter(
					([key, value]) => value.team !== -1 && !value.is_ocean
				)
			);
		},
		captureTerritory(territory, team) {
			this.countries[territory].team = team;
		},
	},
	getters: {
		getCountries: (state) => state.countries,
	},
});
