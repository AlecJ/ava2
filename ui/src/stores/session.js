import { defineStore } from "pinia";
import { API } from "@/services/api";

import { useWorldStore } from "@/stores/world";
import { countries } from "@/data/countries";

export const useSessionStore = defineStore("session", {
	state: () => ({
		sessionId: null,
		playerId: null,
		playerCountry: null,
		players: null,
		status: null,
		turnNum: null,
		phaseNum: null,
		isLoading: false,
		isTesting: false,
	}),
	actions: {
		setSession(session) {
			this.sessionId = session.session_id;
			this.status = session.status;
			this.turnNum = session.turn_num;
			this.phaseNum = session.phase_num;
			this.players = session.players;
		},
		setIsLoading(bool) {
			this.isLoading = bool;
		},
		setPlayer(player) {
			// for setting the user's data
			this.playerId = player.player_id;
			this.playerCountry = player.country;
			this.updateFavicon(player.country);
		},
		updateFavicon(countryName) {
			const favicon = document.querySelector("link[rel='icon']");
			if (!favicon) return;

			// Default favicon if no country is selected
			const defaultFavicon = "/src/assets/flags/tidal-wave.png";

			const countryNameMap = {
				"Soviet Union": "soviet-union.png",
				"United Kingdom": "united-kingdom.png",
				Germany: "germany.png",
				Japan: "japan.png",
				"United States": "united-states-of-america.png",
			};

			const flagFavicon = `/src/assets/flags/${countryNameMap[countryName] || defaultFavicon}`;

			favicon.href = countryName ? flagFavicon : defaultFavicon;

			// Update document title with game details
			const gameDetails = `AvA - ${countryName}`;
			document.title = gameDetails;
		},
		async getSession(sessionId, playerId) {
			// also send player ID
			this.isLoading = true;

			try {
				const url = playerId
					? `/session/${sessionId}?pid=${playerId}`
					: `/session/${sessionId}`;

				const response = await API.get(url);
				this.setSession(response.data.session);
				if (response.data.player) this.setPlayer(response.data.player);

				// if the session has started, fetch the game state
				if (response.data.session.status === "ACTIVE") {
					const worldStore = useWorldStore();
					await worldStore.getWorldData();
				}
			} catch (error) {
				console.error(
					"API Error:",
					error.response?.data?.status || error
				);
			}

			this.isLoading = false;
		},
		async createSession(router) {
			this.isLoading = true;

			try {
				const response = await API.post(`/session/create`);
				this.sessionId = response.data.session_id;
				this.setSession(response.data.session);
				router.push({ path: `/${this.sessionId}` });
			} catch (error) {
				console.error(
					"API Error:",
					error.response?.data?.status || error
				);
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

				this.setSession(response.data.session);

				// if player returned, update query param with player ID
				if (response.data?.player) {
					this.setPlayer(response.data.player);
					router.push({ query: { pid: `${this.playerId}` } });

					if (response.data.session.status === "ACTIVE") {
						const worldStore = useWorldStore();
						await worldStore.getWorldData();
					}
				}
			} catch (error) {
				console.error("API Error:", error.response?.data?.status);

				// TODO dispatch getSession to see available countries
			}

			this.isLoading = false;
		},
	},
	getters: {
		getPlayerId: (state) => state.playerId,
		getPlayer: (state) => {
			if (!state.players) return null;
			return state.players.find(
				(player) => player.country === state.playerCountry
			);
		},
		getPlayerTeamNum: (state) => {
			return countries.findIndex(
				(country) => country.name === state.playerCountry
			);
		},
		getIsLoading: (state) => state.isLoading,
		getPlayers: (state) => state.players,
		getTurnNum: (state) => state.turnNum,
		getPhaseNum: (state) => state.phaseNum,
	},
});
