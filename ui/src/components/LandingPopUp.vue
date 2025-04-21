<script>
import PopUp from "@/components/PopUp.vue";

export default {
	props: {
		createSession: {
			type: Function,
			required: true,
		},
	},
	components: {
		PopUp,
	},
};
</script>

<template>
	<PopUp id="popup" width="60rem">
		<h1>Allies vs Axis</h1>
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
	</PopUp>
</template>

<style scoped lang="scss">
#popup {
	color: white;
	font-size: 1.25rem;

	p {
		max-width: 40rem;
		margin: 1rem;
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
