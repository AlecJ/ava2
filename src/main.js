import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createGlobe } from "./globe.js";

// Scene
const scene = new THREE.Scene();
// scene.add(new THREE.AmbientLight(0xcccccc, Math.PI));
// scene.add(new THREE.DirectionalLight(0xffffff, 0.6 * Math.PI));

// Camera
const camera = new THREE.PerspectiveCamera(
	75,
	window.innerWidth / window.innerHeight,
	0.1,
	1000
);
camera.position.z = 300;

// Renderer
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animate);
document.body.appendChild(renderer.domElement);

// Camera controls
const controls = new OrbitControls(camera, renderer.domElement);
// controls.minDistance = 0;
controls.maxDistance = 500;
controls.rotateSpeed = 0.5;
controls.zoomSpeed = 0.8;

const globe = createGlobe(scene);

// Add raycasting logic
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let currentHoveredCountry = null; // Track currently hovered country

function onPointerMove(event) {
	// Calculate pointer position in normalized device coordinates (-1 to +1)
	pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
	pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

function onClick(event) {
	// Use raycasting to find the clicked country
	raycaster.setFromCamera(pointer, camera); // Set the ray from the camera

	// Get the intersected objects (countries)
	const intersects = raycaster.intersectObjects(scene.children);

	if (intersects.length > 0) {
		// Get the first intersected country
		const country = intersects[0].object;

		// Log the country name
		console.log("Clicked country:", country.userData.name);
	}
}

function checkForPointerTarget() {
	// Find objects intersecting the ray
	const intersects = raycaster.intersectObjects(scene.children);

	// If a country is hovered
	if (intersects.length > 0) {
		const country = intersects[0].object;

		// Highlight the country if it's not the current hovered country
		if (country !== currentHoveredCountry) {
			// Reset the previous hovered country's color
			if (currentHoveredCountry) {
				currentHoveredCountry.material.color.set(
					currentHoveredCountry.material.userData.originalColor
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
}

// Add this function to handle resizing
function onWindowResize() {
	// Update camera aspect ratio and projection matrix
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();

	// Update renderer size
	renderer.setSize(window.innerWidth, window.innerHeight);

	// Optionally, update any other elements dependent on screen size
}

// Event Listeners for mouse and window
window.addEventListener("pointermove", onPointerMove, false);
window.addEventListener("click", onClick, false);
window.addEventListener("resize", onWindowResize);

function animate() {
	controls.update();
	// update the picking ray with the camera and pointer position
	raycaster.setFromCamera(pointer, camera);

	checkForPointerTarget();
	// cube.rotation.x += 0.01;
	// cube.rotation.y += 0.01;
	renderer.render(scene, camera);
}
