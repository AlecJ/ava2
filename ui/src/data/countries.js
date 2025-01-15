export const countries = [
	{
		name: "USA",
		flagIcon: new URL(
			"@/assets/flags/united-states-of-america.png",
			import.meta.url
		).href,
	},
	{
		name: "UK",
		flagIcon: new URL("@/assets/flags/united-kingdom.png", import.meta.url)
			.href,
	},
	{
		name: "USSR",
		flagIcon: new URL("@/assets/flags/soviet-union.png", import.meta.url)
			.href,
	},
	{
		name: "Germany",
		flagIcon: new URL("@/assets/flags/germany.png", import.meta.url).href,
	},
	{
		name: "Japan",
		flagIcon: new URL("@/assets/flags/japan.png", import.meta.url).href,
	},
];
