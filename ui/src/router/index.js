import { createRouter, createWebHistory } from "vue-router";
import GlobeView from "../views/GlobeView.vue";

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: "/:sessionId?",
			name: "home",
			component: GlobeView,
		},
	],
});

export default router;
