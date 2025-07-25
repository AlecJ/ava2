import { createRouter, createWebHistory } from "vue-router";
import GameView from "@/views/GameView.vue";

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: "/:sessionId?",
			name: "home",
			component: GameView,
		},
		{
			path: "/territory-editor",
			name: "territory-editor",
			component: () => import("@/components/TerritoryCenterEditor.vue"),
		},
	],
});

export default router;
