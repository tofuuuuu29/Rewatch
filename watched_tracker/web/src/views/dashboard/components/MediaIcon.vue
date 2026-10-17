<script setup lang="ts">
defineProps<{kind: string}>()
</script>

<template>
	<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
		 stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
		<!-- my list: grid -->
		<template v-if="kind === 'mylist'">
			<rect width="7" height="7" x="3" y="3" rx="1" />
			<rect width="7" height="7" x="14" y="3" rx="1" />
			<rect width="7" height="7" x="14" y="14" rx="1" />
			<rect width="7" height="7" x="3" y="14" rx="1" />
		</template>

		<!-- movies: clapperboard -->
		<template v-else-if="kind === 'movies'">
			<path d="M20.2 6 3 11l-.9-2.4c-.3-1.1.3-2.2 1.3-2.5l13.5-4c1.1-.3 2.2.3 2.5 1.3Z" />
			<path d="m6.2 5.3 3.1 3.9" />
			<path d="m12.4 3.4 3.1 4" />
			<path d="M3 11h18v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
		</template>

		<!-- anime: tv with antenna -->
		<template v-else-if="kind === 'anime'">
			<rect width="20" height="15" x="2" y="7" rx="2" ry="2" />
			<polyline points="17 2 12 7 7 2" />
		</template>

		<!-- k-drama: heart -->
		<template v-else-if="kind === 'kdrama'">
			<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
		</template>

		<!-- tv series: screen with a play button -->
		<template v-else-if="kind === 'tvseries'">
			<rect x="2" y="3" width="20" height="14" rx="2" />
			<path d="M10 7.75a.75.75 0 0 1 1.142-.638l3.664 2.249a.75.75 0 0 1 0 1.276l-3.664 2.249A.75.75 0 0 1 10 12.249z" />
			<path d="M12 17v4" />
			<path d="M8 21h8" />
		</template>

		<!-- completed: check in a circle -->
		<template v-else-if="kind === 'check'">
			<circle cx="12" cy="12" r="10" />
			<path d="m9 12 2 2 4-4" />
		</template>

		<!-- watching: eye -->
		<template v-else-if="kind === 'eye'">
			<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" />
			<circle cx="12" cy="12" r="3" />
		</template>

		<!-- rating: star -->
		<template v-else-if="kind === 'star'">
			<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z" />
		</template>
	</svg>
</template>