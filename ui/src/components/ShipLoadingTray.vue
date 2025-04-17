<script>
import { useWorldStore } from "@/stores/world";
import { unitIcons } from "@/data/unitIcons";
import { countries } from "@/data/countries";

export default {
	props: {
		territoryName: {
			type: String,
			required: true,
		},
		nearbyUnits: {
			type: Array,
			required: true,
		},
		transports: {
			type: Array,
			required: true,
		},
		carriers: {
			type: Array,
			required: true,
		},
		neighboringTerritoriesData: {
			type: Object,
			required: false,
			default: [],
		},
		transportToUnload: {
			type: Object,
			required: false,
			default: {},
		},
		setTransportToUnload: {
			type: Function,
			required: true,
		},
	},
	data() {
		return { worldStore: null };
	},
	computed: {
		selectedUnits() {
			return this.nearbyUnits.filter((unit) => unit.selected);
		},
	},
	methods: {
		getUnitIconSrc(unit) {
			const unitIcon = unitIcons.find((u) => u.name === unit.unit_type);

			return unitIcon ? unitIcon.unitIcon : "";
		},
		getColorForUnit(unit, readOnly = false) {
			const unitCountry = countries[unit.team];

			const alpha = readOnly || unit.selected ? "ff" : "50"; // Fully opaque if selected, semi-transparent if not

			return unitCountry
				? "#" + unitCountry.color.toString(16) + alpha
				: "#0c6f13"; // Default color
		},
		getCargo(transport) {
			return (transport.cargo?.length || 0) === 0
				? [false, false]
				: transport.cargo.length === 1
					? [...transport.cargo, false]
					: transport.cargo;
		},
		toggle(unit) {
			if (!unit.selected) {
				unit.selected = true;
			} else {
				unit.selected = !unit.selected;
			}
		},
		loadUnits(transport) {
			// move unit from territory to transport cargo
			console.log(this.selectedUnits);
			if (this.selectedUnits.length > 2) {
				// todo alert user or prevent?
				console.log("cannot load more than 3 units onto a transport");
				return;
			}

			this.worldStore?.loadTransport(
				this.territoryName,
				transport,
				this.selectedUnits
			);
		},
		unloadUnits(transport) {
			// need to select a territory to unload to
			this.setTransportToUnload(transport);
		},
		launchAirUnits(transport) {
			this.worldStore.unloadTransport(
				this.territoryName,
				this.territoryName,
				transport
			);
		},
	},
	created() {
		this.worldStore = useWorldStore();
	},
};
</script>

<template>
	<div
		v-for="transportType in transportToUnload
			? ['']
			: ['TRANSPORT', 'AIRCRAFT-CARRIER']"
		class="ship-loading-tray"
	>
		<p
			v-if="
				transportType === 'TRANSPORT' &&
				transports.length &&
				!transportToUnload
			"
		>
			Transports
		</p>
		<p
			v-if="
				transportType === 'AIRCRAFT-CARRIER' &&
				carriers.length &&
				!transportToUnload
			"
		>
			Aircraft Carriers
		</p>
		<div
			v-for="transport in transportToUnload
				? [transportToUnload]
				: transportType === 'TRANSPORT'
					? transports
					: carriers"
			class="ship-row"
			:key="transport.unit_id"
		>
			<div
				class="ship-icon"
				:style="{
					backgroundColor: getColorForUnit(
						transport,
						(readOnly = true)
					),
				}"
			>
				<img
					:src="getUnitIconSrc(transport)"
					:alt="transport.unit_type"
					class="ship-img"
					:title="transport.unit_type"
				/>
			</div>
			<div class="ship-cargo">
				<div
					v-for="cargo in getCargo(transport)"
					class="cargo-icon"
					:style="{
						backgroundColor: cargo
							? getColorForUnit(transport, (readOnly = true))
							: '#bec9ce50',
					}"
				>
					<img
						v-if="cargo"
						:src="getUnitIconSrc(cargo)"
						:alt="cargo.unit_type"
						class="cargo-img"
						:title="cargo.unit_type"
					/>
				</div>
			</div>
			<button
				v-if="!transportToUnload && transport.unit_type === 'TRANSPORT'"
				class="ship-load-button"
				:disabled="
					transport.cargo?.length === 2 ||
					!this.selectedUnits.length ||
					this.selectedUnits.length > 2
				"
				@click="loadUnits(transport)"
			>
				Load
			</button>
			<button
				v-if="!transportToUnload && transport.unit_type === 'TRANSPORT'"
				class="ship-unload-button"
				:disabled="!transport.cargo?.length"
				@click="unloadUnits(transport)"
			>
				Unload
			</button>
			<button
				v-if="
					!transportToUnload &&
					transport.unit_type === 'AIRCRAFT-CARRIER'
				"
				class="ship-unload-button"
				:disabled="!transport.cargo?.length"
				@click="launchAirUnits(transport)"
			>
				Launch
			</button>
		</div>
	</div>
</template>

<style scoped lang="scss">
.ship-loading-tray {
	width: 100%;

	display: grid;
	place-items: center;

	p {
		font-size: 1.25rem;
	}

	.ship-row {
		margin: 0.5rem 0;
		display: grid;
		grid-template-columns: 1fr 4fr 2fr 2fr;
		place-items: center;

		.ship-icon,
		.cargo-icon {
			width: 3rem; /* Adjust size */
			height: 3rem;
			margin: 0;

			border-radius: 50%; /* Makes it circular */
			background-color: #00000000; /* Default color */
			border: none;
			display: flex;
			justify-content: center;
			align-items: center;

			.ship-img,
			.cargo-img {
				width: 100%;
				height: auto;
			}
		}

		.ship-cargo {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 0.25rem;
		}

		.ship-load-button,
		.ship-unload-button {
			margin: 0 0.5rem;
		}
	}
}
</style>
