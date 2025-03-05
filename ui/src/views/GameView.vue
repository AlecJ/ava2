<script>
import { useSessionStore } from "@/stores/session";
import { useWorldStore } from "@/stores/world";
import BackgroundStars from "@/components/BackgroundStars.vue";
import LandingPopUp from "@/components/LandingPopUp.vue";
import TeamSelectPopUp from "@/components/TeamSelectPopUp.vue";
import CommandTray from "@/components/CommandTray.vue";
import PlayerBoard from "@/components/PlayerBoard.vue";
import ThreeGlobe from "@/components/ThreeGlobe.vue";
import EndTurnButton from "@/components/EndTurnButton.vue";

export default {
	name: "GameView",
	components: {
		BackgroundStars,
		LandingPopUp,
		TeamSelectPopUp,
		CommandTray,
		PlayerBoard,
		ThreeGlobe,
		EndTurnButton,
	},
	data() {
		return {
			sessionStore: null,
			worldStore: null,
			focusedCountry: null,
			isMovingUnits: false,
			selectedTerritoryForMovement: null,
		};
	},
	computed: {
		sessionId() {
			return this.sessionStore?.sessionId;
		},
		status() {
			return this.sessionStore?.status;
		},
		countries() {
			return this.sessionStore?.countries;
		},
		selectedCountries() {
			return this.sessionStore?.players || [];
		},
		playerCountry() {
			return this.sessionStore?.playerCountry;
		},
		isTestMode() {
			return this.sessionStore?.isTesting;
		},
		showLandingPopUp() {
			return this.sessionId === null && !this.isTestMode;
		},
		showTeamSelectPopUp() {
			return this.status === "TEAM_SELECT" && !this.isTestMode;
		},
		isLoading() {
			return this.sessionStore?.isLoading;
		},
		focusedTerritoryData() {
			const territoryData =
				this.worldStore?.getTerritories[this.focusedCountry];

			if (!territoryData) return null;

			return { ...territoryData, name: this.focusedCountry };
		},
		playerTurn() {
			return this.worldStore?.getPlayerTurn;
		},
		currentPhase() {
			return this.worldStore?.getPhase;
		},
	},
	methods: {
		async fetchSession() {
			const sessionId = this.$route.params.sessionId;

			const playerId = this.$route.query.pid;

			if (sessionId) {
				try {
					await this.sessionStore.getSession(sessionId, playerId);
				} catch (error) {
					console.error("Failed to fetch session:", error);
				}
			}
		},
		selectPlayer(countryName) {
			this.sessionStore.selectPlayer(countryName, this.$router);
		},
		createSession() {
			this.sessionStore.createSession(this.$router);
		},
		focusCountry(countryName) {
			this.focusedCountry = countryName;
		},
		captureTerritory(territoryName, team) {
			this.worldStore.captureTerritory(territoryName, team);
		},
		nextPhase() {
			this.worldStore.setNextPhase();
		},
		switchUnitMovementMode(bool) {
			this.isMovingUnits = bool;
		},
		moveUnits(units) {
			// subtract from focused territory

			// add to selected territory
			this.worldStore.moveUnits(
				this.focusedCountry,
				this.selectedTerritoryForMovement,
				units
			);
		},
		selectTerritoryForUnitMovement(territory) {
			// TODO other validation for game rules

			this.selectedTerritoryForMovement = this.areTerritoriesNeighbors(
				this.focusedCountry,
				territory
			);
		},
		// GAME LOGIC HELPER
		areTerritoriesNeighbors(territoryNameA, territoryNameB) {
			// get territory by name
			const territoryA = this.worldStore.getTerritory(territoryNameA);
			const neighbors = territoryA.neighbors;
			return neighbors.find(
				(neighborTerritoryName) =>
					neighborTerritoryName === territoryNameB
			);
		},
	},
	created() {
		this.sessionStore = useSessionStore();
		this.worldStore = useWorldStore();
		this.worldStore.initTerritories();
	},
	mounted() {
		this.fetchSession();
	},
};
</script>

<template>
	<ThreeGlobe
		:sessionId="sessionId"
		:status="status"
		:focusCountry="focusCountry"
		:isMovingUnits="isMovingUnits"
		:selectTerritoryForUnitMovement="selectTerritoryForUnitMovement"
	/>
	<CommandTray
		v-if="!showLandingPopUp && !showTeamSelectPopUp && !isLoading"
		:territoryData="focusedTerritoryData"
		:captureTerritory="captureTerritory"
		:playerTurn="playerTurn"
		:currentPhase="currentPhase"
		:switchUnitMovementMode="switchUnitMovementMode"
		:isMovingUnits="isMovingUnits"
		:moveUnits="moveUnits"
		:selectedTerritoryForMovement="selectedTerritoryForMovement"
	/>

	<PlayerBoard
		v-if="!showLandingPopUp && !showTeamSelectPopUp && !isLoading"
	/>

	<EndTurnButton
		v-if="!showLandingPopUp && !showTeamSelectPopUp && !isLoading"
		:nextPhase="nextPhase"
		:currentPhase="currentPhase"
	/>

	<LandingPopUp
		v-if="showLandingPopUp && !isLoading"
		:createSession="createSession"
	/>
	<TeamSelectPopUp
		v-if="showTeamSelectPopUp && !isLoading"
		:selectPlayer="selectPlayer"
		:selectedCountries="selectedCountries"
		:playerCountry="playerCountry"
	/>
	<BackgroundStars />
</template>

<style scoped></style>
