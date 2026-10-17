import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/axiosInstance.ts'
import {errorMessage} from '@/utils/errors.ts'
import type {TypePayload, TypeRow} from '@/types/index.ts'

export const useTypeStore = defineStore('types', () => {
	const items = ref<TypeRow[]>([])
	const loading = ref(false)
	const error = ref('')

	// GET /api/type/
	async function fetchAll() {
		loading.value = true
		error.value = ''
		try {
			const {data} = await api.get<TypeRow[]>('/type/')
			items.value = data
		} catch (e) {
			error.value = errorMessage(e)
		} finally {
			loading.value = false
		}
	}

	// POST /api/type/
	async function create(payload: TypePayload) {
		const {data} = await api.post<TypeRow>('/type/', payload)
		items.value.push(data)
	}

	// PUT /api/type/<id>/  (always send all four fields, the API needs exactly one to be set)
	async function update(id: number, payload: TypePayload) {
		const {data} = await api.put<TypeRow>(`/type/${id}/`, payload)
		items.value = items.value.map((row) => (row.id === id ? data : row))
	}

	// DELETE /api/type/<id>/
	async function remove(id: number) {
		await api.delete(`/type/${id}/`)
		items.value = items.value.filter((row) => row.id !== id)
	}

	return {items, loading, error, fetchAll, create, update, remove}
})
