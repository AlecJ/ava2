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

		<div class="countryName">{{ country.name }}</div>

		<button
			@click="selectPlayer"
			class="playerSlot"
			v-if="!isCountryTaken && !this.playerCountry"
		>
			Select
		</button>
		<div class="playerSlot" v-else-if="isCountryTaken && !isPlayer">
			Waiting
		</div>
		<div
			class="playerSlot"
			v-else-if="!isCountryTaken && this.playerCountry && !isPlayer"
		>
			Open
		</div>
		<div class="playerSlot" v-else-if="isPlayer">You</div>
	</div>
</template>

<style scoped lang="scss">
#countryCard {
	border-radius: 0.5rem;
	color: white;
	font-size: 1.25rem;

	display: grid;
	justify-items: center;
	align-content: flex-start;

	.flag-icon {
		width: 100%;
		max-width: 6rem;
		height: auto;
		border-radius: 50%;
		object-fit: cover;
		display: block;
	}

	.countryName {
		margin: 1.5rem 0 0.5rem 0;
		text-align: center;
	}

	button {
		width: 80%;
		max-width: 100px;
		margin-top: 0.75rem;
	}

	.playerSlot {
		height: 3rem;
		padding: 0.75rem;
		margin-top: 0.75rem;
		margin-bottom: 1.5rem;
	}
}
</style>
