<script>
export default {
	props: {
		country: {
			type: Object,
			required: true,
		},
		selectPlayer: {
			type: Function,
			required: true,
		},
	},
};
</script>

<template>
	<div id="countryCard">
		<img :src="country.flagIcon" :alt="country.name" class="flag-icon" />

		<div id="countryName">{{ country.name }}</div>

		<button @click="selectPlayer">Select</button>
	</div>
</template>

<style scoped lang="scss">
#countryCard {
	width: 150px;
	padding: 1rem;

	background-color: rgba(88, 88, 88, 0.663);
	border: 0.15rem solid gray;
	border-radius: 0.5rem;
	color: white;
	font-size: 1.25rem;

	display: grid;
	justify-items: center;
	align-content: flex-start;

	.flag-icon {
		width: 100%;
		max-width: 100px;
		height: auto;
		border-radius: 50%;
		object-fit: cover;
		display: block;
	}

	#countryName {
		margin: 1rem 0;
	}

	button {
		width: 80%;
		max-width: 100px;
	}
}
</style>
