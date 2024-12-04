import * as d3 from "d3";
import earcut from "earcut";

export function createGlobe(scene) {
	const globeRadius = 100;
	const geometry = new THREE.SphereGeometry(globeRadius, 64, 64);
	const material = new THREE.MeshBasicMaterial({
		color: 0x660000,
		wireframe: false,
	});
	const globe = new THREE.Mesh(geometry, material);
	// scene.add(globe);
	// d3.json("../public/ne_110m_admin_0_countries.geojson").then((geoData) => {
	d3.json("../public/ne_110m_admin_0_countries.geojson").then((geoData) => {
		// console.log(geoData.features);

		const group = new THREE.Group();

		// Process each country into a mesh
		geoData.features.forEach((feature) => {
			const geometry = feature.geometry;
			const countryGroup = new THREE.Group(); // Group for the country mesh

			if (geometry.type === "Polygon") {
				// Process single Polygon
				geometry.coordinates.forEach((ring) =>
					processCountry(ring, feature, countryGroup)
				);
			} else if (geometry.type === "MultiPolygon") {
				// Process each Polygon in MultiPolygon
				geometry.coordinates.forEach((polygon) => {
					polygon.forEach((ring) =>
						processCountry(ring, feature, countryGroup)
					);
				});
			} else {
				console.warn("Unsupported geometry type:", geometry.type);
			}

			group.add(countryGroup);
		});

		// Create a 3d mesh from a ring, or array of coordinates
		function processCountry(ring, feature, countryGroup) {
			const points = convertRingToPoints(ring);

			// Flatten the points for Earcut
			const flatPoints = [];
			points.forEach(([x, y, z]) => {
				flatPoints.push(x, y, z);
			});

			// Use Earcut to generate the indices for triangulation
			// const indices = earcut(flatPoints, null, 3); // Use 3 for 3D coordinates

			// Create a BufferGeometry to store the country geometry
			const geometry = new THREE.BufferGeometry();

			// Set the geometry's vertices and indices
			geometry.setAttribute(
				"position",
				new THREE.Float32BufferAttribute(flatPoints, 3)
			);
			geometry.setIndex(indices);

			// Create a material for the country (random color)
			const material = new THREE.MeshBasicMaterial({
				color: Math.random() * 0xffffff,
				side: THREE.DoubleSide, // Both sides of the polygon will be visible
				polygonOffset: true, // Prevent z-fighting
				polygonOffsetFactor: -1,
				polygonOffsetUnits: -1,
			});

			// Store the original color to reset it later
			material.userData = { originalColor: material.color.getHex() };

			// Create the mesh using the geometry and material
			const mesh = new THREE.Mesh(geometry, material);
			mesh.userData = { name: feature.properties.NAME }; // Store country name

			// Add the mesh to the country group
			countryGroup.add(mesh);

			// Function to convert lat/lon to 3D vector on the globe's surface
			function convertRingToPoints(ring) {
				const listOfPoints = [];

				ring.forEach(([lon, lat]) => {
					// Convert lat/lon to 3D spherical coordinates on the globe surface
					const point = latLongToVector3(
						lat,
						lon,
						globeRadius + 0.01
					); // Slightly offset from the sphere surface
					listOfPoints.push([point.x, point.y, point.z]); // Store the x, y, z coordinates
				});

				return listOfPoints;
			}

			// Function to convert lat/lon to 3D spherical coordinates
			function latLongToVector3(lat, lon, radius) {
				const phi = (90 - lat) * (Math.PI / 180); // Latitude to phi (polar angle)
				const theta = (lon + 180) * (Math.PI / 180); // Longitude to theta (azimuthal angle)

				// Spherical to Cartesian conversion
				const x = -(radius * Math.sin(phi) * Math.cos(theta));
				const y = radius * Math.cos(phi);
				const z = radius * Math.sin(phi) * Math.sin(theta);

				return new THREE.Vector3(x, y, z);
			}
		}

		scene.add(group);
	});
}
