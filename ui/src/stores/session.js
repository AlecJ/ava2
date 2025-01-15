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
				this.setSession(response.data.data);
			} catch (error) {
				console.error("API Error:", error.message);
			}
		},
		async createSession(router) {
			try {
				const response = await API.post(`/session/create`);
				this.sessionId = response.data.session_id;
				this.setSession(response.data);
				router.push({ path: `/${this.sessionId}` });
			} catch (error) {
				console.error("API Error:", error.message);
			}
		},
		setSession(data) {
			this.sessionId = data.session_id;
			this.status = data.status;
			this.players = data.players;
			this.currentTurn = data.current_turn;
		},
	},
});
