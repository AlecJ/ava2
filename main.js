
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import * as d3 from 'd3';

// let globe, scene, camera;
const scene = new THREE.Scene();

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);

camera = new THREE.PerspectiveCamera();
camera.aspect = window.innerWidth/ window.innerHeight;
camera.updateProjectionMatrix();
camera.position.z = 300;

// Load GeoJSON
d3.json('./ne_110m_admin_0_countries.geojson').then((data) => {
    createGlobe(data);
});

function createGlobe(data) {
	const globeRadius = 5;
	const geometry = new THREE.SphereGeometry(globeRadius, 64, 64);
	const material = new THREE.MeshBasicMaterial({ 
		color: 0xaaaaaa, 
		wireframe: false 
	});
	const globe = new THREE.Mesh(geometry, material);
	scene.add(globe);

	const group = new THREE.Group();

    geoData.features.forEach((feature) => {
        const coordinates = feature.geometry.coordinates;
        const shape = new THREE.Shape();

        coordinates[0].forEach(([lon, lat], index) => {
            const point = latLongToVector3(lat, lon, globeRadius);
            if (index === 0) shape.moveTo(point.x, point.y);
            else shape.lineTo(point.x, point.y);
        });

        const geometry = new THREE.ShapeGeometry(shape);
        const material = new THREE.MeshBasicMaterial({ 
            color: 0x00ff00, 
            side: THREE.DoubleSide 
        });
        const mesh = new THREE.Mesh(geometry, material);

        group.add(mesh);

        // Add interactivity
        mesh.userData = { country: feature.properties.name };
        mesh.on('mouseover', () => {
            mesh.material.color.set(0xff0000); // Highlight
        });
        mesh.on('mouseout', () => {
            mesh.material.color.set(0x00ff00); // Reset
        });
    });

    scene.add(group);
}

function latLongToVector3(lat, lon, radius) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);

    const x = -(radius * Math.sin(phi) * Math.cos(theta));
    const z = radius * Math.sin(phi) * Math.sin(theta);
    const y = radius * Math.cos(phi);

    return new THREE.Vector3(x, y, z);
}

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onMouseMove(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        const countryMesh = intersects[0].object;
        countryMesh.material.color.set(0xff0000); // Highlight on hover
    }
}

window.addEventListener('mousemove', onMouseMove, false);

function animate() {
    requestAnimationFrame(animate);

    // Rotate the globe for a dynamic effect
    // globe.rotation.y += 0.005;

    renderer.render(scene, camera);
}

animate();


// fetch().then(res => res.json()).then(countries =>
// 	{
// 		let camera, scene, raycaster, renderer, controls;
// 		let INTERSECTED;

// 		let storedCountries;


// 		const mouse = new THREE.Vector2();

// 		init();

// 		function init() {

// 			camera = new THREE.PerspectiveCamera();
// 			camera.aspect = window.innerWidth/ window.innerHeight;
// 			camera.updateProjectionMatrix();
// 			camera.position.z = 300;

// 			scene = new THREE.Scene();
// 			scene.add(new THREE.AmbientLight(0xcccccc, Math.PI));
// 			scene.add(new THREE.DirectionalLight(0xffffff, 0.6 * Math.PI));

// 			const Globe = new ThreeGlobe()
// 				.globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
// 				.polygonsData(countries.features.filter(d => d.properties.ISO_A2 !== 'AQ'))
// 				.polygonCapColor(() => 'rgba(200, 0, 0, 0.7)')
// 				.polygonSideColor(() => 'rgba(0, 200, 0, 0.1)')
// 				.polygonStrokeColor(() => '#111');
// 			scene.add(Globe);

// 			// TESTING

// 			storedCountries = Globe.polygonGeoJsonGeometry();
// 			console.log(storedCountries);

// 			// END TESTING

// 			// setTimeout(() => Globe.polygonAltitude(() => Math.random()), 4000);


// 			raycaster = new THREE.Raycaster();


// 			renderer = new THREE.WebGLRenderer();
// 			renderer.setSize(window.innerWidth, window.innerHeight);
// 			renderer.setAnimationLoop( animate );
// 			document.getElementById('globeViz').appendChild(renderer.domElement);


// 			// Camera controls
// 			controls = new OrbitControls(camera, renderer.domElement);
// 			controls.minDistance = 150;
// 			controls.maxDistance = 500;
// 			controls.rotateSpeed = 0.5;
// 			controls.zoomSpeed = 0.8;

// 			document.addEventListener( 'mousemove', onMouseMove );

// 			window.addEventListener( 'resize', onWindowResize );

// 		}

// 		function onWindowResize() {

// 			camera.aspect = window.innerWidth / window.innerHeight;
// 			camera.updateProjectionMatrix();

// 			renderer.setSize( window.innerWidth, window.innerHeight );

// 		}

// 		function onMouseMove( event ) {

// 			mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
// 			mouse.y = - ( event.clientY / window.innerHeight ) * 2 + 1;

// 		}

// 		function animate() {

// 			render();

// 		}

// 		function render() {

// 			controls.update();

// 			raycaster.setFromCamera( mouse, camera );

// 			console.log(INTERSECTED);
// 			INTERSECTED = null;

// 			if ( INTERSECTED != null && INTERSECTED.material ) {
// 				// console.log(INTERSECTED);
// 				// INTERSECTED.material.color.set( 'rgba(0, 200, 0, 0.1)' );
// 				// INTERSECTED = null;
// 			}

// 			const intersects = raycaster.intersectObjects( scene.children );			

// 			if ( intersects.length > 0 &&
// 				intersects[0].object.type !== "LineSegments" &&
// 				intersects[0].object?.__globeObjType !== "globe" ) {
// 				INTERSECTED = intersects[0];
// 				// INTERSECTED.object.material.color.set( 'rgba(0, 0, 200, 0.1)' );
// 			}
// 			else if ( intersects.length > 1 &&
// 				intersects[1].object.type !== "LineSegments" &&
// 				intersects[1].object?.__globeObjType !== "globe"  ) {
// 				INTERSECTED = intersects[1];
// 				// INTERSECTED.object.material.color.set( 'rgba(0, 0, 200, 0.1)' );
// 			}

// 			renderer.render( scene, camera );

// 		}

// 	});