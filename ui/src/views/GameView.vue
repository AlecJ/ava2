<script>
import { useSessionStore } from "@/stores/session";
import BackgroundStars from "@/components/BackgroundStars.vue";
import LandingPopUp from "@/components/LandingPopUp.vue";
import TeamSelectPopUp from "@/components/TeamSelectPopUp.vue";
import Globe from "@/components/Globe.vue";

export default {
	name: "GameView",
	components: {
		BackgroundStars,
		LandingPopUp,
		TeamSelectPopUp,
		Globe,
	},
	data() {
		return {
			globeAndCountries: null,
			currentHoveredCountry: null,
			selectedCountry: null,
			prevZoom: null,
			sessionStore: null,
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
		showLandingPopUp() {
			return this.sessionId === null;
		},
		showTeamSelectPopUp() {
			return this.status === "TEAM_SELECT";
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
	},
	created() {
		this.sessionStore = useSessionStore();
	},
	mounted() {
		this.fetchSession();
	},
};
</script>

<template>
	<Globe />
	<BackgroundStars />
	<LandingPopUp v-if="showLandingPopUp" :createSession="createSession" />
	<TeamSelectPopUp
		v-if="showTeamSelectPopUp"
		:selectPlayer="selectPlayer"
		:countries="countries"
	/>
</template>

<style scoped></style>
