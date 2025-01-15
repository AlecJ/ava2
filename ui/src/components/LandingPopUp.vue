<script>
export default {
	props: {
		createSession: {
			type: Function,
			required: true,
		},
	},
};
</script>

<template>
	<div id="popup">
		<h1>Global Thermonuclear War</h1>
		<p>
			War! Pushed to the brink, the world is engulfed in chaos. Lead your
			nation to victory and restore peace across the globe!
		</p>
		<p>
			Start a game lobby by selecting the "Create New Game" button below.
			You will be able to invite other players from said lobby.
		</p>
		<button @click="createSession">Create New Game</button>
		<p>
			If you are attempting to join a game, you must use the invite link
			from the user that created the game.
		</p>
	</div>
</template>

<style scoped lang="scss">
#popup {
	position: fixed;
	top: 12.5%;
	left: 12.5%;
	overflow: hidden;
	z-index: 1;

	width: 75%;
	height: 75%;

	display: grid;
	place-items: center;

	background-color: rgba(88, 88, 88, 0.663);
	border: 0.15rem solid gray;
	border-radius: 0.5rem;
	color: white;
	font-size: 1.25rem;

	p {
		max-width: 75%;
	}

	button {
		padding: 1rem;
		font-size: 1.5rem;
		background-color: #4caf50;
		color: white;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
	}
}
</style>
