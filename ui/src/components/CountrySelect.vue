<script>
export default {
	props: {
		country: {
			type: Object,
			required: true,
		},
		isCountryTaken: {
			type: Boolean,
			required: true,
		},
		playerCountry: {
			type: String,
			required: false,
		},
		selectPlayer: {
			type: Function,
			required: true,
		},
	},
	computed: {
		isPlayer() {
			return this.playerCountry === this.country.name;
		},
	},
};
</script>

<template>
	<div id="countryCard">
		<img :src="country.flagIcon" :alt="country.name" class="flag-icon" />

		<div id="countryName">{{ country.name }}</div>

		<button
			@click="selectPlayer"
			v-if="!isCountryTaken && !this.playerCountry"
		>
			Select
		</button>
		<div v-else-if="isCountryTaken && !isPlayer">Waiting</div>
		<div v-else-if="!isCountryTaken && this.playerCountry && !isPlayer">
			Open
		</div>
		<div v-else-if="isPlayer">You</div>
	</div>
</template>

<style scoped lang="scss">
#countryCard {
	width: 5rem;
	// padding: 1rem;

	// background-color: rgba(88, 88, 88, 0.663);
	// border: 0.15rem solid gray;
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
		text-align: center;
	}

	button {
		width: 80%;
		max-width: 100px;
	}
}
</style>
