import * as d3 from "d3";

function createGlobe(globeRadius = 100) {
	const geometry = new THREE.SphereGeometry(globeRadius - 0.5, 64, 64);
	const sphereMaterial = new THREE.MeshBasicMaterial({
		color: 0x529ef7,
		wireframe: false,
	});
	const globe = new THREE.Mesh(geometry, sphereMaterial);

	return globe;
}

function createCountries(globeRadius = 100) {
	const countriesGroup = new THREE.Group();

	d3.json("../triangles.json").then((geoData) => {
		const group = new THREE.Group();

		Object.entries(geoData).forEach(([countryName, countryData]) => {
			const { vertices, polygons, triangles } = countryData;

			const normalizedVertices = [];
			for (let i = 0; i < vertices.length; i += 2) {
				const lon = vertices[i];
				const lat = vertices[i + 1];
				const point = latLongToVector3(lat, lon, globeRadius);
				normalizedVertices.push(point.x, point.y, point.z);
			}

			// Function to convert lat/lon to 3D spherical coordinates
			function latLongToVector3(lat, lon, radius) {
				const phi = (90 - lat) * (Math.PI / 180); // Latitude to phi (polar angle)
				const theta = (lon + 180) * (Math.PI / 180); // Longitude to theta (azimuthal angle)

				// Spherical to Cartesian conversion
				const x = -(radius * Math.sin(phi) * Math.cos(theta));
				const y = radius * Math.cos(phi);
				const z = radius * Math.sin(phi) * Math.sin(theta);

				if (isNaN(x) || isNaN(y) || isNaN(z)) {
					console.error("NaN encountered during transformation:", {
						x,
						y,
						z,
					});
				}

				return new THREE.Vector3(x, y, z);
			}

			// Create the BufferGeometry
			const geometry = new THREE.BufferGeometry();
			geometry.setAttribute(
				"position",
				new THREE.Float32BufferAttribute(normalizedVertices, 3)
			);
			geometry.setIndex(triangles);

			geometry.computeBoundingSphere();

			// Create a material for the country
			const material = new THREE.MeshBasicMaterial({
				color: Math.random() * 0xffffff,
				side: THREE.DoubleSide,
				polygonOffset: true, // Prevent z-fighting
				polygonOffsetFactor: -1,
				polygonOffsetUnits: -1,
			});

			// Store the original color to reset it later
			material.userData = {
				originalColor: material.color.getHex(),
				name: countryName,
			};

			// Create the mesh
			const mesh = new THREE.Mesh(geometry, material);

			mesh.userData = { name: countryName }; // Store country name

			// Add the mesh to the country group
			group.add(mesh);
		});

		countriesGroup.add(group);
	});

	return countriesGroup;
}

export { createGlobe, createCountries };
