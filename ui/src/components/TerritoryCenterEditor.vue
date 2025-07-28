<template>
	<div class="territory-editor">
		<div class="controls">
			<h3>Territory Center Editor</h3>

			<div class="territory-selector">
				<label>Select Territory:</label>
				<select v-model="selectedTerritory">
					<option value="">Choose a territory...</option>
					<option
						v-for="territory in territories"
						:key="territory"
						:value="territory"
					>
						{{ territory }}
					</option>
				</select>
			</div>

			<div
				v-if="selectedTerritory && territoryCenters[selectedTerritory]"
				class="selected-territory"
			>
				<h4>{{ selectedTerritory }}</h4>
				<p>Current position:</p>
				<div class="coordinates">
					<label
						>X:
						<input
							type="number"
							step="0.001"
							v-model.number="
								territoryCenters[selectedTerritory].x
							"
					/></label>
					<label
						>Y:
						<input
							type="number"
							step="0.001"
							v-model.number="
								territoryCenters[selectedTerritory].y
							"
					/></label>
					<label
						>Z:
						<input
							type="number"
							step="0.001"
							v-model.number="
								territoryCenters[selectedTerritory].z
							"
					/></label>
				</div>
				<p><small>Click on the globe to set new position</small></p>
				<p><small>🇯🇵 Japan flag shows current/new position</small></p>
			</div>

			<div v-else-if="selectedTerritory" class="selected-territory">
				<h4>{{ selectedTerritory }}</h4>
				<p style="color: orange">
					No center data found for this territory.
				</p>
				<p><small>Click on the globe to set initial position</small></p>
			</div>

			<div class="file-operations">
				<button @click="exportCenters">Export Centers</button>
			</div>
		</div>
	</div>
</template>

<script>
import * as THREE from "three";
import { markRaw, reactive } from "vue";
import { useGlobe } from "@/composables/globe.js";
import { useScene } from "@/composables/scene.js";
import {
	createWindowResizeListener,
	createPointerMoveListener,
} from "@/composables/eventListeners.js";
import territoryCentersData from "@/data/territoryCenters.json";
import japanFlag from "@/assets/flags/japan.png";

