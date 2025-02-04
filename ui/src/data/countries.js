export const countries = [
	{
		name: "USA",
		flagIcon: new URL(
			"@/assets/flags/united-states-of-america.png",
			import.meta.url
		).href,
		color: 0x738326,
	},
	{
		name: "UK",
		flagIcon: new URL("@/assets/flags/united-kingdom.png", import.meta.url)
			.href,
		color: 0xc5b99b,
	},
	{
		name: "USSR",
		flagIcon: new URL("@/assets/flags/soviet-union.png", import.meta.url)
			.href,
		color: 0x7d4932,
	},
	{
		name: "Germany",
		flagIcon: new URL("@/assets/flags/germany.png", import.meta.url).href,
		color: 0x767a73,
	},
	{
		name: "Japan",
		flagIcon: new URL("@/assets/flags/japan.png", import.meta.url).href,
		color: 0xc78940,
	},
];
