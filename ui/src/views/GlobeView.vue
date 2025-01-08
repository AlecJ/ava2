<template>
	<div id="globeViz"></div>
</template>

<script>
import * as THREE from "three";
import { useGlobe } from "../composables/globe.js";
import { useScene } from "../composables/scene.js";
import { useSessionStore } from "@/stores/session";
import initListeners from "../composables/eventListeners.js";
import { gsap } from "gsap";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

export default {
	name: "GlobalView",
	data() {
		return {
			globeAndCountries: null,
			currentHoveredCountry: null,
			selectedCountry: null,
			prevZoom: null,
			sessionStore: null,
		};
	},
	computed: {
		sessionId() {
			return this.sessionStore.sessionId;
		},
	},
	methods: {
		async fetchSession() {
			const sessionId = this.$route.params.sessionId;

			if (sessionId) {
				try {
					await this.sessionStore.getSession(sessionId);
					console.log("Session data:", this.sessionStore.session);
				} catch (error) {
					console.error("Failed to fetch session:", error);
				}
			} else {
				console.warn("No session ID provided in the route.");
				try {
					await this.sessionStore.createSession();
				} catch (error) {
					console.error("Failed to create session:", error);
				}
			}
		},
		initScene() {
			const { scene, camera, renderer, controls } = useScene();
			this.scene = scene;
			this.camera = camera;
			this.renderer = renderer;
			this.controls = controls;

			const { createGlobe, createCountries } = useGlobe();
			this.globe = createGlobe();
			this.countries = createCountries();
			// this.scene.add(this.globe, this.countries);

			this.globeAndCountries = new THREE.Group();
			this.globeAndCountries.add(this.globe, this.countries);
			this.scene.add(this.globeAndCountries);
			// this.scene.add(globe);
			// this.scene.add(countries);

			this.raycaster = new THREE.Raycaster();
			this.pointer = new THREE.Vector2();
		},
		onClick(event) {
			this.raycaster.setFromCamera(this.pointer, this.camera);

			const intersects = this.raycaster.intersectObjects(
				this.scene.children
			);

			if (intersects.length > 0) {
				const country = intersects[0].object;

				console.log("Clicked country:", country.userData.name);

				if (country.userData.name && !this.prevZoom) {
					const intersectionPoint = intersects[0].point.clone();

					this.prevZoom = Math.round(this.camera.position.length());

					const targetPosition = intersectionPoint
						.normalize()
						.multiplyScalar(150);

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
				} else if (this.prevZoom) {
					const targetPosition = this.camera.position
						.clone()
						.normalize()
						.multiplyScalar(200);

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
						},
					});
					this.prevZoom = null;
				}
			}
		},
		checkForPointerTarget() {
			const intersects = this.raycaster.intersectObjects(
				this.globeAndCountries.children
			);

			if (intersects.length > 0) {
				const country = intersects[0].object;

				if (country !== this.currentHoveredCountry) {
					if (this.currentHoveredCountry) {
						this.currentHoveredCountry.material.color.set(
							this.currentHoveredCountry.material.userData
								.originalColor
						);
					}

					country.material.color.set(0xff0000);
					this.currentHoveredCountry = country;
				}
			} else {
				if (this.currentHoveredCountry) {
					this.currentHoveredCountry.material.color.set(
						this.currentHoveredCountry.material.userData
							.originalColor
					);
					this.currentHoveredCountry = null;
				}
			}
		},
		animate() {
			this.controls.update();
			this.raycaster.setFromCamera(this.pointer, this.camera);
			this.checkForPointerTarget();
			this.globeAndCountries.rotation.y -= 0.003;
			this.renderer.render(this.scene, this.camera);
		},
	},
	created() {
		this.sessionStore = useSessionStore(); // Initialize the session store
		// this.animate = this.animate.bind(this);
		this.initScene();
	},
	mounted() {
		// this.fetchSession();

		initListeners(this.camera, this.renderer, this.pointer);
		window.addEventListener("click", this.onClick, false);

		this.renderer.setAnimationLoop(this.animate);
	},
};
</script>

<style scoped></style>
