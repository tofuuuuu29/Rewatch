import type {MediaConfig, WatchStatus} from '@/types/index.ts'

export const site = {
	name: 'Rewatch',

	// one entry per Django app; the field names must match the models in server/
	media: [
		{key: 'movies', label: 'Movies', singular: 'Movie', endpoint: '/movies/', nameField: 'movie_name', hasProgress: false},
		{key: 'anime', label: 'Anime', singular: 'Anime', endpoint: '/anime/', nameField: 'anime_name', hasProgress: false},
		{key: 'kdrama', label: 'K-Drama', singular: 'K-Drama', endpoint: '/kdrama/', nameField: 'kdrama_name', hasProgress: false},
		{key: 'tvseries', label: 'TV Series', singular: 'TV Series', endpoint: '/tvseries/', nameField: 'tv_series', hasProgress: false}
	] as MediaConfig[],

	// the four statuses of the watch list (keys match the Django model)
	statuses: [
		{key: 'watching', label: 'Watching', badge: 'bg-accent text-accent-ink'},
		{key: 'completed', label: 'Completed', badge: 'bg-green-400 text-green-950'},
		{key: 'plan_to_watch', label: 'Plan to watch', badge: 'bg-black/60 text-white'},
		{key: 'dropped', label: 'Dropped', badge: 'bg-red-400 text-red-950'}
	] as { key: WatchStatus; label: string; badge: string }[]
}

export const statusLabel = (key: string) => site.statuses.find((s) => s.key === key)?.label ?? key
