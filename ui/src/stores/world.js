import { defineStore } from "pinia";

import tileData from "@/data/territories.json" assert { type: "json" };
import { countries } from "@/data/countries";

export const useWorldStore = defineStore("world", {
	state: () => ({
		countries: countries,
		territories: {},
		threeGlobeAndCountries: null,
		playerTurn: 0,
		currentPhase: 1, // TODO set to 0
	}),
	actions: {
		initTerritories() {
			this.territories = Object.fromEntries(
				Object.entries(tileData).filter(
					([key, value]) => value.team !== -1
				)
			);
		},
		getCountryColor(team) {
			if (!this.countries) return null;

			return this.countries[team].color;
		},
		setThreeGlobeAndCountries(threeGlobeAndCountries) {
			this.threeGlobeAndCountries = threeGlobeAndCountries;
		},
		getTerritory(territoryName) {
			return this.territories[territoryName];
		},
		getTerritoryMesh(territoryName) {
			if (!this.threeGlobeAndCountries) return null;

			return this.threeGlobeAndCountries.children[1].children[0].children.find(
				(territoryMesh) => territoryMesh.userData.name === territoryName
			);
		},
		moveUnits(territoryNameA, territoryNameB, units) {
			// send to backend, get new world
			const territoryA = this.getTerritory(territoryNameA);
			const territoryB = this.getTerritory(territoryNameB);
			console.log(territoryA);
			console.log(territoryB);
			console.log(units);
		},
		captureTerritory(territoryName, team) {
			const territoryMesh = this.getTerritoryMesh(territoryName);
			if (!territoryMesh) {
				console.log(territoryName + " not found.");
				return;
			}
			territoryMesh.material.color.setHex(this.getCountryColor(team));
			this.territories[territoryName].team = team;
		},
		setNextPhase() {
			this.currentPhase++;
		},
	},
	getters: {
		getTerritories: (state) => state.territories,
		getGlobeAndCountries: (state) => state.threeGlobeAndCountries,
		getPlayerTurn: (state) => state.playerTurn,
		getPhase: (state) => state.currentPhase,
	},
});
