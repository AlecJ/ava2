import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import * as d3 from "d3";

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
camera.position.z = 15;

// Renderer
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animate);
document.body.appendChild(renderer.domElement);

// Camera controls
const controls = new OrbitControls(camera, renderer.domElement);
// controls.minDistance = 0;
controls.maxDistance = 300;
controls.rotateSpeed = 0.5;
controls.zoomSpeed = 0.8;

// Load GeoJSON and Generate Globe with Countries
createGlobe();

function createGlobe() {
	const globeRadius = 5;
	const geometry = new THREE.SphereGeometry(globeRadius, 64, 64);
	const material = new THREE.MeshBasicMaterial({
		color: 0x660000,
		wireframe: false,
	});
	const globe = new THREE.Mesh(geometry, material);
	scene.add(globe);
	d3.json("./ne_110m_admin_0_countries.geojson").then((geoData) => {
		console.log(geoData.features);
		const group = new THREE.Group();
		geoData.features.forEach((feature) => {
			const coordinates = feature.geometry.coordinates;

			const lineGeometry = new THREE.BufferGeometry();
			const points = [];

			// Create points for the line
			coordinates[0].forEach(([lon, lat]) => {
				if (typeof lat !== "number" || typeof lon !== "number") {
					console.warn("Skipping invalid coordinate:", { lat, lon });
					return; // Skip this iteration
				}
				const point = latLongToVector3(lat, lon, globeRadius + 0.01); // Offset slightly to avoid z-fighting
				points.push(point.x, point.y, point.z); // Push x, y, z coordinates
			});

			// Set points to the BufferGeometry
			lineGeometry.setAttribute(
				"position",
				new THREE.Float32BufferAttribute(points, 3)
			);

			// Create and add the line
			const lineMaterial = new THREE.LineBasicMaterial({
				color: 0x00ff00,
			});
			const line = new THREE.Line(lineGeometry, lineMaterial);
			group.add(line);
			// const shape = new THREE.Shape();
			// coordinates[0].forEach(([lon, lat], index) => {
			// 	const point = latLongToVector3(lat, lon, 6);
			// 	if (index === 0) shape.moveTo(point.x, point.y);
			// 	else shape.lineTo(point.x, point.y);
			// });

			// const geometry = new THREE.ShapeGeometry(shape);
			// const material = new THREE.MeshBasicMaterial({
			// 	color: 0x00ff00,
			// 	side: THREE.DoubleSide,
			// });
			// const mesh = new THREE.Mesh(geometry, material);
			// group.add(mesh);

			// Add interactivity
			// mesh.userData = { country: feature.properties.name };
			// mesh.on("mouseover", () => {
			// 	mesh.material.color.set(0xff0000); // Highlight
			// });
			// mesh.on("mouseout", () => {
			// 	mesh.material.color.set(0x00ff00); // Reset
			// });
		});
		scene.add(group);
	});
}

// Helper for create globe
// Map country geo json data into 3d points on a sphere
function latLongToVector3(lat, lon, radius) {
	const phi = (90 - lat) * (Math.PI / 180);
	const theta = (lon + 180) * (Math.PI / 180);

	const x = -(radius * Math.sin(phi) * Math.cos(theta));
	const y = radius * Math.cos(phi);
	const z = radius * Math.sin(phi) * Math.sin(theta);

	return new THREE.Vector3(x, y, z);
}

function animate() {
	controls.update();
	// cube.rotation.x += 0.01;
	// cube.rotation.y += 0.01;
	renderer.render(scene, camera);
}
