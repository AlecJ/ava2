import { defineStore } from "pinia";
import { API } from "@/services/api";

import { useSessionStore } from "@/stores/session";

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
		// This is used to reset the territories units before updating them
		resetTerritoryUnits() {
			Object.values(this.territories).forEach((territory) => {
				territory.units = [];
			});
		},
		updateGameWorld(units) {
			// reset territories units
			this.resetTerritoryUnits();

			// set territories units
			units.forEach((unit) => {
				this.territories[unit.territory].units.push(unit);
			});
		},
		async getWorldData() {
			// this should be triggered once the game starts and after any updates
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);
			// this.isLoading = true;

			try {
				// console.log(
				// 	"Fetching game state from API:",
				// 	`/game/${this.getSessionId}`
				// );

				const response = await API.get(`/game/${this.getSessionId}`);

				// console.log("API Response:", response.data); // Debugging log

				this.updateGameWorld(response.data.game_state.units);
			} catch (error) {
				console.error("API Error:", error);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async moveUnits(territoryNameA, territoryNameB, units) {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const data = {
					territoryA: territoryNameA,
					territoryB: territoryNameB,
					units: units,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/moveunits?pid=${this.getPlayerId}`,
					data
				);
				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state.units);
			} catch (error) {
				console.error("API Error:", error);
			} finally {
				sessionStore.setIsLoading(false);
			}
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
		getSessionId() {
			const sessionStore = useSessionStore();
			return sessionStore.sessionId;
		},
		getPlayerId() {
			const sessionStore = useSessionStore();
			return sessionStore.playerId;
		},
	},
});
