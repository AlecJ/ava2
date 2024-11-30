import * as THREE from "three";
// import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// import ThreeGlobe from 'three-globe';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
	75,
	window.innerWidth / window.innerHeight,
	0.1,
	1000
);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

camera.position.z = 5;

function animate() {
	cube.rotation.x += 0.01;
	cube.rotation.y += 0.01;
	renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);

// fetch('./ne_110m_admin_0_countries.geojson').then(res => res.json()).then(countries =>
// {
// 	const Globe = new ThreeGlobe()
// 		.globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
// 		.bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
// 		.polygonsData(countries.features.filter(d => d.properties.ISO_A2 !== 'AQ'))
// 		.polygonCapColor(() => 'rgba(39, 245, 223, 0.4)')
// 		.polygonSideColor(() => 'rgba(0, 200, 0, 0.1)')
// 		.polygonStrokeColor(() => '#111')

// 	// Setup renderer
// 	const renderer = new THREE.WebGLRenderer();
// 	renderer.setSize(window.innerWidth, window.innerHeight);
// 	document.getElementById('globeViz').appendChild(renderer.domElement);

// 	// Setup scene
// 	const scene = new THREE.Scene();
// 	scene.add(Globe);
// 	scene.add(new THREE.AmbientLight(0xcccccc, Math.PI));
// 	scene.add(new THREE.DirectionalLight(0xffffff, 0.6 * Math.PI));

// 	// Setup camera
// 	const camera = new THREE.PerspectiveCamera();
// 	camera.aspect = window.innerWidth/ window.innerHeight;
// 	camera.updateProjectionMatrix();
// 	camera.position.z = 500;

// 	// Add camera controls
// 	const controls = new OrbitControls(camera, renderer.domElement);
// 	controls.minDistance = 160;
// 	controls.rotateSpeed = 1;
// 	controls.zoomSpeed = 0.8;
// 	controls.enablePan = false;

// 	controls.minPolarAngle = 0.25;
// 	controls.maxPolarAngle = Math.PI - 0.5;

// 	function onClick() {

// 		event.preventDefault();

// 		mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
// 		mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

// 		raycaster.setFromCamera(mouse, camera);

// 		var intersects = raycaster.intersectObject(scene, true);

// 		if (intersects.length > 0) {

// 			var object = intersects[0].object;

// 		object.material.color.set( Math.random() * 0xffffff );

// 		}

// 		render();

// 		}

// 	// Kick-off renderer
// 	(function animate() { // IIFE
// 		// Frame cycle
// 		controls.update();
// 		renderer.render(scene, camera);
// 		requestAnimationFrame(animate);
// 	})();
// });

// 			document.addEventListener( 'mousemove', onMouseMove );

// 			window.addEventListener( 'resize', onWindowResize );

// 		function onWindowResize() {

// 			camera.aspect = window.innerWidth / window.innerHeight;
// 			camera.updateProjectionMatrix();

// 			renderer.setSize( window.innerWidth, window.innerHeight );

// 		}

// 		function onMouseMove( event ) {

// 			mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
// 			mouse.y = - ( event.clientY / window.innerHeight ) * 2 + 1;

// 		}
