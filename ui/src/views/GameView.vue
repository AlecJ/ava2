<script>
import { useSessionStore } from "@/stores/session";
import { useWorldStore } from "@/stores/world";
import { countries } from "@/data/countries";
import BackgroundStars from "@/components/BackgroundStars.vue";
import LandingPopUp from "@/components/LandingPopUp.vue";
import TeamSelectPopUp from "@/components/TeamSelectPopUp.vue";
import DefaultTray from "@/components/DefaultTray.vue";
import PlayerBoard from "@/components/PlayerBoard.vue";
import ThreeGlobe from "@/components/ThreeGlobe.vue";
import UndoTurnButton from "@/components/UndoTurnButton.vue";
import EndTurnButton from "@/components/EndTurnButton.vue";
import PurchaseUnitsButton from "@/components/PurchaseUnitsButton.vue";
import PlaceMobilizationUnitsButton from "@/components/PlaceMobilizationUnitsButton.vue";

export default {
	name: "GameView",
	components: {
		BackgroundStars,
		LandingPopUp,
		TeamSelectPopUp,
		DefaultTray,
		PlayerBoard,
		ThreeGlobe,
		UndoTurnButton,
		EndTurnButton,
		PurchaseUnitsButton,
		PlaceMobilizationUnitsButton,
	},
	data() {
		return {
			sessionStore: null,
			worldStore: null,
			focusedCountry: null,
			isSelectingTerritory: false,
			isPurchasingUnits: false,
			isPlacingMobilizationUnits: false,
			selectedTerritoryForMovement: null,
			selectedTerritory: null,
		};
	},
	computed: {
		sessionId() {
			return this.sessionStore?.sessionId;
		},
		status() {
			return this.sessionStore?.status;
		},
		players() {
			return this.sessionStore?.getPlayers;
		},
		currentTurnNum() {
			return this.sessionStore?.getTurnNum;
		},
		currentPhaseNum() {
			return this.sessionStore?.getPhaseNum;
		},
		selectedCountries() {
			// TODO remove with above
			return this.sessionStore?.players || [];
		},
		player() {
			return this.sessionStore?.getPlayer;
		},
		playerCountry() {
			// TODO replace with above
			return this.sessionStore?.playerCountry;
		},
		playerTeamNum() {
			return countries.findIndex(
				(country) => country.name === this.player.country
			);
		},
		isThisPlayersTurn() {
			return this.currentTurnNum % 5 === this.playerTeamNum;
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
			return this.sessionStore?.getIsLoading;
		},
		focusedTerritoryData() {
			const territoryData =
				this.worldStore?.getTerritories[this.focusedCountry];

			if (!territoryData) return null;

			return { ...territoryData, name: this.focusedCountry };
		},
		neighboringTerritoriesData() {
			if (!this.focusedTerritoryData) return [];

			return this.worldStore?.getNeighboringTerritories(
				this.focusedCountry
			);
		},
		hasMobilizeUnitsRemaining() {
			return this.player.mobilization_units.length;
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
		purchaseUnit(unitType) {
			this.worldStore.purchaseUnit(unitType);
		},
		setIsSelectingTerritory(bool) {
			this.isSelectingTerritory = bool;

			if (this.isSelectingTerritory) this.selectedTerritory = null;
		},
		selectTerritory(territory) {
			this.selectedTerritory = territory;

			// TODO other validation for game rules
			// this.selectedTerritoryForMovement = territory; // ocean_territories do not have neighbors yet
			// this.selectedTerritoryForMovement = this.areTerritoriesNeighbors(
			// 	this.focusedCountry,
			// 	territory
			// );
		},
		areTerritoriesNeighbors(territoryNameA, territoryNameB) {
			const territoryA = this.worldStore.getTerritory(territoryNameA);
			const neighbors = territoryA.neighbors;
			return neighbors.find(
				(neighborTerritoryName) =>
					neighborTerritoryName === territoryNameB
			);
		},
		setPurchasingUnits(bool) {
			this.isPurchasingUnits = bool;
		},
		setPlacingMobilizationUnits(bool) {
			this.isPlacingMobilizationUnits = bool;
		},
		endPhase() {
			this.setPlacingMobilizationUnits(false);
			this.setPurchasingUnits(false);
			this.worldStore.endPhase();
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
	<!-- needs refactor, merge isMoving into isSelecting -->
	<ThreeGlobe
		:sessionId="sessionId"
		:status="status"
		:focusCountry="focusCountry"
		:isSelectingTerritory="isSelectingTerritory"
		:selectTerritory="selectTerritory"
	/>

	<DefaultTray
		v-if="!showLandingPopUp && !showTeamSelectPopUp"
		:isLoading="isLoading"
		:player="player"
		:territoryData="focusedTerritoryData"
		:neighboringTerritoriesData="neighboringTerritoriesData"
		:currentTurnNum="currentTurnNum"
		:currentPhaseNum="currentPhaseNum"
		:isPurchasingUnits="isPurchasingUnits"
		:purchaseUnit="purchaseUnit"
		:isPlacingMobilizationUnits="isPlacingMobilizationUnits"
		:placeUnit="() => {}"
		:setIsSelectingTerritory="setIsSelectingTerritory"
		:selectedTerritory="selectedTerritory"
	/>

	<PlayerBoard
		v-if="!showLandingPopUp && !showTeamSelectPopUp"
		:players="players"
		:currentTurnNum="currentTurnNum"
	/>

	<PurchaseUnitsButton
		v-if="!showLandingPopUp && !showTeamSelectPopUp"
		:active="currentPhaseNum === 0 && isThisPlayersTurn"
		:setPurchasingUnits="setPurchasingUnits"
		:isPurchasingUnits="isPurchasingUnits"
	/>

	<PlaceMobilizationUnitsButton
		v-if="!showLandingPopUp && !showTeamSelectPopUp"
		:active="currentPhaseNum === 4 && isThisPlayersTurn"
		:setPlacingMobilizationUnits="setPlacingMobilizationUnits"
		:isPlacingMobilizationUnits="isPlacingMobilizationUnits"
	/>

	<UndoTurnButton
		:currentPhaseNum="currentPhaseNum"
		:isThisPlayersTurn="isThisPlayersTurn"
	/>

	<EndTurnButton
		v-if="!showLandingPopUp && !showTeamSelectPopUp"
		:endPhase="endPhase"
		:endTurn="this.worldStore.endTurn"
		:currentPhaseNum="currentPhaseNum"
		:disabled="hasMobilizeUnitsRemaining"
	/>

	<LandingPopUp v-if="showLandingPopUp" :createSession="createSession" />

	<TeamSelectPopUp
		v-if="showTeamSelectPopUp"
		:selectPlayer="selectPlayer"
		:players="players"
		:playerCountry="playerCountry"
	/>

	<BackgroundStars />
</template>

<style scoped></style>
