import * as THREE from "three";

import { Line2 } from "three/examples/jsm/lines/Line2.js";
import { LineMaterial } from "three/examples/jsm/lines/LineMaterial.js";
import { LineGeometry } from "three/examples/jsm/lines/LineGeometry.js";

import tileData from "@/data/territories.json" assert { type: "json" };
import geoData from "@/data/triangles.json" assert { type: "json" };

// country colors
const german_color = 0x767a73;
const united_states_color = 0x738326;
const united_kingdom_color = 0xc5b99b;
const russia_color = 0x7d4932;
const japan_color = 0xc78940;

const countryColors = [
	united_states_color,
	united_kingdom_color,
	russia_color,
	german_color,
	japan_color,
];

export function useGlobe() {
	function createGlobe(globeRadius = 100) {
		const geometry = new THREE.SphereGeometry(globeRadius - 1, 64, 64);
		const sphereMaterial = new THREE.MeshBasicMaterial({
			color: 0x529ef7,
			wireframe: false,
		});
		const globe = new THREE.Mesh(geometry, sphereMaterial);

		return globe;
	}

	function createCountries(globeRadius = 100) {
		const countriesGroup = new THREE.Group();

		const group = new THREE.Group();

		Object.entries(geoData).forEach(([countryName, countryData]) => {
			const { vertices, polygons, triangles, is_ocean_tile } =
				countryData;

			const dataForTile = tileData[countryName];
			const { team } = dataForTile;

			const normalizedVertices = [];
			for (let i = 0; i < vertices.length; i += 2) {
				const lon = vertices[i];
				const lat = vertices[i + 1];
				const point = latLongToVector3(lat, lon, globeRadius);
				normalizedVertices.push(point.x, point.y, point.z);
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
				transparent: true,
				opacity: 0, // Make the mesh invisible
				side: THREE.FrontSide,
				polygonOffset: true, // Prevent z-fighting
				polygonOffsetFactor: 1,
				polygonOffsetUnits: 1,
			});

			// set country tile colors
			if (!is_ocean_tile) {
				if (team === -1) {
					material.color.set(0xc5c6c2);
				} else {
					const countryColor = countryColors[team];
					material.color.set(countryColor);
				}
				material.opacity = 1; // Make the mesh visible
			}

			// Store the original color to reset it later
			material.userData = {
				originalColor: material.color.getHex(),
				name: countryName,
			};

			// Create the mesh
			const mesh = new THREE.Mesh(geometry, material);

			// #region CURRENT
			// // Find boundary edges
			// const boundaryEdges = findBoundaryEdges(geometry);

			// // Create a geometry for the boundary edges
			// const outlineGeometry = new THREE.BufferGeometry();
			// outlineGeometry.setAttribute(
			// 	"position",
			// 	new THREE.Float32BufferAttribute(normalizedVertices, 3)
			// );
			// outlineGeometry.setIndex(boundaryEdges);

			// // Create a material for the outline
			// const outlineMaterial = new THREE.LineBasicMaterial({
			// 	color: 0xffffff, // White color
			// 	linewidth: 2, // Line width
			// });

			// // Create the outline mesh
			// const outline = new THREE.LineSegments(
			// 	outlineGeometry,
			// 	outlineMaterial
			// );

			// // Add the mesh and outline to the country group
			// mesh.add(outline); // Add outline as a child of the mesh
			// #endregion

			// Find boundary edges
			const boundaryEdges = findBoundaryEdges(geometry);

			// Create a geometry for the boundary edges
			const outlineGeometry = new THREE.BufferGeometry();

			// Use the original geometry's vertices for outlineGeometry
			const originalVertices = geometry.attributes.position.array;
			outlineGeometry.setAttribute(
				"position",
				new THREE.Float32BufferAttribute(originalVertices, 3)
			);

			// Set the boundary edges as the index for outlineGeometry
			outlineGeometry.setIndex(boundaryEdges);

			// Create a material for the outline
			const outlineMaterial = new THREE.LineBasicMaterial({
				color: 0xffffff, // White color
				linewidth: 2, // Line width
			});

			// Create the outline mesh
			const outline = new THREE.LineSegments(
				outlineGeometry,
				outlineMaterial
			);

			// Add the mesh and outline to the country group
			mesh.add(outline); // Add outline as a child of the mesh

			mesh.userData = { name: countryName, outline };

			// Add the mesh to the country group
			group.add(mesh);
		});

		countriesGroup.add(group);

		return countriesGroup;
	}

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

	// Helper function to find boundary edges
	function findBoundaryEdges(geometry) {
		const edgeCounts = new Map(); // Map to count how many times each edge appears
		const indices = geometry.index.array; // Get the indices of the triangles

		// Iterate through the triangles
		for (let i = 0; i < indices.length; i += 3) {
			const v0 = indices[i];
			const v1 = indices[i + 1];
			const v2 = indices[i + 2];

			// Create edges for the triangle (order matters to avoid duplicate keys)
			const edge1 = `${Math.min(v0, v1)}-${Math.max(v0, v1)}`;
			const edge2 = `${Math.min(v1, v2)}-${Math.max(v1, v2)}`;
			const edge3 = `${Math.min(v2, v0)}-${Math.max(v2, v0)}`;

			// Count each edge
			edgeCounts.set(edge1, (edgeCounts.get(edge1) || 0) + 1);
			edgeCounts.set(edge2, (edgeCounts.get(edge2) || 0) + 1);
			edgeCounts.set(edge3, (edgeCounts.get(edge3) || 0) + 1);
		}

		// Collect edges that appear only once (boundary edges)
		const boundaryEdges = [];
		for (const [edge, count] of edgeCounts.entries()) {
			if (count === 1) {
				const [v0, v1] = edge.split("-").map(Number);
				boundaryEdges.push(v0, v1);
			}
		}

		return boundaryEdges;
	}

	return {
		createGlobe,
		createCountries,
	};
}
