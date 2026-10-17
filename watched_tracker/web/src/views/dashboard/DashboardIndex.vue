<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import MediaList from './components/MediaList.vue'
import MediaFormModal from './components/MediaFormModal.vue'
import MediaIcon from './components/MediaIcon.vue'
import MyList from './components/MyList.vue'
import SearchBox from '@/components/SearchBox.vue'
import UsersList from './components/UsersList.vue'
import WatchFormModal from './components/WatchFormModal.vue'
import api from '@/axiosInstance.ts'
import {site} from '@/config/site.ts'
import {useAuthStore} from '@/stores/auth.ts'
import {useMediaStore} from '@/stores/media.ts'
import {useWatchedStore} from '@/stores/watched.ts'
import {errorMessage} from '@/utils/errors.ts'
import type {DiscoverResult, MediaConfig, MediaItem, WatchEntry, WatchPayload} from '@/types/index.ts'

const auth = useAuthStore()
const media = useMediaStore()
const watched = useWatchedStore()

// tabs: My List first, then every media type, then Users (admins only)
const tab = ref<string>('mylist')
const search = ref('')

const tabs = computed(() => [
	{key: 'mylist', label: 'My List'},
	...site.media.map((m) => ({key: m.key as string, label: m.label})),
	...(auth.isAdmin ? [{key: 'users', label: 'Users'}] : [])
])

// icon colour of each tab while it is not selected
const tabIcon: Record<string, string> = {
	mylist: 'text-white/70',
	movies: 'text-amber-400',
	anime: 'text-sky-400',
	kdrama: 'text-pink-500',
	tvseries: 'text-fuchsia-400'
}

// the four numbers above My List
const statCards = computed(() => {
	const entries = watched.entries
	const rated = entries.filter((e) => typeof e.rating === 'number')
	const average = rated.length ? (rated.reduce((sum, e) => sum + (e.rating as number), 0) / rated.length).toFixed(1) : '–'

	return [
		{
			label: 'Total', value: String(entries.length), kind: 'movies',
			box: 'border-amber-400/25 from-amber-400/15', icon: 'text-amber-400', ghost: 'text-amber-400/10'
		},
		{
			label: 'Completed', value: String(entries.filter((e) => e.status === 'completed').length), kind: 'check',
			box: 'border-violet-400/25 from-violet-500/20', icon: 'text-violet-300', ghost: 'text-violet-400/10'
		},
		{
			label: 'Watching', value: String(entries.filter((e) => e.status === 'watching').length), kind: 'eye',
			box: 'border-pink-400/25 from-pink-500/20', icon: 'text-pink-300', ghost: 'text-pink-400/10'
		},
		{
			label: 'Avg rating', value: average, kind: 'star',
			box: 'border-teal-400/25 from-teal-400/15', icon: 'text-teal-300', ghost: 'text-teal-400/10'
		}
	]
})

// null while My List or Users is open
const cfg = computed(() => site.media.find((m) => m.key === tab.value) ?? null)

const visible = computed(() => {
	const c = cfg.value
	if (!c) return []
	const q = search.value.trim().toLowerCase()
	const list = media.items[c.key]
	return q ? list.filter((i) => String(i[c.nameField] ?? '').toLowerCase().includes(q)) : list
})

// titles of the open tab, offered while typing in the search box
const suggestions = computed(() => {
	const c = cfg.value
	return c ? media.items[c.key].map((i) => ({label: String(i[c.nameField] ?? '')})).filter((o) => o.label) : []
})

const countOf = (key: string) => {
	if (key === 'mylist') return watched.entries.length
	const c = site.media.find((m) => m.key === key)
	return c ? media.items[c.key].length : null
}

const switchTab = (key: string, e?: Event) => {
	tab.value = key
	search.value = ''
	actionError.value = ''
	notice.value = ''

	// on a phone the tab strip scrolls sideways: bring the tapped tab into view
	;(e?.currentTarget as HTMLElement | null)?.scrollIntoView?.({inline: 'center', block: 'nearest', behavior: 'smooth'})
}

onMounted(() => {
	media.fetchAll()
	watched.fetchAll()
})

const actionError = ref('')
const notice = ref('')

// ================= titles (movies, anime, ...) =================
const showTitleForm = ref(false)
const editingTitle = ref<MediaItem | null>(null)
const savingTitle = ref(false)
const titleError = ref('')

const prefillName = ref('')

// "Add 'xyz' as new Movie" from the search box: open the form with the name filled in
const openAddTitleNamed = (name: string) => {
	openAddTitle()
	prefillName.value = name
}

