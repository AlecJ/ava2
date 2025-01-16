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

export default {
	data() {
		return {
			globeAndCountries: null,
			currentHoveredCountry: null,
			selectedCountry: null,
			prevZoom: null,
			sessionStore: null,
			clickTimeout: null,
		};
	},
	computed: {
		sessionId() {
			return this.sessionStore?.sessionId;
		},
		status() {
			return this.sessionStore?.status;
		},
		controlsEnabled() {
			return this.sessionId && this.status === "!TEAM_SELECT";
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

			this.globeAndCountries = markRaw(new THREE.Group());
			this.globeAndCountries.add(globe, countries);
			this.scene.add(this.globeAndCountries);

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
				duration: 1.5,
				onStart: () => {
					this.controls.enabled = false;
				},
				onComplete: () => {
					this.controls.enabled = true;
					this.controls.update();
				},
			});
		},
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
				const country = intersects[0].object;

				console.log("Clicked country:", country.userData.name);

				if (country.userData?.name && !this.prevZoom) {
					const intersectionPoint = intersects[0].point.clone();

					this.prevZoom = Math.round(this.camera.position.length());

					const targetPosition = intersectionPoint
						.normalize()
						.multiplyScalar(150);

					this.moveCameraToTarget(targetPosition);
				} else if (this.prevZoom) {
					const targetPosition = this.camera.position
						.clone()
						.normalize()
						.multiplyScalar(200);

					this.moveCameraToTarget(targetPosition);
					this.prevZoom = null;
				}
			}
		},
		resetHoveredCountry() {
			if (this.currentHoveredCountry) {
				this.currentHoveredCountry.material.color.set(
					this.currentHoveredCountry.material.userData.originalColor
				);
				this.currentHoveredCountry = null;
			}
		},
		// highlights the country the user is hovering over
		checkForPointerTarget() {
			const intersects = this.raycaster.intersectObjects(
				this.scene.children
			);

			if (intersects.length > 0) {
				const country = intersects[0].object;

				if (
					country.userData?.name &&
					country !== this.currentHoveredCountry
				) {
					this.resetHoveredCountry();
					country.material.color.set(0xff0000);
					this.currentHoveredCountry = country;
				} else {
					this.resetHoveredCountry();
				}
			} else {
				this.resetHoveredCountry();
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
		this.initScene();
		this.windowResizeListener = createWindowResizeListener(
			this.camera,
			this.renderer
		);
		this.windowResizeListener.enable();
		this.pointerMoveListener = createPointerMoveListener(this.pointer);
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
