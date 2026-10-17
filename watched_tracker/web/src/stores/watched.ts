import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import api from '@/axiosInstance.ts'
import {errorMessage} from '@/utils/errors.ts'
import type {MediaKey, WatchEntry, WatchPayload, WatchStatus} from '@/types/index.ts'

export const useWatchedStore = defineStore('watched', () => {
	const entries = ref<WatchEntry[]>([])
	const loading = ref(false)
	const error = ref('')

	// "anime:12" for every title that is already on my list
	const listed = computed(() => new Set(entries.value.map((e) => `${e.media?.category}:${e.media?.id}`)))
	const isListed = (category: MediaKey, titleId: number) => listed.value.has(`${category}:${titleId}`)

	// GET /api/watched/
	async function fetchAll() {
		loading.value = true
		error.value = ''
		try {
			const {data} = await api.get<WatchEntry[]>('/watched/')
			entries.value = data
		} catch (e) {
			error.value = errorMessage(e)
		} finally {
			loading.value = false
		}
	}

	// POST /api/watched/
	async function add(category: MediaKey, titleId: number, payload: WatchPayload) {
		const {data} = await api.post<WatchEntry>('/watched/', {category, title_id: titleId, ...payload})
		entries.value.unshift(data)
	}

	// PUT /api/watched/<id>/
	async function update(id: number, payload: WatchPayload) {
		const {data} = await api.put<WatchEntry>(`/watched/${id}/`, payload)
		entries.value = entries.value.map((e) => (e.id === id ? data : e))
	}

	// PATCH /api/watched/<id>/  (only the status, used by the dropdown in the table)
	async function setStatus(id: number, status: WatchStatus) {
		const {data} = await api.patch<WatchEntry>(`/watched/${id}/`, {status})
		entries.value = entries.value.map((e) => (e.id === id ? data : e))
	}

	// DELETE /api/watched/<id>/
	async function remove(id: number) {
		await api.delete(`/watched/${id}/`)
		entries.value = entries.value.filter((e) => e.id !== id)
	}

	function clear() {
		entries.value = []
	}

	return {entries, loading, error, isListed, fetchAll, add, update, setStatus, remove, clear}
})
