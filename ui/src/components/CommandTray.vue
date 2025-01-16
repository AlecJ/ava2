<script>
export default {
	props: {
		focusedCountry: {
			type: String,
			required: false,
		},
	},
	data() {
		return {
			countryName: null,
		};
	},
	watch: {
		focusedCountry(newVal) {
			if (newVal) {
				// Show the name immediately when a country is selected
				this.countryName = newVal;
			} else {
				// Delay clearing the name until after the sidebar transition ends
				setTimeout(() => {
					this.countryName = null;
				}, 300);
			}
		},
	},
};
</script>

<template>
	<div
		:class="['right-side-bar', { active: !!focusedCountry }]"
		@mousedown.prevent.stop
	>
		<div class="country-name">{{ countryName }}</div>
		<button @click="() => console.log('ok!')">Action</button>
	</div>
</template>

<style scoped lang="scss">
.right-side-bar {
	position: fixed;
	top: 12.5%;
	right: 0;
	overflow: hidden;
	z-index: 1;

	width: 30%;
	min-width: 200px;
	max-width: 600px;
	height: 75%;
	padding: 1rem;

	background-color: rgba(33, 32, 32, 0.931);
	border: 2px solid white;
	border-radius: 2rem 0 0 2rem;
	border-right: 0;

	display: grid;
	place-items: center;
	pointer-events: auto;

	transform: translateX(90%);
	transition: transform 0.3s ease-in-out;

	&.active {
		transform: translateX(0%);
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
