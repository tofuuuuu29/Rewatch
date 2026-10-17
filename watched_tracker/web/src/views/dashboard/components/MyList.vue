<script setup lang="ts">
import {computed, ref} from 'vue'
import {site, statusLabel} from '@/config/site.ts'
import PosterCard from '@/components/PosterCard.vue'
import SearchBox from '@/components/SearchBox.vue'
import type {WatchEntry, WatchStatus} from '@/types/index.ts'

const props = defineProps<{
	entries: WatchEntry[]
	loading: boolean
}>()

defineEmits<{
	edit: [entry: WatchEntry]
	remove: [entry: WatchEntry]
	status: [entry: WatchEntry, status: WatchStatus]
}>()

const filter = ref<'all' | WatchStatus>('all')
const search = ref('')

const countOf = (status: WatchStatus) => props.entries.filter((e) => e.status === status).length

const visible = computed(() => {
	const q = search.value.trim().toLowerCase()
	return props.entries.filter(
		(e) =>
			(filter.value === 'all' || e.status === filter.value) &&
			(!q || (e.media?.title ?? '').toLowerCase().includes(q))
	)
})

const suggestions = computed(() =>
	props.entries.map((e) => ({label: e.media?.title ?? '', hint: categoryLabel(e.media?.category)})).filter((o) => o.label)
)

const categoryLabel = (key?: string) => site.media.find((m) => m.key === key)?.singular ?? '-'
const badge = (status: string) => site.statuses.find((s) => s.key === status)?.badge ?? ''

const progress = (e: WatchEntry) => {
	if (e.season && e.episode) return `S${e.season} · E${e.episode}`
	if (e.season) return `S${e.season}`
	if (e.episode) return `E${e.episode}`
	return '-'
}
</script>

<template>
	<!-- status filter + search -->
	<div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
		<div class="-mx-4 overflow-x-auto px-4 lg:mx-0 lg:px-0">
			<div class="inline-flex gap-2">
				<button type="button" @click="filter = 'all'"
						class="whitespace-nowrap rounded-full border px-4 py-2 text-xs font-semibold transition"
						:class="filter === 'all' ? 'border-accent bg-accent text-accent-ink' : 'border-white/10 text-white/60 hover:border-white/30 hover:text-white'">
					All {{ entries.length }}
				</button>
				<button v-for="s in site.statuses" :key="s.key" type="button" @click="filter = s.key"
						class="whitespace-nowrap rounded-full border px-4 py-2 text-xs font-semibold transition"
						:class="filter === s.key ? 'border-accent bg-accent text-accent-ink' : 'border-white/10 text-white/60 hover:border-white/30 hover:text-white'">
					{{ s.label }} {{ countOf(s.key) }}
				</button>
			</div>
		</div>

		<SearchBox v-model="search" placeholder="Search my list..." :options="suggestions" />
	</div>

	<p v-if="loading" class="py-16 text-center text-white/50">Loading...</p>
	<div v-else-if="!entries.length" class="panel mt-6 px-6 py-16 text-center">
		<p class="display text-2xl">Your list is empty</p>
		<p class="mt-2 text-sm text-white/50">
			Open Movies, Anime, K-Drama or TV Series and press <span class="font-semibold text-accent">+ My list</span>.
		</p>
	</div>
	<p v-else-if="!visible.length" class="py-16 text-center text-white/50">No matches.</p>

	<div v-else class="stagger mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 sm:gap-5 lg:grid-cols-4 xl:grid-cols-5">
		<PosterCard v-for="e in visible" :key="e.id" :title="e.media?.title ?? 'Unknown title'"
					:category="e.media?.category" :label="categoryLabel(e.media?.category)"
					:poster="e.media?.poster_url">
			<template #top>
				<select :value="e.status" :aria-label="`Status of ${e.media?.title}`"
						@change="(ev) => $emit('status', e, (ev.target as HTMLSelectElement).value as WatchStatus)"
						class="min-w-0 flex-1 cursor-pointer truncate rounded-full border-0 px-2 py-1 text-[10px] font-bold uppercase tracking-wide outline-none backdrop-blur sm:flex-none sm:px-2.5"
						:class="badge(e.status)">
					<option v-for="s in site.statuses" :key="s.key" :value="s.key" class="bg-ink text-white">{{ statusLabel(s.key) }}</option>
				</select>
				<span v-if="e.rating !== null"
					  class="shrink-0 rounded-full bg-black/55 px-2.5 py-1 text-xs font-bold text-accent backdrop-blur">
					&#9733; {{ e.rating }}
				</span>
			</template>
			<template #meta>
				<p v-if="progress(e) !== '-'" class="mt-1 text-xs font-medium text-white/60">{{ progress(e) }}</p>
				<p v-if="e.notes" class="mt-1 line-clamp-2 text-xs italic text-white/50">&ldquo;{{ e.notes }}&rdquo;</p>
			</template>
			<template #actions>
				<button type="button" @click="$emit('edit', e)" class="btn-chip backdrop-blur">Edit</button>
				<button type="button" @click="$emit('remove', e)" class="btn-chip-danger backdrop-blur">Remove</button>
			</template>
		</PosterCard>
	</div>
</template>