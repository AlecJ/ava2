<template></template>

<script>
import * as THREE from "three";
import { markRaw } from "vue";
import { gsap } from "gsap";
import { useGlobe } from "@/composables/globe.js";
import { useScene } from "@/composables/scene.js";
import {
	createWindowResizeListener,
	createPointerMoveListener,
} from "@/composables/eventListeners.js";
import { useSessionStore } from "@/stores/session";
import { useWorldStore } from "@/stores/world";

export default {
	props: {
		sessionId: {
			type: String,
			required: false,
		},
		status: {
			type: String,
			required: false,
		},
		focusCountry: {
			type: Function,
			required: true,
		},
		isMovingUnits: {
			type: Boolean,
			required: false,
			default: false,
		},
		selectTerritoryForUnitMovement: {
			type: Function,
			required: true,
		},
	},
	data() {
		return {
			currentHoveredCountry: null,
			currentClickedCountry: null,

			prevZoom: null,
			sessionStore: null,
			worldStore: null,
			clickTimeout: null,
		};
	},
	computed: {
		controlsEnabled() {
			return true; //this.status === "ACTIVE";
		},
		globeAndCountries() {
			return this.worldStore?.threeGlobeAndCountries;
		},
	},
	watch: {
		controlsEnabled(newVal) {
			if (newVal) {
				this.enableListeners();
			} else {
				this.disableListeners();
			}
		},
	},
	methods: {
		initScene() {
			const { scene, camera, renderer, controls } = useScene();
			this.scene = scene;
			this.camera = camera;
			this.renderer = renderer;
			this.controls = controls;

			const { createGlobe, createCountries } = useGlobe();
			const globe = createGlobe();
			const countries = createCountries();

			const globeAndCountries = markRaw(new THREE.Group());
			globeAndCountries.add(globe, countries);
			this.worldStore.setThreeGlobeAndCountries(globeAndCountries);
			this.scene.add(globeAndCountries);

			this.raycaster = new THREE.Raycaster();
			this.pointer = new THREE.Vector2();
		},
		enableListeners() {
			this.pointerMoveListener.enable();
			window.addEventListener("mousedown", this.onMouseDown, false);
			window.addEventListener("click", this.onClick, false);
			this.controls.enabled = true;
		},
		disableListeners() {
			this.pointerMoveListener.disable();
			window.removeEventListener("mousedown", this.onMouseDown, false);
			window.removeEventListener("click", this.onClick, false);
			this.controls.enabled = false;
		},
		// used with onClick to ensure user is not performing a drag
		onMouseDown() {
			this.clickTimeout = Date.now();
		},
		moveCameraToTarget(targetPosition) {
			gsap.to(this.camera.position, {
				x: targetPosition.x,
				y: targetPosition.y,
				z: targetPosition.z,
				duration: 0.8,
				onStart: () => {
					this.controls.enabled = false;
					this.controls.enableZoom = false;
				},
				onComplete: () => {
					this.controls.enabled = true;
					this.controls.enableZoom = true;
					this.controls.update();
				},
			});
		},
		// handles country selection, including zooming and selecting for troop movement
		// zooms in on the country the user clicked on (out after second click)
		onClick() {
			if (Date.now() - this.clickTimeout > 200) {
				return;
			}

			this.raycaster.setFromCamera(this.pointer, this.camera);

			const intersects = this.raycaster.intersectObjects(
				this.scene.children
			);

			if (intersects.length > 0) {
				const territory = intersects[0].object;
				const territoryName = territory.userData?.name;

				console.log("Clicked territory:", territoryName);

				// if a country is selected
				if (!territoryName || !this.isValidTerritory(territoryName)) {
					return;
				}

				// if we are moving units, then just return the name of the territory
				if (this.isMovingUnits) {
					this.selectTerritoryForUnitMovement(territoryName);
					return;
				}

				// if not zoomed in, zoom in
				if (!this.prevZoom) {
					this.currentClickedCountry = territoryName;
					// set country as the user's focused country
					this.focusCountry(territoryName);

					const intersectionPoint = intersects[0].point.clone();

					this.prevZoom = Math.round(this.camera.position.length());

					const targetPosition = intersectionPoint
						.normalize()
						.multiplyScalar(150);

					this.moveCameraToTarget(targetPosition);
				}

				// if already zoomed in ...
				else {
					// if same country, zoom out
					if (this.hasSelectedSameTerritory(territoryName)) {
						// set focused country to null
						this.focusCountry(null);

						const targetPosition = this.camera.position
							.clone()
							.normalize()
							.multiplyScalar(this.prevZoom);

						this.moveCameraToTarget(targetPosition);

						this.prevZoom = null;
						this.currentClickedCountry = null;
					}

					// if different country, shift over
					else {
						this.currentClickedCountry = territoryName;
						// set country as the user's focused country
						this.focusCountry(territoryName);

						const intersectionPoint = intersects[0].point.clone();

						const targetPosition = intersectionPoint
							.normalize()
							.multiplyScalar(150);

						this.moveCameraToTarget(targetPosition);
					}
				}

				// if selecting nothing (space), back out
			} else if (this.prevZoom) {
				// set focused country to null
				this.focusCountry(null);

				const targetPosition = this.camera.position
					.clone()
					.normalize()
					.multiplyScalar(this.prevZoom);

				this.moveCameraToTarget(targetPosition);
				this.prevZoom = null;
			}
		},
		isValidTerritory(territoryName) {
			return !!this.worldStore.territories[territoryName];
		},
		hasSelectedSameTerritory(territoryName) {
			return (
				this.prevZoom && this.currentClickedCountry === territoryName
			);
		},
		resetHoveredCountry() {
			if (this.currentHoveredCountry) {
				const outline = this.currentHoveredCountry.userData.outline;
				outline.material.color.set(0xffffff);
				outline.material.depthTest = true;
				outline.renderOrder = 0;

				// this.currentHoveredCountry.material.color.set(
				// 	this.currentHoveredCountry.material.userData.originalColor
				// );
				this.currentHoveredCountry = null;
			}
		},
		// highlights the country the user is hovering over
		checkForPointerTarget() {
			const intersects = this.raycaster.intersectObjects(
				this.scene.children
			);

			this.resetHoveredCountry();

			if (intersects.length > 0) {
				const country = intersects[0].object;

				if (
					country.userData?.name &&
					country !== this.currentHoveredCountry &&
					this.isValidTerritory(country.userData.name)
				) {
					const outline = country.userData.outline;
					outline.material.color.set(0xffa000);
					outline.material.depthTest = false;
					outline.renderOrder = 1;
					this.currentHoveredCountry = country;
				}
			}
		},
		animate() {
			this.controls.update();
			this.raycaster.setFromCamera(this.pointer, this.camera);

			if (!this.controlsEnabled) {
				this.globeAndCountries.rotation.y -= 0.003;
			} else {
				this.checkForPointerTarget();
			}

			this.renderer.render(this.scene, this.camera);
		},
	},
	created() {
		this.sessionStore = useSessionStore();
		this.worldStore = useWorldStore();

		this.initScene();
		this.windowResizeListener = createWindowResizeListener(
			this.camera,
			this.renderer
		);
		this.windowResizeListener.enable();
		this.pointerMoveListener = createPointerMoveListener(this.pointer);

		this.disableListeners();
	},
	mounted() {
		if (this.controlsEnabled) {
			this.enableListeners();
		}

		this.renderer.setAnimationLoop(this.animate);
	},
	beforeUnmount() {
		this.windowResizeListener.disable();
		this.disableListeners();
	},
};
</script>

<style scoped></style>
