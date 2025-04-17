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
		battles: [],
	}),
	actions: {
		initTerritories() {
			this.territories = Object.fromEntries(
				Object.entries(tileData).filter(
					([key, value]) => value.team !== -1
				)
			);
		},
		// TODO use this everywhere
		getCountryColor(team) {
			if (!this.countries) return null;

			return this.countries[team].color;
		},
		getNeighboringTerritories(territoryName) {
			const territory = this.territories[territoryName];
			const neighborNames = territory["neighbors"];

			return neighborNames.map((tName) => {
				return { ...this.territories[tName], name: tName };
			});
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

				// Get the mesh for the territory
				const territoryMesh = this.getTerritoryMesh(territoryName);
				if (territoryMesh) {
					// Get the color for the controlling team
					const teamColor = this.getCountryColor(territory.team);

					// Update the mesh color
					if (teamColor) {
						territoryMesh.material.color.set(teamColor);
					} else {
						console.warn(
							`No color found for team ${territory.team}`
						);
					}
				}
			}

			this.battles = gameState.battles;
		},
		async getWorldData() {
			// this should be triggered once the game starts and after any updates
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);
			// this.isLoading = true;

			try {
				const response = await API.get(`/game/${this.getSessionId}`);

				console.log("API Response:", response.data); // Debugging log

				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async purchaseUnit(unitType) {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;
				const data = {
					unitType: unitType,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/purchaseunit?pid=${playerId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log
				sessionStore.setSession(response.data.session);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async mobilizeUnits(units, selectedTerritory) {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;
				const data = {
					units: units,
					selectedTerritory: selectedTerritory,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/mobilizeunits?pid=${playerId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log
				sessionStore.setSession(response.data.session);
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async moveUnits(territoryNameA, territoryNameB, units) {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;
				const data = {
					territoryA: territoryNameA,
					territoryB: territoryNameB,
					units: units,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/moveunits?pid=${playerId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async loadTransport(territoryName, transport, units) {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;
				const data = {
					territoryName: territoryName,
					transport: transport,
					units: units,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/loadtransport?pid=${playerId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async unloadTransport(seaTerritory, selectedTerritory, transport) {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;
				const data = {
					seaTerritory,
					selectedTerritory,
					transport,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/unloadtransport?pid=${playerId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async combatAttack(selectedTerritory) {
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;
				const data = {
					selectedTerritory,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/attack?pid=${playerId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async combatRetreat(selectedTerritory) {
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;
				const data = {
					selectedTerritory,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/retreat?pid=${playerId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async combatSelectCasualties(selectedTerritory, selectedUnits) {
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;
				const data = {
					selectedTerritory,
					selectedUnits,
				};

				const response = await API.post(
					`/game/${this.getSessionId}/casualties?pid=${playerId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error);
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async undoPhase() {
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;

				const response = await API.post(
					`/game/${this.getSessionId}/undophase?pid=${playerId}`
				);

				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async endPhase() {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;

				const response = await API.post(
					`/game/${this.getSessionId}/endphase?pid=${playerId}`
				);

				console.log("API Response:", response.data); // Debugging log
				sessionStore.setSession(response.data.session);
			} catch (error) {
				console.error("API Error:", error.response.data.status);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
		async endTurn() {
			// also send player ID
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);

			try {
				const playerId = sessionStore.getPlayerId;

				const response = await API.post(
					`/game/${this.getSessionId}/endturn?pid=${playerId}`
				);

				console.log("API Response:", response.data); // Debugging log
				this.updateGameWorld(response.data.game_state);
				sessionStore.setSession(response.data.session);
			} catch (error) {
				console.error("API Error:", error);
			} finally {
				sessionStore.setIsLoading(false);
			}
		},
	},
	getters: {
		getTerritories: (state) => state.territories,
		getGlobeAndCountries: (state) => state.threeGlobeAndCountries,
		getSessionId() {
			const sessionStore = useSessionStore();
			return sessionStore.sessionId;
		},
		getPlayerId() {
			const sessionStore = useSessionStore();
			return sessionStore.playerId;
		},
		getBattles: (state) => state.battles,
	},
});
