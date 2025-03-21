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
		updateGameWorld(gameState) {
			for (let [territoryName, territory] of Object.entries(
				gameState.territories
			)) {
				if (!this.territories[territoryName]) {
					console.warn(
						`Territory ${territoryName} not found in the store.`
					);
					continue;
				}
				// console.log(territoryName, territory);
				this.territories[territoryName].team = territory.team;
				this.territories[territoryName].units = territory.units;
				this.territories[territoryName].has_factory =
					territory.has_factory;
			}
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

				console.log("API Response:", response.data); // Debugging log

				this.updateGameWorld(response.data.game_state);
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
					`/game/${this.getSessionId}/moveunits`,
					data
				);
				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async endTurn() {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const response = await API.post(
					`/game/${this.getSessionId}/endturn`
				);
				console.log("API Response:", response.data); // Debugging log

				this.updateGameWorld(response.data.game_state);
				sessionStore.setPlayers(response.data.players);
			} catch (error) {
				console.error("API Error:", error);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		// captureTerritory(territoryName, team) {
		// 	const territoryMesh = this.getTerritoryMesh(territoryName);
		// 	if (!territoryMesh) {
		// 		console.log(territoryName + " not found.");
		// 		return;
		// 	}
		// 	territoryMesh.material.color.setHex(this.getCountryColor(team));
		// 	this.territories[territoryName].team = team;
		// },
		// setNextPhase() {
		// 	this.currentPhase++;
		// },
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
