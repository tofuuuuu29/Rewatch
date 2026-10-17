<script setup lang="ts">
import PosterCard from '@/components/PosterCard.vue'
import type {MediaConfig, MediaItem} from '@/types/index.ts'

defineProps<{
	cfg: MediaConfig
	items: MediaItem[]
	loading: boolean
	canEdit: boolean // admins can rename / delete titles
	isListed: (id: number) => boolean // is this title already on my list?
}>()

defineEmits<{
	track: [item: MediaItem]
	edit: [item: MediaItem]
	remove: [item: MediaItem]
}>()
</script>

<template>
	<p v-if="loading" class="py-16 text-center text-white/50">Loading...</p>
	<div v-else-if="!items.length" class="panel px-6 py-16 text-center">
		<p class="display text-2xl">Nothing here yet</p>
		<p class="mt-2 text-sm text-white/50">Use the Add button to add the first title.</p>
	</div>

	<div v-else class="stagger grid grid-cols-2 gap-4 sm:grid-cols-3 sm:gap-5 lg:grid-cols-4 xl:grid-cols-5">
		<PosterCard v-for="item in items" :key="item.id" :title="String(item[cfg.nameField])"
					:category="cfg.key" :label="cfg.singular" :poster="item.poster_url">
			<template #top>
				<span v-if="isListed(item.id)"
					  class="rounded-full bg-green-400/90 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-green-950">
					On my list
				</span>
			</template>
			<template #actions>
				<button v-if="!isListed(item.id)" type="button" @click="$emit('track', item)"
						class="rounded-full bg-accent px-3.5 py-1.5 text-xs font-bold text-accent-ink transition hover:brightness-110">
					+ My list
				</button>
				<template v-if="canEdit">
					<button type="button" @click="$emit('edit', item)" class="btn-chip backdrop-blur">Edit</button>
					<button type="button" @click="$emit('remove', item)" class="btn-chip-danger backdrop-blur">Delete</button>
				</template>
			</template>
		</PosterCard>
	</div>
</template>
