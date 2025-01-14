import { defineStore } from "pinia";
import { API } from "@/services/api";

export const useSessionStore = defineStore("session", {
	state: () => ({
		sessionId: null,
		status: null,
		players: [],
		currentTurn: null,
	}),
	actions: {
		async getSession(sessionId) {
			try {
				console.log(
					"Fetching session from API:",
					`/session/${sessionId}`
				);
				const response = await API.get(`/session/${sessionId}`);
				console.log("API Response:", response.data); // Debugging log
				const { status, players, current_turn } = response.data.data;
				this.sessionId = response.data.session_id;
				this.status = status;
				this.players = players;
				this.currentTurn = current_turn;
			} catch (error) {
				console.error("API Error:", error.message);
			}
		},
		async createSession(router) {
			try {
				const response = await API.post(`/session/create`);
				this.sessionId = response.data.session_id;
				router.push({ path: `/${this.sessionId}` });
			} catch (error) {
				console.error("API Error:", error.message);
			}
		},
	},
});
