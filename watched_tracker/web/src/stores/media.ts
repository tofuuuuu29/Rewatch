import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/axiosInstance.ts'
import {site} from '@/config/site.ts'
import {errorMessage} from '@/utils/errors.ts'
import type {MediaConfig, MediaItem, MediaKey} from '@/types/index.ts'

export const useMediaStore = defineStore('media', () => {
	const items = ref<Record<MediaKey, MediaItem[]>>({movies: [], anime: [], kdrama: [], tvseries: []})
	const loading = ref(false)
	const error = ref('')

	// GET /api/<type>/
	async function fetchOne(cfg: MediaConfig) {
		const {data} = await api.get<MediaItem[]>(cfg.endpoint)
		items.value[cfg.key] = data
	}

	async function fetchAll() {
		loading.value = true
		error.value = ''
		try {
			await Promise.all(site.media.map(fetchOne))
		} catch (e) {
			error.value = errorMessage(e)
		} finally {
			loading.value = false
		}
	}

	// POST /api/<type>/
	async function create(cfg: MediaConfig, payload: Partial<MediaItem>) {
		const {data} = await api.post<MediaItem>(cfg.endpoint, payload)
		items.value[cfg.key].push(data)
		return data
	}

	// PUT /api/<type>/<id>/
	async function update(cfg: MediaConfig, id: number, payload: Partial<MediaItem>) {
		const {data} = await api.put<MediaItem>(`${cfg.endpoint}${id}/`, payload)
		items.value[cfg.key] = items.value[cfg.key].map((item) => (item.id === id ? data : item))
		return data
	}

	// DELETE /api/<type>/<id>/
	async function remove(cfg: MediaConfig, id: number) {
		await api.delete(`${cfg.endpoint}${id}/`)
		items.value[cfg.key] = items.value[cfg.key].filter((item) => item.id !== id)
	}

	return {items, loading, error, fetchAll, create, update, remove}
})
