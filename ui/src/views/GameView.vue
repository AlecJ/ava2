<script>
import { useSessionStore } from "@/stores/session";
import { useWorldStore } from "@/stores/world";
import BackgroundStars from "@/components/BackgroundStars.vue";
import LandingPopUp from "@/components/LandingPopUp.vue";
import TeamSelectPopUp from "@/components/TeamSelectPopUp.vue";
import CommandTray from "@/components/CommandTray.vue";
import PlayerBoard from "@/components/PlayerBoard.vue";
import ThreeGlobe from "@/components/ThreeGlobe.vue";

export default {
	name: "GameView",
	components: {
		BackgroundStars,
		LandingPopUp,
		TeamSelectPopUp,
		CommandTray,
		PlayerBoard,
		ThreeGlobe,
	},
	data() {
		return {
			focusedCountry: null,
			sessionStore: null,
			worldStore: null,
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
	/>
	<CommandTray
		:focusedCountry="focusedCountry"
		:captureTerritory="captureTerritory"
	/>

	<PlayerBoard />

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
