
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';



fetch('./ne_110m_admin_0_countries.geojson').then(res => res.json()).then(countries =>
	{
		let camera, scene, raycaster, renderer, controls;
		let INTERSECTED;

		let storedCountries;


		const mouse = new THREE.Vector2();

		init();

		function init() {

			camera = new THREE.PerspectiveCamera();
			camera.aspect = window.innerWidth/ window.innerHeight;
			camera.updateProjectionMatrix();
			camera.position.z = 300;

			scene = new THREE.Scene();
			scene.add(new THREE.AmbientLight(0xcccccc, Math.PI));
			scene.add(new THREE.DirectionalLight(0xffffff, 0.6 * Math.PI));

			const Globe = new ThreeGlobe()
				.globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
				.polygonsData(countries.features.filter(d => d.properties.ISO_A2 !== 'AQ'))
				.polygonCapColor(() => 'rgba(200, 0, 0, 0.7)')
				.polygonSideColor(() => 'rgba(0, 200, 0, 0.1)')
				.polygonStrokeColor(() => '#111');
			scene.add(Globe);

			// TESTING

			storedCountries = Globe.polygonGeoJsonGeometry();
			console.log(storedCountries);

			// END TESTING

			// setTimeout(() => Globe.polygonAltitude(() => Math.random()), 4000);


			raycaster = new THREE.Raycaster();


			renderer = new THREE.WebGLRenderer();
			renderer.setSize(window.innerWidth, window.innerHeight);
			renderer.setAnimationLoop( animate );
			document.getElementById('globeViz').appendChild(renderer.domElement);


			// Camera controls
			controls = new OrbitControls(camera, renderer.domElement);
			controls.minDistance = 150;
			controls.maxDistance = 500;
			controls.rotateSpeed = 0.5;
			controls.zoomSpeed = 0.8;

			document.addEventListener( 'mousemove', onMouseMove );

			window.addEventListener( 'resize', onWindowResize );

		}

		function onWindowResize() {

			camera.aspect = window.innerWidth / window.innerHeight;
			camera.updateProjectionMatrix();

			renderer.setSize( window.innerWidth, window.innerHeight );

		}

		function onMouseMove( event ) {

			mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
			mouse.y = - ( event.clientY / window.innerHeight ) * 2 + 1;

		}

		function animate() {

			render();

		}

		function render() {

			controls.update();

			raycaster.setFromCamera( mouse, camera );

			console.log(INTERSECTED);
			INTERSECTED = null;

			if ( INTERSECTED != null && INTERSECTED.material ) {
				// console.log(INTERSECTED);
				// INTERSECTED.material.color.set( 'rgba(0, 200, 0, 0.1)' );
				// INTERSECTED = null;
			}

			const intersects = raycaster.intersectObjects( scene.children );			

			if ( intersects.length > 0 &&
				intersects[0].object.type !== "LineSegments" &&
				intersects[0].object?.__globeObjType !== "globe" ) {
				INTERSECTED = intersects[0];
				// INTERSECTED.object.material.color.set( 'rgba(0, 0, 200, 0.1)' );
			}
			else if ( intersects.length > 1 &&
				intersects[1].object.type !== "LineSegments" &&
				intersects[1].object?.__globeObjType !== "globe"  ) {
				INTERSECTED = intersects[1];
				// INTERSECTED.object.material.color.set( 'rgba(0, 0, 200, 0.1)' );
			}

			renderer.render( scene, camera );

		}

	});