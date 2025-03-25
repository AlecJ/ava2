import { defineStore } from "pinia";
import { API } from "@/services/api";

import { useWorldStore } from "@/stores/world";

export const useSessionStore = defineStore("session", {
	state: () => ({
		sessionId: null,
		playerId: null,
		playerCountry: null,
		players: null,
		status: null,
		turnNum: null,
		isLoading: false,
		isTesting: false,
	}),
	actions: {
		setSession(session) {
			this.sessionId = session.session_id;
			this.status = session.status;
			this.turnNum = session.turn_num;
			this.players = session.players;
		},
		setIsLoading(bool) {
			this.isLoading = bool;
		},
		setPlayer(player) {
			// for setting the user's data
			this.playerId = player.player_id;
			this.playerCountry = player.country;
		},
		setPlayers(players) {
			// for updating all player data (countries and IPCS)
			this.players = players;
		},
		setTurnNum(num) {
			this.turnNum = num;
		},
		async getSession(sessionId, playerId) {
			// also send player ID
			this.isLoading = true;

			try {
				console.log(
					"Fetching session from API:",
					`/session/${sessionId}`
				);

				// todo
				const url = playerId
					? `/session/${sessionId}?pid=${playerId}`
					: `/session/${sessionId}`;

				const response = await API.get(url);
				console.log("API Response:", response.data); // Debugging log
				this.setSession(response.data.session);
				if (response.data.player) this.setPlayer(response.data.player);

				// if the session has started, fetch the game state
				if (response.data.session.status === "ACTIVE") {
					const worldStore = useWorldStore();
					await worldStore.getWorldData();
				}
			} catch (error) {
				console.error("API Error:", error);
			}

			this.isLoading = false;
		},
		async createSession(router) {
			this.isLoading = true;

			try {
				const response = await API.post(`/session/create`);
				console.log("API Response:", response.data); // Debugging log
				this.sessionId = response.data.session_id;
				this.setSession(response.data.session);
				router.push({ path: `/${this.sessionId}` });
			} catch (error) {
				console.error("API Error:", error.response?.data?.status);
			}

			this.isLoading = false;
		},
		// validate country can be joined for sessionId
		// return playerId on success
		async selectPlayer(countryName, router) {
			this.isLoading = true;

			const data = { countryName: countryName };

			try {
				const response = await API.post(
					`/session/join/${this.sessionId}`,
					data
				);

				console.log("API Response:", response.data); // Debugging log

				this.setSession(response.data.session);

				// if player returned, update query param with player ID
				if (response.data?.player) {
					this.setPlayer(response.data.player);
					router.push({ query: { pid: `${this.playerId}` } });
				}
			} catch (error) {
				console.error("API Error:", error.response?.data?.status);

				// TODO dispatch getSession to see available countries
			}

			this.isLoading = false;
		},
	},
	getters: {
		getIsLoading: (state) => state.isLoading,
		getPlayers: (state) => state.players,
		getTurnNum: (state) => state.turnNum,
	},
});
