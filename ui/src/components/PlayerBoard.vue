<script>
export default {
	props: {},
	data() {
		return {
			Countries: [
				{ name: "United States", color: 0x738326, power: 42 },
				{ name: "United Kingdom", color: 0xc5b99b, power: 30 },
				{ name: "Soviet Union", color: 0x7d4932, power: 24 },
				{ name: "Germany", color: 0x767a73, power: 40 },
				{ name: "Japan", color: 0xc78940, power: 30 },
			],
		};
	},
};
</script>

<template>
	<div :class="['board']" @mousedown.prevent.stop>
		<div
			class="playerCard"
			v-for="country in Countries"
			:key="country.name"
			:style="{ backgroundColor: '#' + country.color.toString(16) }"
		>
			<div class="name">{{ country.name }}</div>
			<div class="power">{{ country.power }}</div>
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