const openAddTitle = () => {
	prefillName.value = ''
	editingTitle.value = null
	titleError.value = ''
	showTitleForm.value = true
}

// GET /api/discover/: searches TMDB (movies, series, K-dramas) or AniList (anime) for the open tab
const searchOnline = async (q: string, signal: AbortSignal) => {
	const c = cfg.value
	if (!c) return []
	const {data} = await api.get<DiscoverResult[]>('/discover/', {params: {category: c.key, q}, signal})
	return data
}

// a title picked from the online suggestions: save it with its poster, then open the My List form
const addFromWeb = async (result: DiscoverResult) => {
	const c = cfg.value
	if (!c) return
	search.value = ''
	actionError.value = ''
	notice.value = ''

	try {
		const wanted = result.title.trim().toLowerCase()
		let item = media.items[c.key].find((i) => String(i[c.nameField] ?? '').trim().toLowerCase() === wanted)

		if (!item) {
			item = await media.create(c, {[c.nameField]: result.title, poster_url: result.poster_url})
		} else if (!item.poster_url && result.poster_url) {
			// you already had this title without a picture: give it one
			item = await media.update(c, item.id, {[c.nameField]: String(item[c.nameField]), poster_url: result.poster_url})
		}

		if (watched.isListed(c.key, item.id)) {
			notice.value = `"${result.title}" is already on your list.`
			return
		}
		openTrack(item)
	} catch (e) {
		actionError.value = errorMessage(e)
	}
}

const openEditTitle = (item: MediaItem) => {
	editingTitle.value = item
	titleError.value = ''
	showTitleForm.value = true
}

const saveTitle = async (payload: Partial<MediaItem>) => {
	const c = cfg.value
	if (!c) return
	savingTitle.value = true
	titleError.value = ''
	try {
		if (editingTitle.value) await media.update(c, editingTitle.value.id, payload)
		else await media.create(c, payload)
		showTitleForm.value = false
	} catch (e) {
		titleError.value = errorMessage(e)
	} finally {
		savingTitle.value = false
	}
}

const removeTitle = async (item: MediaItem) => {
	const c = cfg.value
	if (!c) return
	if (!window.confirm(`Delete "${item[c.nameField]}" for everyone? It is removed from all lists.`)) return
	actionError.value = ''
	try {
		await media.remove(c, item.id)
		await watched.fetchAll() // entries for this title are gone too
	} catch (e) {
		actionError.value = errorMessage(e)
	}
}

// ================= my list =================
const showWatchForm = ref(false)
const watchEntry = ref<WatchEntry | null>(null) // set when editing
const watchTarget = ref<{ cfg: MediaConfig; item: MediaItem } | null>(null) // set when adding
const savingWatch = ref(false)
const watchError = ref('')

const watchTitle = computed(() => {
	if (watchEntry.value) return watchEntry.value.media?.title ?? 'Entry'
	if (watchTarget.value) return String(watchTarget.value.item[watchTarget.value.cfg.nameField])
	return ''
})

const openTrack = (item: MediaItem) => {
	if (!cfg.value) return
	watchEntry.value = null
	watchTarget.value = {cfg: cfg.value, item}
	watchError.value = ''
	showWatchForm.value = true
}

const openEditEntry = (entry: WatchEntry) => {
	watchTarget.value = null
	watchEntry.value = entry
	watchError.value = ''
	showWatchForm.value = true
}

const saveWatch = async (payload: WatchPayload) => {
	savingWatch.value = true
	watchError.value = ''
	try {
		if (watchEntry.value) await watched.update(watchEntry.value.id, payload)
		else if (watchTarget.value) await watched.add(watchTarget.value.cfg.key, watchTarget.value.item.id, payload)
		showWatchForm.value = false
	} catch (e) {
		watchError.value = errorMessage(e)
	} finally {
		savingWatch.value = false
	}
}

const removeEntry = async (entry: WatchEntry) => {
	if (!window.confirm(`Remove "${entry.media?.title}" from your list?`)) return
	actionError.value = ''
	try {
		await watched.remove(entry.id)
	} catch (e) {
		actionError.value = errorMessage(e)
	}
}

const changeStatus = async (entry: WatchEntry, status: WatchEntry['status']) => {
	actionError.value = ''
	try {
		await watched.setStatus(entry.id, status)
	} catch (e) {
		actionError.value = errorMessage(e)
	}
}
</script>

