<template>
	<div id="globeViz"></div>
</template>

<script>
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import * as THREE from "three";
import { useGlobe } from "../composables/globe.js";
import { useScene } from "../composables/scene.js";
import { useSessionStore } from "@/stores/session";
import initListeners from "../composables/eventListeners.js";
import { gsap } from "gsap";

export default {
	name: "GlobalView",
	setup() {
		const sessionStore = useSessionStore();
		const route = useRoute();
		const router = useRouter();

		const { scene, camera, renderer, controls } = useScene();

		// Globe and countries created and added as a group
		const { createGlobe, createCountries } = useGlobe();

		const globe = createGlobe();
		const countries = createCountries();

		const globeAndCountries = new THREE.Group();
		globeAndCountries.add(globe, countries);
		scene.add(globeAndCountries);

		// Raycasting setup
		const raycaster = new THREE.Raycaster();
		const pointer = new THREE.Vector2();
		let currentHoveredCountry = null; // Track currently hovered country

		let selectedCountry = null;
		let prevZoom = null;

		const onClick = (event) => {
			// Use raycasting to find the clicked country
			raycaster.setFromCamera(pointer, camera); // Set the ray from the camera

			// Get the intersected objects (countries)
			const intersects = raycaster.intersectObjects(scene.children);

			if (intersects.length > 0) {
				// Get the first intersected country
				const country = intersects[0].object;

				// Log the country name
				console.log("Clicked country:", country.userData.name);

				if (country.userData.name && !prevZoom) {
					// rotate to the country
					// get coordinates of pointer click on sphere
					const intersectionPoint = intersects[0].point.clone();

					prevZoom = Math.round(camera.position.length());

					const targetPosition = intersectionPoint
						.normalize()
						.multiplyScalar(150);

					// disable country during animation
					// toggleOrbitControls(controls, false);

					gsap.to(camera.position, {
						x: targetPosition.x,
						y: targetPosition.y,
						z: targetPosition.z,
						duration: 1.5, // Duration of the animation in seconds
						onStart: () => {
							// Disable OrbitControls when animation starts
							controls.enabled = false;
						},
						onComplete: () => {
							// Re-enable OrbitControls when animation is complete
							controls.enabled = true;
							controls.update();
						},
						onUpdate: () => {
							// controls.update(); // Ensure controls update during animation
							// toggleOrbitControls(controls, true); // reenable controls
						},
					});
				} else if (prevZoom) {
					const targetPosition = camera.position
						.clone()
						.normalize()
						.multiplyScalar(200);

					// disable country during animation
					// toggleOrbitControls(controls, false);

					gsap.to(camera.position, {
						x: targetPosition.x,
						y: targetPosition.y,
						z: targetPosition.z,
						duration: 1.5, // Duration of the animation in seconds
						onStart: () => {
							// Disable OrbitControls when animation starts
							controls.enabled = false;
						},
						onComplete: () => {
							// Re-enable OrbitControls when animation is complete
							controls.enabled = true;
						},
						onUpdate: () => {
							// controls.update(); // Ensure controls update during animation
							// toggleOrbitControls(controls, true); // reenable controls
						},
					});
					console.log(prevZoom);

					prevZoom = null;
				}
			}

			// to do -- zoom in a little? add dialogue ui

			// click out zooms out and removes dialogue
		};

		const checkForPointerTarget = () => {
			// Find objects intersecting the ray
			const intersects = raycaster.intersectObjects(countries.children);

			// If a country is hovered
			if (intersects.length > 0) {
				const country = intersects[0].object;

				// Highlight the country if it's not the current hovered country
				if (country !== currentHoveredCountry) {
					// Reset the previous hovered country's color
					if (currentHoveredCountry) {
						currentHoveredCountry.material.color.set(
							currentHoveredCountry.material.userData
								.originalColor
						);
					}

					// Highlight the current country
					country.material.color.set(0xff0000);
					currentHoveredCountry = country;
				}
			} else {
				// Reset the previous hovered country's color if no country is hovered
				if (currentHoveredCountry) {
					currentHoveredCountry.material.color.set(
						currentHoveredCountry.material.userData.originalColor
					);
					currentHoveredCountry = null;
				}
			}
		};

		const animate = () => {
			controls.update();
			// update the picking ray with the camera and pointer position
			raycaster.setFromCamera(pointer, camera);

			// checkForPointerTarget();
			globeAndCountries.rotation.y -= 0.003;
			renderer.render(scene, camera);
		};

		onMounted(async () => {
			const sessionId = route.params.sessionId;

			if (sessionId) {
				try {
					await sessionStore.getSession(sessionId);
					console.log("Session data:", sessionStore.session);
				} catch (error) {
					console.error("Failed to fetch session:", error);
				}
			} else {
				console.warn("No session ID provided in the route.");

				// create a new session
				try {
					await sessionStore.createSession();
				} finally {
					const newSessionId = sessionStore.sessionId;

					router.push(newSessionId).then(() => {
						// Reload the page
						window.location.reload();
					});
				}
			}

			initListeners(camera, renderer);
			renderer.setAnimationLoop(animate);
		});

		return {
			sessionStore,
		};
	},
};
</script>

<style scoped></style>
