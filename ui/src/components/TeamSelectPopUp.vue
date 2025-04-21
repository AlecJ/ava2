<script>
import CountrySelect from "@/components/CountrySelect.vue";
import InviteLinkButton from "@/components/InviteLinkButton.vue";
import PopUp from "@/components/PopUp.vue";
import { countries } from "@/data/countries";

export default {
	components: {
		CountrySelect,
		InviteLinkButton,
		PopUp,
	},
	props: {
		selectPlayer: {
			type: Function,
			required: true,
		},
		players: {
			type: Array,
			required: true,
		},
		playerCountry: {
			type: String,
			required: false,
		},
	},
	data() {
		return {
			countries,
		};
	},
	methods: {
		isCountryTaken(countryName) {
			return (
				this.players.find(
					(player) => player.country === countryName
				) !== undefined
			);
		},
	},
};
</script>

<template>
	<PopUp id="popup" width="60rem">
		<h1>Allies vs Axis</h1>
		<InviteLinkButton />
		<h2 v-if="!playerCountry">Choose a Country to Play</h2>
		<h2 v-else>Waiting for Players to Join</h2>
		<div id="countryCards">
			<CountrySelect
				v-for="country in countries"
				:key="country.name"
				:country="country"
				:isCountryTaken="isCountryTaken(country.name)"
				:playerCountry="playerCountry"
				:selectPlayer="
					() => {
						selectPlayer(country.name);
					}
				"
			/>
		</div>
	</PopUp>
</template>

<style scoped lang="scss">
#popup {
	display: grid;
	place-items: center;
	grid-template-rows: 1.5fr 0.25fr 1.5fr 3fr;

	background-color: rgba(88, 88, 88, 0.663);
	border: 0.15rem solid gray;
	border-radius: 0.5rem;
	color: white;
	font-size: 1.25rem;

	#countryCards {
		display: grid;
		min-width: 42rem;
		grid-template-columns: repeat(5, minmax(100px, 1fr));
		justify-content: space-between;
		justify-items: center;
	}
}
</style>
