import { defineStore } from "pinia";
import { API } from "@/services/api";

export const useSessionStore = defineStore("session", {
	state: () => ({
		sessionId: null,
		playerId: null,
		playerCountry: null,
		status: null,
		currentTurn: null,
	}),
	actions: {
		setSession(session) {
			this.sessionId = session.session_id;
			this.status = session.status;
			this.currentTurn = session.current_turn;
		},
		selectPlayer(player) {
			this.playerId = player.player_id;
			this.playerCountry = player.country;
		},
		async getSession(sessionId, playerId) {
			// also send player ID
			try {
				console.log(
					"Fetching session from API:",
					`/session/${sessionId}`
				);

				const response = await API.get(
					`/session/${sessionId}?pid=${playerId}`
				);
				console.log("API Response:", response.data); // Debugging log
				this.setSession(response.data.session);
				this.selectPlayer(response.data.player);
			} catch (error) {
				console.error("API Error:", error.message);
			}
		},
		async createSession(router) {
			try {
				const response = await API.post(`/session/create`);
				console.log("API Response:", response.data); // Debugging log
				this.sessionId = response.data.session_id;
				this.setSession(response.data.session);
				router.push({ path: `/${this.sessionId}` });
			} catch (error) {
				console.error("API Error:", error.message);
			}
		},
		// validate country can be joined for sessionId
		// return playerId on success
		async selectPlayer(countryName, router) {
			const data = { countryName: countryName };

			const response = await API.post(
				`/session/join/${this.sessionId}`,
				data
			);

			console.log("API Response:", response.data); // Debugging log

			// if player returned, update session ID
			if (response.data?.player) {
				this.selectPlayer(response.data.player);
				router.push({ query: { pid: `${this.playerId}` } });
			}
		},
	},
});