<template>
	<MainLayout>
		<div class="fade-up flex flex-col gap-1">
			<p class="eyebrow">Your watch list</p>
			<h1 class="display text-4xl font-semibold leading-tight sm:text-5xl">
				What have you <em class="text-accent">watched</em> lately?
			</h1>
			<p class="mt-2 max-w-xl text-sm text-white/60">
				Keep track of movies, anime, K-dramas and TV series.
				<span v-if="!auth.isAdmin" class="text-white/40">Anyone can add a title, only admins can rename or delete one.</span>
			</p>
		</div>

		<!-- tabs: scroll sideways on small screens -->
		<div class="-mx-4 mt-9 overflow-x-auto px-4 [scrollbar-width:none] sm:mx-0 sm:px-0 [&::-webkit-scrollbar]:hidden">
			<div class="inline-flex gap-1 rounded-full border border-white/10 bg-panel/80 p-1.5">
				<button v-for="t in tabs" :key="t.key" type="button" @click="switchTab(t.key, $event)"
						class="flex items-center gap-2 whitespace-nowrap rounded-full px-4 py-2.5 text-sm font-medium transition"
						:class="tab === t.key ? 'bg-accent text-accent-ink shadow' : 'text-white/70 hover:text-white'">
					<MediaIcon v-if="t.key !== 'users'" :kind="t.key"
							   class="h-4 w-4 shrink-0 transition-colors"
							   :class="[tab === t.key ? 'text-accent-ink' : tabIcon[t.key], t.key === 'kdrama' ? 'fill-current' : '']" />
					{{ t.label }}
					<span v-if="countOf(t.key) !== null" class="rounded-full px-1.5 text-xs"
						  :class="tab === t.key ? 'bg-black/15 text-accent-ink' : 'text-white/40'">{{ countOf(t.key) }}</span>
				</button>
			</div>
		</div>

		<!-- numbers (My List only): 2 across on phones, 4 across from tablet width -->
		<div v-if="tab === 'mylist'" class="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
			<div v-for="card in statCards" :key="card.label"
				 class="relative overflow-hidden rounded-2xl border bg-gradient-to-l to-transparent p-4 sm:p-5" :class="card.box">
				<MediaIcon :kind="card.kind" class="pointer-events-none absolute -bottom-3 -right-3 h-24 w-24 sm:h-28 sm:w-28" :class="card.ghost" />
				<MediaIcon :kind="card.kind" class="relative h-6 w-6" :class="card.icon" />
				<p class="display relative mt-3 text-3xl font-semibold leading-none sm:text-4xl">{{ card.value }}</p>
				<p class="relative mt-2 text-[11px] font-medium uppercase tracking-widest text-white/50">{{ card.label }}</p>
			</div>
		</div>

		<!-- search + add (title tabs only) -->
		<div v-if="cfg" class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
			<SearchBox v-model="search" :placeholder="`Search ${cfg.label.toLowerCase()}...`"
					   :options="suggestions" :create-label="cfg.singular" :remote="searchOnline"
					   @create="openAddTitleNamed" @pick-remote="addFromWeb" />

			<button type="button" @click="openAddTitle" class="btn-primary w-full sm:w-auto">+ Add {{ cfg.singular }}</button>
		</div>

		<p v-if="media.error || watched.error" class="alert-error mt-4">{{ media.error || watched.error }}</p>
		<p v-if="actionError" class="alert-error mt-4">{{ actionError }}</p>
		<p v-if="notice" class="mt-4 text-sm font-medium text-accent">{{ notice }}</p>

		<Transition name="tab" mode="out-in">
			<div :key="tab" class="mt-6">
				<MyList v-if="tab === 'mylist'" :entries="watched.entries" :loading="watched.loading"
						@edit="openEditEntry" @remove="removeEntry" @status="changeStatus" />

				<MediaList v-else-if="cfg" :cfg="cfg" :items="visible" :loading="media.loading" :can-edit="auth.isAdmin"
						   :is-listed="(id: number) => watched.isListed(cfg!.key, id)"
						   @track="openTrack" @edit="openEditTitle" @remove="removeTitle" />

				<UsersList v-else />
			</div>
		</Transition>

		<Transition name="modal">
			<MediaFormModal v-if="showTitleForm && cfg" :cfg="cfg" :item="editingTitle" :initial-name="prefillName" :saving="savingTitle"
							:error="titleError" @save="saveTitle" @close="showTitleForm = false" />
		</Transition>

		<Transition name="modal">
			<WatchFormModal v-if="showWatchForm" :title="watchTitle" :entry="watchEntry" :saving="savingWatch"
							:error="watchError" @save="saveWatch" @close="showWatchForm = false" />
		</Transition>
	</MainLayout>
</template>