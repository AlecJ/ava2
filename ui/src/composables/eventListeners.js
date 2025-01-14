// Event Listeners for mouse and window

export function createWindowResizeListener(camera, renderer) {
	function onWindowResize() {
		// Update camera aspect ratio and projection matrix
		renderer.setSize(window.innerWidth, window.innerHeight);
		camera.aspect = window.innerWidth / window.innerHeight;
		camera.updateProjectionMatrix();
	}

	return {
		enable: () => window.addEventListener("resize", onWindowResize),
		disable: () => window.removeEventListener("resize", onWindowResize),
	};
}

export function createPointerMoveListener(pointer) {
	function onPointerMove(event) {
		// Calculate pointer position in normalized device coordinates (-1 to +1)
		pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
		pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
	}

	return {
		enable: () =>
			window.addEventListener("pointermove", onPointerMove, false),
		disable: () =>
			window.removeEventListener("pointermove", onPointerMove, false),
	};
}
