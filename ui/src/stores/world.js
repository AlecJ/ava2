import { defineStore } from "pinia";
import * as THREE from "three";

import { API } from "@/services/api";
import { useSessionStore } from "@/stores/session";

import tileData from "@/data/territories.json" assert { type: "json" };
import { countries } from "@/data/countries";
import territoryCenters from "@/data/territoryCenters.json";

import japanFlag from "@/assets/flags/japan.png";

let spriteCreationTime = 0;
let spriteAddToWorldTime = 0;

export const useWorldStore = defineStore("world", {
	state: () => ({
		countries: countries,
		territories: {},
		threeGlobeAndCountries: null,
		battles: [],
		sprites: {},
		textureCache: new Map(),
	}),
	actions: {
		initTerritories() {
			this.territories = Object.fromEntries(
				Object.entries(tileData).filter(
					([key, value]) => value.team !== -1
				)
			);
		},
		getCachedTexture(image) {
			if (!this.textureCache.has(image)) {
				const texture = new THREE.TextureLoader().load(image);
				this.textureCache.set(image, texture);
			}
			return this.textureCache.get(image);
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
		getTerritoryCenter(territoryName) {
			const center = territoryCenters[territoryName];

			if (!center) {
				console.error(
					`Center not found for territory: ${territoryName}`
				);
				return null;
			}
			return new THREE.Vector3(center.x, center.y, center.z);
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
		updateTerritorySprites(territory, newSprites) {
			const territoryName = territory.userData.name;

			if (!this.sprites[territoryName]) {
				this.sprites[territoryName] = [];
			}

			// Remove sprites that are no longer needed
			// spritesToRemove.forEach((sprite) => {
			// 	const rawSprite = sprite.__v_raw || sprite;
			// 	this.threeGlobeAndCountries.remove(rawSprite);
			// 	this.sprites[territoryName] = this.sprites[
			// 		territoryName
			// 	].filter((s) => s !== sprite);
			// });

			const center = this.getTerritoryCenter(territoryName);
			center.multiplyScalar(103); // Normalize and scale the center point

			// Create new sprites from spritesToAdd

			newSprites.forEach((image) => {
				// skip the image if it is already in the scene
				if (
					!this.sprites[territoryName].some(
						(sprite) => sprite.userData.name === image
					)
				) {
					const spriteCreationStart = performance.now();

					const texture = this.getCachedTexture(image);
					const material = new THREE.SpriteMaterial({
						map: texture,
					});

					const sprite = new THREE.Sprite(material);

					// add userdata type
					sprite.userData = {
						name: image,
					};

					this.sprites[territoryName].push(sprite);

					const spriteCreationEnd = performance.now();
					spriteCreationTime +=
						spriteCreationEnd - spriteCreationStart;

					this.threeGlobeAndCountries.add(sprite);
				}
			});

			const spritesToDraw = this.sprites[territoryName];

			// Loop through and position the active sprites
			spritesToDraw.forEach((sprite, index) => {
				// Calculate the offset angle for each sprite
				const angle =
					((index - (spritesToDraw.length - 1) / 2) * Math.PI) / 36; // Adjust spacing with angle

				// Create a rotation matrix to rotate around the sphere's vertical axis
				const rotationMatrix = new THREE.Matrix4().makeRotationY(angle);

				// Apply the rotation to the center point to calculate the sprite position
				const offset = center.clone().applyMatrix4(rotationMatrix);

				// Set the sprite position
				sprite.position.copy(offset);
				sprite.scale.set(5, 5, 1);
			});
		},
		updateGameWorld(gameState) {
			const newTerritories = gameState?.territories || this.territories;

			const spriteAddStartTime = performance.now();

			for (let [territoryName, territory] of Object.entries(
				newTerritories
			)) {
				if (!this.territories[territoryName]) {
					console.warn(
						`Territory ${territoryName} not found in the store.`
					);
					continue;
				}
				this.territories[territoryName].team = territory.team;
				this.territories[territoryName].units = territory.units;
				this.territories[territoryName].has_factory =
					territory.has_factory;

				const isOwnedByThisPlayer =
					territory.team == this.getPlayerTeamNum;
				const isMobilizationPhase = this.getCurrentPhase === 4;
				const shouldDrawFactory =
					territory.has_factory &&
					isOwnedByThisPlayer &&
					isMobilizationPhase;

				const shouldDrawUnits = true;

				// track sprites to add
				const newSprites = [];

				// Get the mesh for the territory
				const territoryMesh = this.getTerritoryMesh(territoryName);
				if (territoryMesh) {
					const teamColor = this.getCountryColor(territory.team);

					// Add sprites to industrial complexes
					if (shouldDrawFactory) {
						// TODO need factory sprite
						newSprites.push(japanFlag);
					}

					// Add sprites for units
					if (shouldDrawUnits) {
						if (territory.units.length) {
							newSprites.push(japanFlag);
						}
					}

					// Add and reposition sprites
					this.updateTerritorySprites(territoryMesh, newSprites);

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

			const spriteAddEndTime = performance.now();
			spriteAddToWorldTime += spriteAddEndTime - spriteAddStartTime;

			if (gameState?.battles) {
				this.battles = gameState.battles;
			}

			console.log(
				`Total time for sprite creation: ${spriteCreationTime.toFixed(2)}ms`
			);

			console.log(
				`Total time to add sprite to world: ${spriteAddToWorldTime.toFixed(2)}ms`
			);
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
				this.updateGameWorld();
			} catch (error) {
				console.error("API Error:", error);
				// console.error("API Error:", error.response.data.status);
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
				sessionStore.setSession(response.data.session);
				this.updateGameWorld(response.data.game_state);
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
		getPlayerTeamNum() {
			const sessionStore = useSessionStore();
			return sessionStore.getPlayerTeamNum;
		},
		getCurrentPhase() {
			const sessionStore = useSessionStore();
			return sessionStore.getPhaseNum;
		},
		getBattles: (state) => state.battles,
		getSprites: (state) => state.sprites,
	},
});