export default {
	name: "TerritoryCenterEditor",
	data() {
		return {
			scene: null,
			camera: null,
			renderer: null,
			controls: null,
			raycaster: null,
			pointer: null,
			globeAndCountries: null,
			selectedTerritory: null,
			territoryCenters: reactive({ ...territoryCentersData }),
			territories: [],
			previewSprite: null,
			materialCache: new Map(),
		};
	},
	mounted() {
		this.initScene();
		this.loadTerritories();
		this.renderer.setAnimationLoop(this.animate);

		// Add click listener
		window.addEventListener("click", this.onClick, false);
	},
	beforeUnmount() {
		window.removeEventListener("click", this.onClick, false);
		if (this.pointerMoveListener) {
			this.pointerMoveListener.disable();
		}
		if (this.previewSprite) {
			this.scene.remove(this.previewSprite);
		}
		if (this.renderer) {
			this.renderer.setAnimationLoop(null);
			if (this.renderer.domElement.parentNode) {
				this.renderer.domElement.parentNode.removeChild(
					this.renderer.domElement
				);
			}
		}
	},
	watch: {
		selectedTerritory(newTerritory) {
			// Add a small delay to ensure scene is fully initialized
			this.$nextTick(() => {
				try {
					// Make sure scene is initialized before trying to update sprites
					if (!this.scene || !this.renderer) {
						console.log(
							"Scene not ready, skipping preview sprite update"
						);
						return;
					}

					if (newTerritory && this.territoryCenters[newTerritory]) {
						// Show preview sprite at current territory center
						const center = this.territoryCenters[newTerritory];
						const position = new THREE.Vector3(
							center.x,
							center.y,
							center.z
						);
						this.updatePreviewSprite(position);
					} else if (this.previewSprite && this.scene) {
						// Remove preview sprite if no territory selected
						this.scene.remove(this.previewSprite);
						this.previewSprite = null;
					}
				} catch (error) {
					console.error("Error updating preview sprite:", error);
					// Ensure we clean up if there's an error
					if (this.previewSprite && this.scene) {
						this.scene.remove(this.previewSprite);
						this.previewSprite = null;
					}
				}
			});
		},
	},
	methods: {
		initScene() {
			const { scene, camera, renderer, controls } = useScene();
			this.scene = markRaw(scene);
			this.camera = markRaw(camera);
			this.renderer = markRaw(renderer);
			this.controls = markRaw(controls);

			// Mount the renderer to the component
			this.$el.appendChild(this.renderer.domElement);

			const { createGlobe, createCountries } = useGlobe();
			const globe = createGlobe();
			const countries = createCountries();

			this.globeAndCountries = markRaw(new THREE.Group());
			this.globeAndCountries.add(globe, countries);
			this.scene.add(this.globeAndCountries);

			this.raycaster = markRaw(new THREE.Raycaster());
			this.pointer = markRaw(new THREE.Vector2());

			// Add pointer move listener
			this.pointerMoveListener = createPointerMoveListener(this.pointer);
			this.pointerMoveListener.enable();
		},
		loadTerritories() {
			// Wait a frame for the scene to be fully loaded
			this.$nextTick(() => {
				try {
					// Get list of territories from the countries mesh
					const countriesMesh =
						this.globeAndCountries.children[1].children[0];
					this.territories = countriesMesh.children
						.filter(
							(child) => child.userData?.name
							// Include both regular territories and ocean tiles
						)
						.map((child) => child.userData.name)
						.sort();
				} catch (error) {
					console.error("Error loading territories:", error);
					// Fallback: use territory names from the imported data
					this.territories = Object.keys(territoryCentersData).sort();
				}
			});
		},
		createPreviewSprite() {
			try {
				if (!this.materialCache.has(japanFlag)) {
					const texture = markRaw(
						new THREE.TextureLoader().load(japanFlag)
					);
					const material = markRaw(
						new THREE.SpriteMaterial({ map: texture })
					);
					this.materialCache.set(japanFlag, material);
				}

				const material = this.materialCache.get(japanFlag);
				const sprite = markRaw(new THREE.Sprite(material)); // Mark as raw to prevent reactivity
				sprite.scale.set(5, 5, 1); // Make it visible
				sprite.userData = { name: "preview-flag" };

				return sprite;
			} catch (error) {
				console.error("Error creating preview sprite:", error);
				// Return a basic sprite as fallback
				const basicMaterial = markRaw(
					new THREE.SpriteMaterial({
						color: 0xff0000,
					})
				);
				const sprite = markRaw(new THREE.Sprite(basicMaterial)); // Mark as raw to prevent reactivity
				sprite.scale.set(8, 8, 1);
				sprite.userData = { name: "preview-flag-fallback" };
				return sprite;
			}
		},
		updatePreviewSprite(position) {
			// Safety check: make sure scene is ready
			if (!this.scene || !this.renderer) {
				console.log("Scene not ready for sprite update");
				return;
			}

			try {
				// Remove existing preview sprite
				if (this.previewSprite) {
					this.scene.remove(this.previewSprite);
				}

				// Create new preview sprite at the position
				this.previewSprite = this.createPreviewSprite();

				// Scale the position to be slightly above the globe surface
				const scaledPosition = position.clone().multiplyScalar(103);
				this.previewSprite.position.copy(scaledPosition);

				this.scene.add(this.previewSprite);
			} catch (error) {
				console.error("Error in updatePreviewSprite:", error);
				// Clean up on error
				if (this.previewSprite) {
					this.previewSprite = null;
				}
			}
		},
		onClick() {
			if (!this.selectedTerritory) return;

			this.raycaster.setFromCamera(this.pointer, this.camera);

			// Create a sphere to raycast against
			const sphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), 100);
			const ray = this.raycaster.ray;
			const intersectionPoint = new THREE.Vector3();

			if (ray.intersectSphere(sphere, intersectionPoint)) {
				// Normalize the intersection point to get the correct position on unit sphere
				const normalizedPoint = intersectionPoint.normalize();

				// Create or update the territory center
				this.territoryCenters[this.selectedTerritory] = {
					x: normalizedPoint.x,
					y: normalizedPoint.y,
					z: normalizedPoint.z,
				};

				// Show preview sprite at the new position
				this.updatePreviewSprite(normalizedPoint);
			}
		},
		animate() {
			this.controls.update();
			this.renderer.render(this.scene, this.camera);
		},
		exportCenters() {
			// Copy to clipboard or download as file
			const json = JSON.stringify(this.territoryCenters, null, 2);
			navigator.clipboard.writeText(json);
			console.log("Territory centers copied to clipboard!");
		},
	},
};
</script>

<style scoped>
.territory-editor {
	width: 100%;
	height: 100vh;
	position: relative;
	background: #000;
}

.controls {
	position: absolute;
	top: 20px;
	left: 20px;
	background: rgba(0, 0, 0, 0.8);
	color: white;
	padding: 20px;
	border-radius: 8px;
	z-index: 100;
	min-width: 300px;
}

.controls h3 {
	margin: 0 0 20px 0;
	color: #fff;
}

.control-group {
	margin-bottom: 15px;
}

.control-group label {
	display: block;
	margin-bottom: 5px;
	color: #ccc;
}

select,
input[type="range"],
input[type="file"],
button {
	width: 100%;
	padding: 8px;
	border-radius: 4px;
	border: 1px solid #555;
	background: #333;
	color: white;
}

button {
	margin-top: 10px;
	background: #0066cc;
	cursor: pointer;
}

button:hover {
	background: #0088ff;
}

.sphere-container {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	z-index: 1;
}

.sphere-container canvas {
	display: block;
	width: 100%;
	height: 100%;
}
</style>
