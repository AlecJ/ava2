import { defineStore } from "pinia";

export const useToastStore = defineStore("toast", {
	state: () => ({
		toasts: [],
		nextId: 1,
	}),

	actions: {
		addToast(message, type = "error", duration = 4000) {
			const toast = {
				id: this.nextId++,
				message,
				type, // 'error', 'success', 'warning', 'info'
				duration,
				timestamp: Date.now(),
			};

			this.toasts.push(toast);

			// Auto-remove after duration
			setTimeout(() => {
				this.removeToast(toast.id);
			}, duration);

			return toast.id;
		},

		removeToast(id) {
			const index = this.toasts.findIndex((toast) => toast.id === id);
			if (index > -1) {
				this.toasts.splice(index, 1);
			}
		},

		clearAll() {
			this.toasts = [];
		},

		// Convenience methods
		error(message, duration) {
			return this.addToast(message, "error", duration);
		},

		success(message, duration) {
			return this.addToast(message, "success", duration);
		},

		warning(message, duration) {
			return this.addToast(message, "warning", duration);
		},

		info(message, duration) {
			return this.addToast(message, "info", duration);
		},
	},

	getters: {
		activeToasts: (state) => state.toasts,
	},
});
