// Event Listeners for mouse and window

export default function initListeners(camera, renderer, pointer, raycaster) {
	function onWindowResize() {
		// Update camera aspect ratio and projection matrix
		camera.aspect = window.innerWidth / window.innerHeight;
		camera.updateProjectionMatrix();

		// Update renderer size
		renderer.setSize(window.innerWidth, window.innerHeight);
	}

	function onPointerMove(event) {
		// Calculate pointer position in normalized device coordinates (-1 to +1)
		pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
		pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
	}

	// window.addEventListener("pointermove", onPointerMove, false);
	// window.addEventListener("click", onClick, false);
	window.addEventListener("resize", onWindowResize);
}
