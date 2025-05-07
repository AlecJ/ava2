import * as THREE from "three";
import fs from "fs";
import { useGlobe } from "@/composables/globe.js";

export function calculateTerritoryCenters() {
	const centers = {};

	const { createCountries } = useGlobe();
	const countries = createCountries().children[0];

	countries.children.forEach((territoryMesh) => {
		const territoryName = territoryMesh.userData?.name;
		if (!territoryName) {
			console.warn("Territory mesh without a name found, skipping.");
			return;
		}

		const vertices = territoryMesh.geometry.attributes.position.array;
		const center = new THREE.Vector3();
		let count = 0;

		// Calculate the center point of the territory
		for (let i = 0; i < vertices.length; i += 3) {
			center.x += vertices[i];
			center.y += vertices[i + 1];
			center.z += vertices[i + 2];
			count++;
		}
		center.divideScalar(count); // Average the vertices
		center.normalize(); // Normalize and scale the center point

		centers[territoryName] = {
			x: center.x,
			y: center.y,
			z: center.z,
		};
	});

	return centers;
}

export function saveTerritoryCentersToFile(
	filePath = "./src/data/territoryCenters.json"
) {
	const centers = calculateTerritoryCenters();
	fs.writeFileSync(filePath, JSON.stringify(centers, null, 2));
	console.log(`Territory centers have been saved to ${filePath}`);
}

saveTerritoryCentersToFile();
