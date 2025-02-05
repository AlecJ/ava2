<script>
export default {
	props: {
		width: {
			type: String,
			required: false,
			default: "75%",
		},
		height: {
			type: String,
			required: false,
			default: "75%",
		},
	},
};
</script>

<template>
	<div
		id="popup"
		:style="{
			width,
			height,
			top: `calc(50% - ${height} / 2)`,
			left: `calc(50% - ${width} / 2)`,
		}"
	>
		<slot></slot>
	</div>
</template>

<style scoped lang="scss">
#popup {
	position: fixed;
	overflow: hidden;
	z-index: 1;

	display: grid;
	place-items: center;

	background-color: rgba(88, 88, 88, 0.663);
	border: 0.15rem solid gray;
	border-radius: 0.5rem;
}
</style>
