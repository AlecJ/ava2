import { defineStore } from "pinia";
import * as THREE from "three";

import { API } from "@/services/api";
import { useSessionStore } from "@/stores/session";
import { useToastStore } from "@/stores/toast";

import tileData from "@/data/territories.json" assert { type: "json" };
import { countries } from "@/data/countries";
import territoryCenters from "@/data/territoryCenters.json";
import { PHASES } from "@/constants/phases";

import japanFlag from "@/assets/flags/japan.png";
import germanyFlag from "@/assets/flags/germany.png";
import sovietFlag from "@/assets/flags/soviet-union.png";
import ukFlag from "@/assets/flags/united-kingdom.png";
import usFlag from "@/assets/flags/united-states-of-america.png";

export const useWorldStore = defineStore("world", {
	state: () => ({
		countries: countries,
		territories: {},
		threeGlobeAndCountries: null,
		battles: [],
		sprites: {},
		textureCache: new Map(),
		materialCache: new Map(),
		isGeneratingSprites: false,
		showFactorySprites: false,
	}),
	actions: {
		initTerritories() {
			this.territories = Object.fromEntries(
				Object.entries(tileData).filter(
					([key, value]) => value.team !== -1
				)
			);
		},
		async initializeAllSprites() {
			if (!this.threeGlobeAndCountries) {
				console.warn("Three globe not ready for sprite initialization");
				return;
			}

			// Create sprites for all territories
			const territoryEntries = Object.entries(this.territories);
			const batchSize = 20; // Process territories in batches

			this.isGeneratingSprites = true;

			for (let i = 0; i < territoryEntries.length; i += batchSize) {
				const batch = territoryEntries.slice(i, i + batchSize);
				const territoryNames = batch.map(([name]) => name);
				const territoryData = Object.fromEntries(batch);

				await this.processTerritoryBatch(territoryNames, territoryData);

				// Yield control every batch to prevent blocking
				if (i + batchSize < territoryEntries.length) {
					await new Promise((resolve) => setTimeout(resolve, 0));
				}
			}

			this.isGeneratingSprites = false;

			// Apply initial visibility settings
			this.toggleSpriteVisibility();
		},
		getCachedTexture(image) {
			if (!this.textureCache.has(image)) {
				const texture = new THREE.TextureLoader().load(image);
				this.textureCache.set(image, texture);
			}
			return this.textureCache.get(image);
		},
		getCachedMaterial(image) {
			if (!this.materialCache.has(image)) {
				const texture = this.getCachedTexture(image);
				const material = new THREE.SpriteMaterial({ map: texture });
				this.materialCache.set(image, material);
			}
			return this.materialCache.get(image);
		},
		// TODO use this everywhere
		getCountryColor(team) {
			if (!this.countries) return null;

			return this.countries[team].color;
		},
		getCountryFlag(team) {
			const flagMap = {
				0: sovietFlag,
				1: germanyFlag,
				2: ukFlag,
				3: japanFlag,
				4: usFlag,
			};
			return flagMap[team] || japanFlag;
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
		setShowFactorySprites(show) {
			this.showFactorySprites = show;
			this.toggleSpriteVisibility();
		},
		toggleSpriteVisibility() {
			// Iterate through all territories and toggle sprite visibility
			Object.keys(this.sprites).forEach((territoryName) => {
				const territory = this.territories[territoryName];
				if (!territory) return;

				const isOwnedByThisPlayer =
					territory.team === this.getPlayerTeamNum;
				const isMobilizationPhase =
					this.getCurrentPhase === PHASES.MOBILIZATION;

				this.sprites[territoryName].forEach((sprite) => {
					const isFactorySprite = sprite.userData.type === "factory";
					const isUnitSprite = sprite.userData.type === "unit";

					if (this.showFactorySprites) {
						// Show factory sprites, hide unit sprites
						sprite.visible = isFactorySprite && isOwnedByThisPlayer;
					} else {
						// Show unit sprites, hide factory sprites
						sprite.visible = isUnitSprite;
					}
				});
			});
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

			// Create a Set for faster lookups
			const newSpriteKeys = new Set(
				newSprites.map((sprite) => `${sprite.image}_${sprite.type}`)
			);

			// Create a Set of existing sprite keys for faster comparison
			const existingKeys = new Set(
				this.sprites[territoryName].map(
					(sprite) =>
						`${sprite.userData.name}_${sprite.userData.type}`
				)
			);

			// Remove sprites that are no longer needed
			const spritesToRemove = this.sprites[territoryName].filter(
				(sprite) => {
					const key = `${sprite.userData.name}_${sprite.userData.type}`;
					return !newSpriteKeys.has(key);
				}
			);

			spritesToRemove.forEach((sprite) => {
				const rawSprite = sprite.__v_raw || sprite;
				this.threeGlobeAndCountries.remove(rawSprite);
			});

			// Update sprites array by removing old sprites
			this.sprites[territoryName] = this.sprites[territoryName].filter(
				(sprite) => {
					const key = `${sprite.userData.name}_${sprite.userData.type}`;
					return newSpriteKeys.has(key);
				}
			);

			// Get territory center once
			const center = this.getTerritoryCenter(territoryName);
			if (!center) return; // Early exit if no center found
			center.multiplyScalar(103); // Normalize and scale the center point

			// Create new sprites only for missing ones
			newSprites.forEach((spriteData) => {
				const spriteKey = `${spriteData.image}_${spriteData.type}`;

				// Skip if sprite already exists
				if (existingKeys.has(spriteKey)) return;

				const material = this.getCachedMaterial(spriteData.image);
				const sprite = new THREE.Sprite(material);

				// Set sprite properties
				sprite.userData = {
					name: spriteData.image,
					type: spriteData.type,
				};
				sprite.raycast = () => {}; // Disable raycasting for sprites

				// Set initial visibility based on current mode
				sprite.visible = this.showFactorySprites
					? spriteData.type === "factory"
					: spriteData.type === "unit";

				this.sprites[territoryName].push(sprite);
				this.threeGlobeAndCountries.add(sprite);
			});

			// Position all sprites for this territory
			this.positionTerritorySprites(territoryName, center);
		},
		positionTerritorySprites(territoryName, center) {
			const spritesToDraw = this.sprites[territoryName];
			if (!spritesToDraw || spritesToDraw.length === 0) return;

			// Pre-calculate some values for performance
			const spriteCount = spritesToDraw.length;
			const halfCount = (spriteCount - 1) / 2;
			const angleStep = Math.PI / 30;

			// Loop through and position the sprites
			spritesToDraw.forEach((sprite, index) => {
				// Calculate the offset angle for each sprite
				const angle = (index - halfCount) * angleStep;

				// Create a rotation matrix to rotate around the sphere's vertical axis
				const rotationMatrix = new THREE.Matrix4().makeRotationY(angle);

				// Apply the rotation to the center point to calculate the sprite position
				const offset = center.clone().applyMatrix4(rotationMatrix);

				// Set the sprite position and scale
				sprite.position.copy(offset);
				sprite.scale.set(5, 5, 1);
			});
		},
		territoryHasChanges(currentTerritory, newTerritory) {
			if (!currentTerritory || !newTerritory) return true;

			// Check team change
			if (currentTerritory.team !== newTerritory.team) return true;

			// Check factory status change
			if (currentTerritory.has_factory !== newTerritory.has_factory)
				return true;

			// Check units changes
			if (!currentTerritory.units || !newTerritory.units) return true;
			if (currentTerritory.units.length !== newTerritory.units.length)
				return true;

			// Quick check for unit team composition changes
			const currentTeams = new Set(
				currentTerritory.units.map((unit) => unit.team)
			);
			const newTeams = new Set(
				newTerritory.units.map((unit) => unit.team)
			);

			if (currentTeams.size !== newTeams.size) return true;
			for (const team of currentTeams) {
				if (!newTeams.has(team)) return true;
			}

			return false;
		},
		async processTerritoryBatch(territoryNames, newTerritories) {
			for (const territoryName of territoryNames) {
				const territory = newTerritories[territoryName];
				if (!territory) continue;

				const newSprites = [];

				// Always create factory sprites if territory has a factory
				if (territory.has_factory) {
					newSprites.push({
						image: this.getCountryFlag(territory.team),
						type: "factory",
					});
				}

				// Always create unit sprites if territory has units
				if (territory.units && territory.units.length > 0) {
					const teams = [
						...new Set(territory.units.map((unit) => unit.team)),
					];
					teams.forEach((team) => {
						newSprites.push({
							image: this.getCountryFlag(team),
							type: "unit",
						});
					});
				}

				// Update territory mesh and sprites
				const territoryMesh = this.getTerritoryMesh(territoryName);
				if (territoryMesh) {
					// Update sprites
					this.updateTerritorySprites(territoryMesh, newSprites);

					// Update mesh color
					const teamColor = this.getCountryColor(territory.team);
					if (teamColor) {
						territoryMesh.material.color.set(teamColor);
					}
				}
			}
		},
		async updateGameWorld(gameState) {
			const newTerritories = gameState?.territories || this.territories;

			// First pass: identify changed territories without expensive operations
			const changedTerritories = [];
			let changeCount = 0;

			for (const [territoryName, newTerritory] of Object.entries(
				newTerritories
			)) {
				if (!this.territories[territoryName]) {
					console.warn(
						`Territory ${territoryName} not found in the store.`
					);
					continue;
				}

				if (
					this.territoryHasChanges(
						this.territories[territoryName],
						newTerritory
					)
				) {
					changedTerritories.push(territoryName);
					changeCount++;
				}
			}

			// Early exit if no changes detected
			if (changedTerritories.length === 0) {
				if (gameState?.battles) {
					this.battles = gameState.battles;
				}
				return;
			}

			// Update all territory data first (fast operation)
			for (const [territoryName, newTerritory] of Object.entries(
				newTerritories
			)) {
				if (this.territories[territoryName]) {
					this.territories[territoryName].team = newTerritory.team;
					this.territories[territoryName].units = newTerritory.units;
					this.territories[territoryName].has_factory =
						newTerritory.has_factory;
				}
			}

			// Only process sprites for changed territories with batching
			if (changedTerritories.length > 0) {
				this.isGeneratingSprites = true;

				// Process territories in batches to avoid blocking the main thread
				const batchSize = Math.min(10, changedTerritories.length);
				const batches = [];
				for (let i = 0; i < changedTerritories.length; i += batchSize) {
					batches.push(changedTerritories.slice(i, i + batchSize));
				}

				for (const batch of batches) {
					// Process batch
					await this.processTerritoryBatch(batch, newTerritories);

					// Yield control to prevent blocking UI (only if there are more batches)
					if (batches.length > 1) {
						await new Promise((resolve) => setTimeout(resolve, 0));
					}
				}

				this.isGeneratingSprites = false;
			}

			// Update battles if provided
			if (gameState?.battles) {
				this.battles = gameState.battles;
			}

			// Apply visibility settings once at the end
			this.toggleSpriteVisibility();
		},
		handleApiError(error, defaultMessage = "An error occurred") {
			const toastStore = useToastStore();
			let errorMessage = defaultMessage;

			if (error?.response?.data?.status) {
				errorMessage = error.response.data.status;
			} else if (error?.response?.data?.message) {
				errorMessage = error.response.data.message;
			} else if (error?.message) {
				errorMessage = error.message;
			}

			console.error("API Error:", errorMessage);
			toastStore.error(errorMessage);
		},
		// Test method for toast notifications (can be removed later)
		testToast(type = "error", message = "Test notification") {
			const toastStore = useToastStore();
			toastStore[type](message);
		},
		async getWorldData() {
			// this should be triggered once the game starts and after any updates
			const sessionStore = useSessionStore();
			sessionStore.setIsLoading(true);
			// this.isLoading = true;

			try {
				const response = await API.get(`/game/${this.getSessionId}`);

				await this.updateGameWorld(response.data.game_state);

				// Initialize all sprites if this is the first load
				if (Object.keys(this.sprites).length === 0) {
					await this.initializeAllSprites();
				}
			} catch (error) {
				this.handleApiError(error, "Failed to load game data");
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

				sessionStore.setSession(response.data.session);

				// Show success message
				const toastStore = useToastStore();
				toastStore.success(
					`Successfully purchased ${unitType.toLowerCase()}`
				);
			} catch (error) {
				this.handleApiError(error, "Failed to purchase unit");
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

				sessionStore.setSession(response.data.session);
				await this.updateGameWorld(response.data.game_state);

				// Show success message
				const toastStore = useToastStore();
				toastStore.success(
					`Successfully mobilized ${units.length} unit(s) to ${selectedTerritory}`
				);
			} catch (error) {
				this.handleApiError(error, "Failed to mobilize units");
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

				await this.updateGameWorld(response.data.game_state);
			} catch (error) {
				this.handleApiError(error, "Failed to move units");
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

				await this.updateGameWorld(response.data.game_state);
			} catch (error) {
				this.handleApiError(error, "Failed to load transport");
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

				await this.updateGameWorld(response.data.game_state);
			} catch (error) {
				this.handleApiError(error, "Failed to unload transport");
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

				await this.updateGameWorld(response.data.game_state);
			} catch (error) {
				this.handleApiError(error, "Failed to attack");
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

				await this.updateGameWorld(response.data.game_state);
			} catch (error) {
				this.handleApiError(error, "Failed to retreat");
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

				await this.updateGameWorld(response.data.game_state);
			} catch (error) {
				this.handleApiError(error, "Failed to select casualties");
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

				await this.updateGameWorld(response.data.game_state);
			} catch (error) {
				this.handleApiError(error, "Failed to undo phase");
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

				sessionStore.setSession(response.data.session);
				await this.updateGameWorld();
			} catch (error) {
				this.handleApiError(error, "Failed to end phase");
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

				sessionStore.setSession(response.data.session);
				await this.updateGameWorld(response.data.game_state);
			} catch (error) {
				this.handleApiError(error, "Failed to end turn");
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
		getIsGeneratingSprites: (state) => state.isGeneratingSprites,
		getShowFactorySprites: (state) => state.showFactorySprites,
	},
});
