import axios from 'axios'

// turns any error from the API into a readable message
export function errorMessage(e: unknown): string {
	if (axios.isAxiosError(e)) {
		if (!e.response) return 'Cannot reach the server. Is the Django server running?'

		const data = e.response.data
		if (data && typeof data === 'object') {
			if ('detail' in data) return String(data.detail)
			if ('message' in data) return String(data.message)

			const parts = Object.entries(data as Record<string, unknown>).map(([field, msg]) =>
				`${field}: ${Array.isArray(msg) ? msg.join(' ') : String(msg)}`
			)
			if (parts.length) return parts.join(' · ')
		}
		return `Request failed (${e.response.status})`
	}
	return e instanceof Error ? e.message : 'Something went wrong'
}
