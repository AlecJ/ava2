<script>
export default {
	data() {
		return {
			copySuccess: false,
		};
	},
	methods: {
		copyInviteLink() {
			const inviteLink = `${window.location.origin}/${this.$route.params.sessionId}`;
			navigator.clipboard.writeText(inviteLink).then(() => {
				this.copySuccess = true;

				// Hide the success message 3 seconds
				setTimeout(() => {
					this.copySuccess = false;
				}, 2000);
			});
		},
	},
};
</script>

<template>
	<div class="invite-container">
		<button @click="copyInviteLink" class="invite-button">
			Copy Invite Link
		</button>
		<p v-if="copySuccess" class="copied-text">Link Copied!</p>
	</div>
</template>

<style scoped lang="scss">
.invite-button {
	position: relative;
	padding: 10px 20px;
	background-color: #000000;
	color: white;
	border: none;
	border-radius: 5px;
	cursor: pointer;
	font-size: 16px;
	z-index: 2;
}

.invite-button:hover {
	background-color: #4a4a4a;
}

.copied-text {
	z-index: 1;
	position: absolute;
	left: 50%;
	transform: translateX(-50%) translateY(-200%);
	margin-top: 10px;
	font-size: 16px;
	color: black;
	animation: slideOutFade 2s;
	opacity: 0;

	/* Outline effect */
	text-shadow:
		1px 1px 2px white,
		-1px -1px 2px white,
		1px -1px 2px white,
		-1px 1px 2px white;
}

/* Keyframes for sliding out and fading */
@keyframes slideOutFade {
	0% {
		opacity: 1;
		transform: translateX(-50%) translateY(-200%);
	}
	30% {
		transform: translateX(-50%) translateY(-300%);
	}
	80% {
		opacity: 1;
		transform: translateX(-50%) translateY(-300%); /* Slide up slightly */
	}
	100% {
		opacity: 0;
		transform: translateX(-50%) translateY(-300%); /* Slide further up */
	}
}
</style>
