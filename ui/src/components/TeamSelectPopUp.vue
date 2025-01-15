<script>
import CountrySelect from "@/components/CountrySelect.vue";
import { countries } from "@/data/countries";

export default {
	components: {
		CountrySelect,
	},
	props: {
		selectPlayer: {
			type: Function,
			required: true,
		},
	},
	data() {
		return {
			countries,
		};
	},
};
</script>

<template>
	<div id="popup">
		<h1>Axis vs Allies</h1>
		<h2>Choose a Country to Play</h2>
		<div id="countryCards">
			<CountrySelect
				v-for="country in countries"
				:key="country.name"
				:country="country"
				:selectPlayer="
					() => {
						console.log('selected button');
						selectPlayer(country.name);
					}
				"
			/>
		</div>
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
	min-width: 770px;
	height: 75%;

	display: grid;
	place-items: center;
	grid-template-rows: 1fr 1fr 2fr;

	background-color: rgba(88, 88, 88, 0.663);
	border: 0.15rem solid gray;
	border-radius: 0.5rem;
	color: white;
	font-size: 1.25rem;

	#countryCards {
		display: grid;
		width: 100%;
		grid-template-columns: repeat(5, minmax(100px, 1fr));
		justify-content: space-between;
		justify-items: center;
	}
}
</style>
