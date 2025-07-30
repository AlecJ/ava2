<template>
	<div class="toast-container">
		<TransitionGroup name="toast" tag="div" class="toast-list">
			<div
				v-for="toast in toasts"
				:key="toast.id"
				:class="['toast', `toast--${toast.type}`]"
				@click="removeToast(toast.id)"
			>
				<div class="toast__icon">
					<svg
						v-if="toast.type === 'error'"
						class="toast__svg"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<path
							fill-rule="evenodd"
							d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
							clip-rule="evenodd"
						/>
					</svg>
					<svg
						v-else-if="toast.type === 'success'"
						class="toast__svg"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
							clip-rule="evenodd"
						/>
					</svg>
					<svg
						v-else-if="toast.type === 'warning'"
						class="toast__svg"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<path
							fill-rule="evenodd"
							d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
							clip-rule="evenodd"
						/>
					</svg>
					<svg
						v-else
						class="toast__svg"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<path
							fill-rule="evenodd"
							d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
				<div class="toast__content">
					<p class="toast__message">{{ toast.message }}</p>
				</div>
				<button
					@click.stop="removeToast(toast.id)"
					class="toast__close"
					aria-label="Close notification"
				>
					<svg
						class="toast__close-svg"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<path
							fill-rule="evenodd"
							d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
							clip-rule="evenodd"
						/>
					</svg>
				</button>
			</div>
		</TransitionGroup>
	</div>
</template>

<script>
import { useToastStore } from "@/stores/toast";

export default {
	name: "ToastNotifications",
	setup() {
		const toastStore = useToastStore();

		return {
			toasts: toastStore.activeToasts,
			removeToast: toastStore.removeToast,
		};
	},
};
</script>

<style scoped>
.toast-container {
	position: fixed;
	top: 1rem;
	right: 1rem;
	z-index: 9999;
	pointer-events: none;
}

.toast-list {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
}

.toast {
	display: flex;
	align-items: flex-start;
	gap: 0.75rem;
	max-width: 400px;
	min-width: 300px;
	padding: 1rem;
	border-radius: 0.5rem;
	box-shadow:
		0 10px 15px -3px rgba(0, 0, 0, 0.1),
		0 4px 6px -2px rgba(0, 0, 0, 0.05);
	backdrop-filter: blur(10px);
	cursor: pointer;
	pointer-events: auto;
	transition: all 0.3s ease;
}

.toast:hover {
	transform: translateY(-2px);
	box-shadow:
		0 20px 25px -5px rgba(0, 0, 0, 0.1),
		0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.toast--error {
	background: rgba(239, 68, 68, 0.95);
	color: white;
	border-left: 4px solid #dc2626;
}

.toast--success {
	background: rgba(34, 197, 94, 0.95);
	color: white;
	border-left: 4px solid #16a34a;
}

.toast--warning {
	background: rgba(245, 158, 11, 0.95);
	color: white;
	border-left: 4px solid #d97706;
}

.toast--info {
	background: rgba(59, 130, 246, 0.95);
	color: white;
	border-left: 4px solid #2563eb;
}

.toast__icon {
	flex-shrink: 0;
}

.toast__svg {
	width: 1.25rem;
	height: 1.25rem;
}

.toast__content {
	flex: 1;
	min-width: 0;
}

.toast__message {
	margin: 0;
	font-size: 0.875rem;
	font-weight: 500;
	line-height: 1.25rem;
	word-wrap: break-word;
}

.toast__close {
	flex-shrink: 0;
	background: none;
	border: none;
	color: inherit;
	cursor: pointer;
	opacity: 0.7;
	transition: opacity 0.2s ease;
	padding: 0;
	margin: 0.5rem;
}

.toast__close:hover {
	opacity: 1;
}

.toast__close-svg {
	width: 1rem;
	height: 1rem;
}

/* Transition animations */
.toast-enter-active,
.toast-leave-active {
	transition: all 0.3s ease;
}

.toast-enter-from {
	opacity: 0;
	transform: translateX(100%);
}

.toast-leave-to {
	opacity: 0;
	transform: translateX(100%);
}

.toast-move {
	transition: transform 0.3s ease;
}
</style>
