
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';



fetch('./ne_110m_admin_0_countries.geojson').then(res => res.json()).then(countries =>
	{
		let camera, scene, raycaster, renderer;
		let INTERSECTED;

		const mouse = new THREE.Vector2();

		init();

		function init() {

			camera = new THREE.PerspectiveCamera();
			camera.aspect = window.innerWidth/ window.innerHeight;
			camera.updateProjectionMatrix();
			camera.position.z = 500;

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

			// setTimeout(() => Globe.polygonAltitude(() => Math.random()), 4000);


			// raycaster = new THREE.Raycaster();


			renderer = new THREE.WebGLRenderer();
			renderer.setSize(window.innerWidth, window.innerHeight);
			document.getElementById('globeViz').appendChild(renderer.domElement);


			// Add camera controls
			// const tbControls = new OrbitControls(camera, renderer.domElement);
			// tbControls.minDistance = 101;
			// tbControls.rotateSpeed = 5;
			// tbControls.zoomSpeed = 0.8;

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

			// tbControls.update();

			// raycaster.setFromCamera( pointer, camera );

			// const intersects = raycaster.intersectObjects( scene.children, false );

			// if ( intersects.length > 0 ) {

			// 	if ( INTERSECTED != intersects[ 0 ].object ) {

			// 		if ( INTERSECTED ) INTERSECTED.material.emissive.setHex( INTERSECTED.currentHex );

			// 		INTERSECTED = intersects[ 0 ].object;
			// 		INTERSECTED.currentHex = INTERSECTED.material.emissive.getHex();
			// 		INTERSECTED.material.emissive.setHex( 0xff0000 );

			// 	}

			// } else {

			// 	if ( INTERSECTED ) INTERSECTED.material.emissive.setHex( INTERSECTED.currentHex );

			// 	INTERSECTED = null;

			// }

			renderer.render( scene, camera );
		}
	});