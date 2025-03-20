<script>
import { countries } from "@/data/countries";
import { useSessionStore } from "@/stores/session";

export default {
	props: {
		players: {
			type: Array,
			required: true,
		},
	},
	computed: {},
	methods: {
		getCountryColor(player) {
			const country = countries.find(
				(country) => country.name === player.country
			);

			return country
				? "#" + country.color.toString(16) + "ff"
				: "#0c6f13"; // Default color
		},
	},
};
</script>

<template>
	<div :class="['board']" @mousedown.prevent.stop>
		<div
			class="playerCard"
			v-for="player in players"
			:key="player.country"
			:style="{ backgroundColor: getCountryColor(player) }"
		>
			<div class="name">{{ player.country }}</div>
			<div class="power">{{ player.ipcs }}</div>
		</div>
	</div>
</template>

<style scoped lang="scss">
.board {
	position: fixed;
	top: 12.5%;
	left: 0;
	overflow: hidden;
	z-index: 1;

	width: 15%;
	min-width: 200px;
	max-width: 600px;
	height: 25%;
	padding: 1rem;

	background-color: rgba(33, 32, 32, 0.931);
	border: 2px solid white;
	border-radius: 0 2rem 2rem 0;
	border-left: 0;

	display: grid;
	place-items: center;
	pointer-events: auto;

	.playerCard {
		width: 98%;
		padding: 0.25rem;
		// margin: 0.5rem;
		background-color: #000000;
		color: white;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		font-size: 1rem;
		display: grid;
		grid-template-columns: 1fr auto;
	}
	button {
		width: 12rem;
		padding: 10px 20px;
		background-color: #000000;
		color: white;
		border: none;
		border-radius: 5px;
		cursor: pointer;
		font-size: 1.2rem;
	}
}
</style>
