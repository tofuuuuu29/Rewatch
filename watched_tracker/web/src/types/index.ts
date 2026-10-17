export interface Role {
	id: number
	name: string
}

export interface User {
	id: number
	first_name: string
	last_name: string
	username: string
	email: string
	gender: string
	role: number | null
}

export interface RegisterPayload {
	first_name: string
	last_name: string
	username: string
	email: string
	gender: string
	password: string
}

export type MediaKey = 'movies' | 'anime' | 'kdrama' | 'tvseries'

export interface MediaConfig {
	key: MediaKey
	label: string
	singular: string
	endpoint: string // matches the Django route, e.g. /api/movies/
	nameField: string // name of the title column in the Django model
	hasProgress: boolean // true if the model has season + episode
}

// one row from any media table (movie, anime, kdrama, tv series)
export interface MediaItem {
	id: number
	season?: number | null
	episode?: number | null
	poster_url?: string // picture of the title, filled in when it was picked from the online search

	[field: string]: string | number | null | undefined
}

// ----- watched list (one user's record of one title) -----
export type WatchStatus = 'watching' | 'completed' | 'plan_to_watch' | 'dropped'

export interface WatchEntry {
	id: number
	username: string
	media: { category: MediaKey; id: number; title: string; poster_url?: string } | null
	status: WatchStatus
	rating: number | null
	season: number | null
	episode: number | null
	notes: string
	date_started: string | null
	date_finished: string | null
	created_at: string
	updated_at: string
}

// what the form sends (the title itself is sent separately when adding)
export interface WatchPayload {
	status: WatchStatus
	rating: number | null
	season: number | null
	episode: number | null
	notes: string
	date_started: string | null
	date_finished: string | null
}

// one suggestion from GET /api/discover/ (TMDB for movies, series and K-dramas, MyAnimeList for anime)
export interface DiscoverResult {
	title: string
	year: string
	poster_url: string
	overview: string
	source: string
}
