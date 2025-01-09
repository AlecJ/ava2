<script>
import { useSessionStore } from "@/stores/session";
import BackgroundStars from "@/components/BackgroundStars.vue";
import LandingPopUp from "@/components/LandingPopUp.vue";
import Globe from "@/components/Globe.vue";

export default {
	name: "GameView",
	components: {
		BackgroundStars,
		LandingPopUp,
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
			return this.sessionStore.sessionId;
		},
	},
	methods: {
		async fetchSession() {
			const sessionId = this.$route.params.sessionId;

			if (sessionId) {
				try {
					await this.sessionStore.getSession(sessionId);
					console.log("Session data:", this.sessionStore.session);
				} catch (error) {
					console.error("Failed to fetch session:", error);
				}
			}
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
	<LandingPopUp v-if="sessionId === null" :createSession="createSession" />
</template>

<style scoped></style>
