import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import api, {ACCESS_KEY, REFRESH_KEY} from '@/axiosInstance.ts'
import {useWatchedStore} from '@/stores/watched.ts'
import type {RegisterPayload, Role, User} from '@/types/index.ts'

export const useAuthStore = defineStore('auth', () => {
	const accessToken = ref<string | null>(null)
	const refreshToken = ref<string | null>(null)
	const user = ref<User | null>(null)
	const role = ref<Role | null>(null)

	// only users whose role is named "Admin" can add / edit / delete (same rule as the Django API)
	const isAdmin = computed(() => role.value?.name.toLowerCase() === 'admin')

	function loadTokens() {
		accessToken.value = localStorage.getItem(ACCESS_KEY)
		refreshToken.value = localStorage.getItem(REFRESH_KEY)
	}

	// the login endpoint only returns tokens, so read the user id from the token itself
	function userIdFromToken(token: string): number | null {
		try {
			const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
			return JSON.parse(atob(payload)).user_id ?? null
		} catch {
			return null
		}
	}

	async function loadProfile() {
		loadTokens()
		if (!accessToken.value) return

		const id = userIdFromToken(accessToken.value)
		if (id === null) return

		const {data} = await api.get<User>(`/users/${id}/`)
		user.value = data

		if (data.role) {
			const res = await api.get<Role>(`/roles/${data.role}/`)
			role.value = res.data
		} else {
			role.value = null
		}
	}

	async function login(username: string, password: string) {
		const {data} = await api.post('/login/', {username, password})
		localStorage.setItem(ACCESS_KEY, data.access)
		localStorage.setItem(REFRESH_KEY, data.refresh)
		loadTokens()

		try {
			await loadProfile()
		} catch {
			// logged in, but the profile could not be loaded; the dashboard still works read-only
		}
	}

	async function register(payload: RegisterPayload) {
		await api.post('/users/', payload)
	}

	function logout() {
		localStorage.removeItem(ACCESS_KEY)
		localStorage.removeItem(REFRESH_KEY)
		accessToken.value = null
		refreshToken.value = null
		user.value = null
		role.value = null
		useWatchedStore().clear()
	}

	return {accessToken, refreshToken, user, role, isAdmin, loadTokens, loadProfile, login, register, logout}
})
