import axios from 'axios'

export const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api'
export const ACCESS_KEY = 'wt_access'
export const REFRESH_KEY = 'wt_refresh'

const api = axios.create({baseURL: API_URL})

// send the access token with every request
api.interceptors.request.use((config) => {
	const token = localStorage.getItem(ACCESS_KEY)
	if (token) config.headers.Authorization = `Bearer ${token}`
	return config
})

// if the access token expired (401), get a new one with the refresh token and retry once
let refreshing: Promise<string> | null = null

api.interceptors.response.use(
	(response) => response,
	async (error) => {
		const original = error.config
		const isAuthCall = /\/(login|token\/refresh)\//.test(original?.url ?? '')

		if (error.response?.status === 401 && original && !original._retry && !isAuthCall) {
			const refresh = localStorage.getItem(REFRESH_KEY)

			if (refresh) {
				original._retry = true
				try {
					refreshing ??= axios
						.post(`${API_URL}/token/refresh/`, {refresh})
						.then((res) => {
							localStorage.setItem(ACCESS_KEY, res.data.access)
							return res.data.access as string
						})
						.finally(() => {
							refreshing = null
						})

					const access = await refreshing
					original.headers.Authorization = `Bearer ${access}`
					return api(original)
				} catch {
					// refresh token is also expired -> fall through to logout
				}
			}

			localStorage.removeItem(ACCESS_KEY)
			localStorage.removeItem(REFRESH_KEY)
			if (window.location.pathname !== '/login') window.location.href = '/login'
		}

		return Promise.reject(error)
	}
)

export default api
