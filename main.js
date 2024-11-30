import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import * as d3 from "d3";

// let globe, scene, camera;
const scene = new THREE.Scene();
// scene.add(new THREE.AmbientLight(0xcccccc, Math.PI));
// scene.add(new THREE.DirectionalLight(0xffffff, 0.6 * Math.PI));

const camera = new THREE.PerspectiveCamera(
	75,
	window.innerWidth / window.innerHeight,
	0.1,
	1000
);

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

// const geometry = new THREE.BoxGeometry(1, 1, 1);
// const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
// const cube = new THREE.Mesh(geometry, material);
// scene.add(cube);

camera.position.z = 15;

// Load GeoJSON
createGlobe();

function createGlobe() {
	const globeRadius = 5;
	const geometry = new THREE.SphereGeometry(globeRadius, 64, 64);
	const material = new THREE.MeshBasicMaterial({
		color: 0xaaaaaa,
		wireframe: false,
	});
	const globe = new THREE.Mesh(geometry, material);
	scene.add(globe);
	d3.json("./ne_110m_admin_0_countries.geojson").then((geoData) => {
		// const group = new THREE.Group();
		// geoData.features.forEach((feature) => {
		// 	const coordinates = feature.geometry.coordinates;
		// 	const shape = new THREE.Shape();
		// 	coordinates[0].forEach(([lon, lat], index) => {
		// 		const point = latLongToVector3(lat, lon, globeRadius);
		// 		if (index === 0) shape.moveTo(point.x, point.y);
		// 		else shape.lineTo(point.x, point.y);
		// 	});
		// 	const geometry = new THREE.ShapeGeometry(shape);
		// 	const material = new THREE.MeshBasicMaterial({
		// 		color: 0x00ff00,
		// 		side: THREE.DoubleSide,
		// 	});
		// 	const mesh = new THREE.Mesh(geometry, material);
		// 	group.add(mesh);
		// 	// Add interactivity
		// 	mesh.userData = { country: feature.properties.name };
		// 	mesh.on("mouseover", () => {
		// 		mesh.material.color.set(0xff0000); // Highlight
		// 	});
		// 	mesh.on("mouseout", () => {
		// 		mesh.material.color.set(0x00ff00); // Reset
		// 	});
		// });
		// scene.add(group);
	});
}

function animate() {
	controls.update();
	// cube.rotation.x += 0.01;
	// cube.rotation.y += 0.01;
	renderer.render(scene, camera);
}
