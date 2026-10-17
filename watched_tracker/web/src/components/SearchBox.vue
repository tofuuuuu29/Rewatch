<script setup lang="ts">
import axios from 'axios'
import {computed, onBeforeUnmount, reactive, ref, watch} from 'vue'
import {errorMessage} from '@/utils/errors.ts'
import type {DiscoverResult} from '@/types/index.ts'

export interface Suggestion {
	label: string
	hint?: string // small grey text on the right, e.g. the category
}

const props = defineProps<{
	modelValue: string
	options: Suggestion[] // titles that are already in the tracker
	placeholder: string
	createLabel?: string // e.g. "Movie": shows an "Add ... as new Movie" row when nothing matches exactly
	// optional online search (TMDB / MyAnimeList). Without it the box only suggests your own titles.
	remote?: (query: string, signal: AbortSignal) => Promise<DiscoverResult[]>
}>()

const emit = defineEmits<{
	'update:modelValue': [value: string]
	pick: [label: string]
	pickRemote: [result: DiscoverResult]
	create: [query: string]
}>()

const open = ref(false)
const active = ref(-1)
const uid = `sb-${Math.random().toString(36).slice(2, 8)}`

const query = computed(() => props.modelValue.trim().toLowerCase())

// ---------- your own titles ----------
// titles that start with the text come first, then titles that contain it
const matches = computed(() => {
	const q = query.value
	if (!q) return []
	const starts: Suggestion[] = []
	const contains: Suggestion[] = []
	for (const o of props.options) {
		const l = o.label.toLowerCase()
		if (l.startsWith(q)) starts.push(o)
		else if (l.includes(q)) contains.push(o)
	}
	return [...starts, ...contains].slice(0, props.remote ? 4 : 6)
})

// ---------- online results (typing waits a moment, old searches are cancelled) ----------
const online = ref<DiscoverResult[]>([])
const onlineLoading = ref(false)
const onlineError = ref('')
const searchedFor = ref('') // the text the current online results belong to

let timer: ReturnType<typeof setTimeout> | undefined
let controller: AbortController | undefined
let seq = 0

const stopSearch = () => {
	clearTimeout(timer)
	controller?.abort()
	seq++
}

const runSearch = async (text: string) => {
	if (!props.remote) return
	const mine = ++seq
	controller = new AbortController()

	try {
		const results = await props.remote(text, controller.signal)
		if (mine !== seq) return
		online.value = results
		onlineError.value = ''
		searchedFor.value = text.toLowerCase()
	} catch (e) {
		if (mine !== seq || axios.isCancel(e)) return
		online.value = []
		onlineError.value = errorMessage(e)
		searchedFor.value = ''
	} finally {
		if (mine === seq) onlineLoading.value = false
	}
}

watch(
	() => props.modelValue,
	(value) => {
		active.value = -1
		stopSearch()

		const text = value.trim()
		if (!props.remote || text.length < 2) {
			online.value = []
			onlineLoading.value = false
			onlineError.value = ''
			searchedFor.value = ''
			return
		}

		onlineLoading.value = true
		timer = setTimeout(() => runSearch(text), 350)
	}
)

onBeforeUnmount(stopSearch)

// a title you already have is shown once (as your own title), not again as an online result
const onlineRows = computed(() => {
	const own = new Set(props.options.map((o) => o.label.trim().toLowerCase()))
	return online.value.filter((r) => !own.has(r.title.trim().toLowerCase()))
})

const noOnlineMatches = computed(
	() =>
		!!props.remote &&
		!onlineLoading.value &&
		!onlineError.value &&
		searchedFor.value === props.modelValue.trim().toLowerCase() &&
		!onlineRows.value.length
)

// ---------- all selectable rows, in the order they are shown ----------
type Row = { kind: 'own'; item: Suggestion } | { kind: 'online'; item: DiscoverResult } | { kind: 'create' }

const canCreate = computed(
	() => !!props.createLabel && query.value.length >= 2 && !props.options.some((o) => o.label.toLowerCase() === query.value)
)

const rows = computed<Row[]>(() => [
	...matches.value.map((item) => ({kind: 'own', item}) as Row),
	...onlineRows.value.map((item) => ({kind: 'online', item}) as Row),
	...(canCreate.value ? [{kind: 'create'} as Row] : [])
])

const hasStatus = computed(() => !!props.remote && query.value.length >= 2 && (onlineLoading.value || !!onlineError.value || noOnlineMatches.value))
const visible = computed(() => open.value && (rows.value.length > 0 || hasStatus.value))

const parts = (label: string) => {
	const i = label.toLowerCase().indexOf(query.value)
	if (i < 0 || !query.value) return {before: label, hit: '', after: ''}
	return {before: label.slice(0, i), hit: label.slice(i, i + query.value.length), after: label.slice(i + query.value.length)}
}

// pictures that failed to load show the first letter instead
const broken = reactive(new Set<string>())

const choose = (index: number) => {
	const row = rows.value[index]
	if (!row) return

	if (row.kind === 'own') {
		emit('update:modelValue', row.item.label)
		emit('pick', row.item.label)
	} else if (row.kind === 'online') {
		emit('pickRemote', row.item)
	} else {
		emit('create', props.modelValue.trim())
	}
	open.value = false
	active.value = -1
}

const onKey = (e: KeyboardEvent) => {
	const count = rows.value.length
	if (e.key === 'ArrowDown') {
		e.preventDefault()
		open.value = true
		if (count) active.value = (active.value + 1) % count
	} else if (e.key === 'ArrowUp') {
		e.preventDefault()
		if (count) active.value = (active.value - 1 + count) % count
	} else if (e.key === 'Enter' && visible.value && active.value >= 0) {
		e.preventDefault()
		choose(active.value)
	} else if (e.key === 'Escape') {
		open.value = false
	}
}

