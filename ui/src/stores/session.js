import { defineStore } from "pinia";
import { API } from "@/services/api";

export const useSessionStore = defineStore("session", {
	state: () => ({
		sessionId: null,
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
				this.sessionId = response.data.id;
			} catch (error) {
				console.error("API Error:", error.message);
			}
		},
		async createSession() {
			try {
				const response = await API.post(`/session/create`);
				console.log();
				this.sessionId = response.data.session_id;
			} catch (error) {
				console.error("API Error:", error.message);
			}
		},
	},
});
