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
import PurchaseUnitsButton from "@/components/PurchaseUnitsButton.vue";
import CombatButton from "@/components/CombatButton.vue";
import PlaceMobilizationUnitsButton from "@/components/PlaceMobilizationUnitsButton.vue";
import UndoTurnButton from "@/components/UndoTurnButton.vue";
import EndTurnButton from "@/components/EndTurnButton.vue";

export default {
	name: "GameView",
	components: {
		BackgroundStars,
		LandingPopUp,
		TeamSelectPopUp,
		DefaultTray,
		PlayerBoard,
		ThreeGlobe,
		PurchaseUnitsButton,
		CombatButton,
		PlaceMobilizationUnitsButton,
		UndoTurnButton,
		EndTurnButton,
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
			showBattles: false,
			pollingInterval: null,
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
			const player = this.sessionStore?.getPlayer;

			if (!player) return {};

			return {
				...player,
				team: this.playerTeamNum,
			};
		},
		playerCountry() {
			// TODO replace with above
			return this.sessionStore?.playerCountry || "";
		},
		playerTeamNum() {
			return this.sessionStore?.getPlayerTeamNum;
		},
		isThisPlayersTurn() {
			if (!this.player) return false;

			return this.currentTurnNum % 5 === this.playerTeamNum;
		},
		isThisPlayersTurnNext() {
			if (!this.player) return false;

			return (this.currentTurnNum + 1) % 5 === this.playerTeamNum;
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
			return (this.player.mobilization_units?.length ?? 0) > 0;
		},
		hasUnresolvedBattles() {
			return this.worldStore?.getBattles.some(
				(battle) => battle.result === null
			);
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
		setShowBattles(bool) {
			this.showBattles = bool;
		},
		setPlacingMobilizationUnits(bool) {
			this.isPlacingMobilizationUnits = bool;
		},
		endPhase() {
			this.setIsSelectingTerritory(false);
			this.setPurchasingUnits(false);
			this.setShowBattles(false);
			this.worldStore.endPhase();
		},
		endTurn() {
			this.setIsSelectingTerritory(false);
			this.setPlacingMobilizationUnits(false);
			this.worldStore.endTurn();
		},
	},
	created() {
		this.sessionStore = useSessionStore();
		this.worldStore = useWorldStore();
		this.worldStore.initTerritories();
	},
	mounted() {
		this.fetchSession();

		// poll normally every 30 seconds
		this.pollingInterval = setInterval(() => {
			if (!this.isThisPlayersTurn && !this.isThisPlayersTurnNext)
				this.fetchSession();
		}, 15000);

		// if it is almost this players turn, poll every 7 seconds
		this.pollingInterval = setInterval(() => {
			if (
				(!this.isThisPlayersTurn && this.isThisPlayersTurnNext) ||
				this.showTeamSelectPopUp
			)
				this.fetchSession();
		}, 7000);
	},
};
</script>

<template>
	<!-- needs refactor, merge isMoving into isSelecting -->
	<ThreeGlobe
		:sessionId="sessionId"
		:player="player"
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
		:showBattles="showBattles"
		:isPlacingMobilizationUnits="isPlacingMobilizationUnits"
		:setIsSelectingTerritory="setIsSelectingTerritory"
		:selectedTerritory="selectedTerritory"
	/>

	<PlayerBoard
		v-if="!showLandingPopUp && !showTeamSelectPopUp"
		:player="player"
		:players="players"
		:currentTurnNum="currentTurnNum"
	/>

	<div class="tray-buttons">
		<PurchaseUnitsButton
			v-if="!showLandingPopUp && !showTeamSelectPopUp"
			:active="currentPhaseNum === 0 && isThisPlayersTurn"
			:setPurchasingUnits="setPurchasingUnits"
			:isPurchasingUnits="isPurchasingUnits"
		/>

		<CombatButton
			v-if="!showLandingPopUp && !showTeamSelectPopUp"
			:active="
				(currentPhaseNum === 1 || currentPhaseNum === 2) &&
				isThisPlayersTurn
			"
			:setShowBattles="setShowBattles"
			:showBattles="showBattles"
		/>

		<PlaceMobilizationUnitsButton
			v-if="!showLandingPopUp && !showTeamSelectPopUp"
			:active="currentPhaseNum === 4 && isThisPlayersTurn"
			:setPlacingMobilizationUnits="setPlacingMobilizationUnits"
			:isPlacingMobilizationUnits="isPlacingMobilizationUnits"
		/>
	</div>

	<UndoTurnButton
		v-if="!showLandingPopUp && !showTeamSelectPopUp"
		:currentPhaseNum="currentPhaseNum"
		:isThisPlayersTurn="isThisPlayersTurn"
	/>

	<EndTurnButton
		v-if="!showLandingPopUp && !showTeamSelectPopUp"
		:endPhase="endPhase"
		:endTurn="endTurn"
		:currentPhaseNum="currentPhaseNum"
		:hasUnresolvedBattles="hasUnresolvedBattles"
		:hasMobilizeUnitsRemaining="hasMobilizeUnitsRemaining"
		:isThisPlayersTurn="isThisPlayersTurn"
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

<style scoped>
.tray-buttons {
	position: absolute;
	top: 40%;
	left: -2rem;
	display: grid;
	gap: 1rem;
}
</style>