const clear = () => {
	emit('update:modelValue', '')
	open.value = false
}

const heading = (i: number) => {
	if (!props.remote) return ''
	const row = rows.value[i]
	const before = rows.value[i - 1]
	if (row.kind === 'create' || (before && before.kind === row.kind)) return ''
	return row.kind === 'own' ? 'In your tracker' : 'Add from the web'
}
</script>

<template>
	<div class="relative w-full sm:max-w-sm">
		<svg viewBox="0 0 24 24" class="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40"
			 fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">
			<circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
		</svg>

		<input :value="modelValue" type="text" autocomplete="off" spellcheck="false" :placeholder="placeholder"
			   role="combobox" aria-autocomplete="list" :aria-expanded="visible" :aria-controls="uid"
			   :aria-activedescendant="active >= 0 ? `${uid}-${active}` : undefined"
			   class="field !rounded-full !pl-11 !pr-10"
			   @input="(e) => { emit('update:modelValue', (e.target as HTMLInputElement).value); open = true }"
			   @focus="open = true" @blur="open = false" @keydown="onKey" />

		<button v-if="modelValue" type="button" aria-label="Clear search" @mousedown.prevent @click="clear"
				class="absolute right-3 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-full text-lg leading-none text-white/50 transition hover:bg-white/10 hover:text-white">
			&times;
		</button>

		<Transition name="modal">
			<ul v-if="visible" :id="uid" role="listbox"
				class="panel !bg-raised absolute left-0 right-0 top-full z-30 mt-2 max-h-[70vh] overflow-y-auto p-1.5 shadow-2xl">
				<template v-for="(row, i) in rows" :key="`${row.kind}-${row.kind === 'own' ? row.item.label : row.kind === 'online' ? row.item.title + row.item.year : 'new'}`">
					<li v-if="heading(i)" role="presentation"
						class="px-3 pb-1 pt-2 text-[10px] font-semibold uppercase tracking-[.18em] text-white/40">
						{{ heading(i) }}
					</li>

					<!-- a title you already have -->
					<li v-if="row.kind === 'own'" :id="`${uid}-${i}`" role="option" :aria-selected="active === i"
						@mousedown.prevent @click="choose(i)" @mousemove="active = i"
						class="flex cursor-pointer items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-sm transition"
						:class="active === i ? 'bg-white/10' : ''">
						<span class="truncate">
							{{ parts(row.item.label).before }}<mark class="rounded bg-accent/25 px-0.5 text-accent">{{ parts(row.item.label).hit }}</mark>{{ parts(row.item.label).after }}
						</span>
						<span v-if="row.item.hint" class="shrink-0 text-[10px] font-semibold uppercase tracking-wider text-white/40">{{ row.item.hint }}</span>
					</li>

					<!-- a suggestion from TMDB / MyAnimeList, with its poster -->
					<li v-else-if="row.kind === 'online'" :id="`${uid}-${i}`" role="option" :aria-selected="active === i"
						@mousedown.prevent @click="choose(i)" @mousemove="active = i"
						class="flex cursor-pointer items-center gap-3 rounded-xl px-2 py-2 text-sm transition"
						:class="active === i ? 'bg-white/10' : ''">
						<span class="flex h-[54px] w-9 shrink-0 items-center justify-center overflow-hidden rounded-md bg-white/10">
							<img v-if="row.item.poster_url && !broken.has(row.item.poster_url)" :src="row.item.poster_url" alt=""
								 loading="lazy" referrerpolicy="no-referrer" class="h-full w-full object-cover"
								 @error="broken.add(row.item.poster_url)" />
							<span v-else class="text-sm font-bold text-white/40" aria-hidden="true">{{ (row.item.title[0] ?? '?').toUpperCase() }}</span>
						</span>
						<span class="min-w-0 flex-1">
							<span class="block truncate font-medium">
								{{ parts(row.item.title).before }}<mark class="rounded bg-accent/25 px-0.5 text-accent">{{ parts(row.item.title).hit }}</mark>{{ parts(row.item.title).after }}
							</span>
							<span class="block truncate text-xs text-white/45">
								{{ [row.item.year, row.item.source].filter(Boolean).join(' · ') }}
							</span>
						</span>
						<span class="shrink-0 rounded-full border border-accent/40 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-accent">Add</span>
					</li>

					<!-- type something that is not found anywhere: add it by hand -->
					<li v-else :id="`${uid}-${i}`" role="option" :aria-selected="active === i"
						@mousedown.prevent @click="choose(i)" @mousemove="active = i"
						class="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium text-accent transition"
						:class="[active === i ? 'bg-white/10' : '', i ? 'mt-1 border-t border-white/10 rounded-t-none' : '']">
						<span aria-hidden="true">+</span>
						<span class="truncate">Add &ldquo;{{ modelValue.trim() }}&rdquo; as new {{ createLabel }}</span>
					</li>
				</template>

				<li v-if="onlineLoading" role="presentation" class="px-3 py-2.5 text-xs text-white/50">Searching online...</li>
				<li v-else-if="onlineError" role="presentation" class="px-3 py-2.5 text-xs leading-relaxed text-red-300">
					Online search is not available: {{ onlineError }}
				</li>
				<li v-else-if="noOnlineMatches" role="presentation" class="px-3 py-2.5 text-xs text-white/50">No online matches.</li>
			</ul>
		</Transition>
	</div>
</template>
